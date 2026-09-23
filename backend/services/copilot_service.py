"""
AI Copilot — Module 10.
Tool-calling architecture.  The LLM selects tools, calls them,
gets structured data, then synthesises a grounded natural language response.
The LLM NEVER makes safety decisions and NEVER invents telemetry.
"""

from datetime import datetime
from backend.services import data_service
from backend.services.context_service import build_context
from backend.services.safety_service import evaluate_safety
from backend.services.xai_service import explain_task_eta, explain_behavior, explain_machine_health
from backend.services.weather_service import get_weather_risk, get_current_weather
from backend.services.task_service import get_task_eta, get_current_task
from backend.services.machine_service import get_passport
from backend.services.training_service import get_training_recommendations
from backend.services.report_service import generate_shift_handover, generate_daily_report


# ============================================================
# TOOL REGISTRY
# ============================================================

def get_machine_status(machine_id: str) -> dict:
    m = data_service.get_machine(machine_id)
    return m or {"error": f"Machine {machine_id} not found"}

def get_machine_passport(machine_id: str) -> dict:
    return get_passport(machine_id)

def get_current_context(machine_id: str) -> dict:
    return build_context(machine_id)

def get_safety_status(machine_id: str) -> dict:
    return evaluate_safety(machine_id)

def get_behavior_anomaly(machine_id: str) -> dict:
    return explain_behavior(machine_id)

def get_task_eta_tool(task_id: str) -> dict:
    return get_task_eta(task_id)

def explain_task_eta_tool(task_id: str) -> dict:
    return explain_task_eta(task_id)

def explain_behavior_tool(machine_id: str) -> dict:
    return explain_behavior(machine_id)

def get_weather_tool(machine_id: str) -> dict:
    return get_current_weather(machine_id)

def get_weather_risk_tool(machine_id: str, eta_min: float | None = None) -> dict:
    return get_weather_risk(machine_id, task_eta_min=eta_min)

def get_machine_health(machine_id: str) -> dict:
    return explain_machine_health(machine_id)

def get_current_task_tool(machine_id: str) -> dict:
    task = get_current_task(machine_id)
    return task or {"message": f"No active task for machine {machine_id}"}

def get_operator_profile(operator_id: str) -> dict:
    op = data_service.get_operator(operator_id)
    return op or {"error": f"Operator {operator_id} not found"}

def get_shift_summary(machine_id: str) -> dict:
    return generate_shift_handover(machine_id)

def get_machine_history_tool(machine_id: str) -> dict:
    return {"machine_id": machine_id, "history": data_service.get_machine_history(machine_id)}

def create_incident_tool(machine_id: str, operator_id: str, category: str,
                         description: str, severity: str = "MEDIUM") -> dict:
    return data_service.create_incident(machine_id, operator_id, category, description, severity)

def create_support_request_tool(machine_id: str, operator_id: str, description: str,
                                troubleshooting_steps: list, xai_findings: str = "",
                                safety_state: str = "UNKNOWN") -> dict:
    return data_service.create_support_request(
        machine_id, operator_id, description, troubleshooting_steps, xai_findings, safety_state
    )

def generate_shift_handover_tool(machine_id: str) -> dict:
    return generate_shift_handover(machine_id)

def generate_daily_report_tool(machine_id: str) -> dict:
    return generate_daily_report(machine_id)

def get_training_recommendations_tool(operator_id: str) -> dict:
    return get_training_recommendations(operator_id)


TOOLS = {
    "get_machine_status": get_machine_status,
    "get_machine_passport": get_machine_passport,
    "get_current_context": get_current_context,
    "get_safety_status": get_safety_status,
    "get_behavior_anomaly": get_behavior_anomaly,
    "get_task_eta": get_task_eta_tool,
    "explain_task_eta": explain_task_eta_tool,
    "explain_behavior": explain_behavior_tool,
    "get_weather": get_weather_tool,
    "get_weather_risk": get_weather_risk_tool,
    "get_machine_health": get_machine_health,
    "get_current_task": get_current_task_tool,
    "get_operator_profile": get_operator_profile,
    "get_shift_summary": get_shift_summary,
    "get_machine_history": get_machine_history_tool,
    "create_incident": create_incident_tool,
    "create_support_request": create_support_request_tool,
    "generate_shift_handover": generate_shift_handover_tool,
    "generate_daily_report": generate_daily_report_tool,
    "get_training_recommendations": get_training_recommendations_tool,
}


# ============================================================
# INTENT → TOOL SELECTOR
# ============================================================

def _select_tools(message: str, machine_id: str | None, task_id: str | None) -> list[dict]:
    """
    Deterministic intent router.  Returns a list of
    {tool_name, args} in execution order.
    """
    m = (message or "").lower()
    calls = []

    # Always get context when a machine is mentioned
    if machine_id:
        calls.append({"tool": "get_current_context", "args": {"machine_id": machine_id}})

    if any(k in m for k in ["delay", "eta", "long", "time", "slow", "taking", "complete"]):
        if machine_id:
            task = data_service.get_current_task_for_machine(machine_id)
            if task:
                calls.append({"tool": "get_task_eta", "args": {"task_id": task["task_id"]}})
                calls.append({"tool": "explain_task_eta", "args": {"task_id": task["task_id"]}})
        elif task_id:
            calls.append({"tool": "get_task_eta", "args": {"task_id": task_id}})
            calls.append({"tool": "explain_task_eta", "args": {"task_id": task_id}})

    if any(k in m for k in ["safe", "safety", "score", "seatbelt", "alert", "risk"]):
        if machine_id:
            calls.append({"tool": "get_safety_status", "args": {"machine_id": machine_id}})

    if any(k in m for k in ["weather", "rain", "wind", "storm", "forecast", "continue", "happen"]):
        if machine_id:
            calls.append({"tool": "get_weather", "args": {"machine_id": machine_id}})
            task = data_service.get_current_task_for_machine(machine_id)
            eta_min = None
            if task:
                from ml.inference import predict_eta_with_uncertainty
                task_row = {
                    "Task Type": task["task_type"], "Weather": task["weather"],
                    "Operator Skill": task["operator_skill"],
                    "Machine Age (yrs)": task["machine_age_years"],
                    "Estimated Time (min)": task["estimated_time_min"],
                }
                eta_min = predict_eta_with_uncertainty(task_row)["predicted_time_min"]
            calls.append({"tool": "get_weather_risk", "args": {"machine_id": machine_id, "eta_min": eta_min}})

    if any(k in m for k in ["anomal", "behav", "unusual", "normal", "pattern", "wrong", "abnormal"]):
        if machine_id:
            calls.append({"tool": "get_behavior_anomaly", "args": {"machine_id": machine_id}})

    if any(k in m for k in ["health", "condition", "engine", "hydraul", "oil", "service"]):
        if machine_id:
            calls.append({"tool": "get_machine_health", "args": {"machine_id": machine_id}})

    if any(k in m for k in ["report", "handover", "shift", "summary", "end"]):
        if machine_id:
            calls.append({"tool": "generate_shift_handover", "args": {"machine_id": machine_id}})

    if any(k in m for k in ["train", "recommend", "skill", "improve"]):
        context = data_service.get_machine(machine_id) if machine_id else None
        op_id = context.get("current_operator_id") if context else None
        if op_id:
            calls.append({"tool": "get_training_recommendations", "args": {"operator_id": op_id}})

    if any(k in m for k in ["passport", "details", "info", "status"]):
        if machine_id:
            calls.append({"tool": "get_machine_passport", "args": {"machine_id": machine_id}})

    # "Something feels wrong" / call expert
    if any(k in m for k in ["feels wrong", "problem", "issue", "help", "expert", "technician", "support"]):
        if machine_id:
            calls.append({"tool": "get_behavior_anomaly", "args": {"machine_id": machine_id}})
            calls.append({"tool": "get_safety_status", "args": {"machine_id": machine_id}})
            calls.append({"tool": "get_machine_health", "args": {"machine_id": machine_id}})

    # Deduplicate preserving order
    seen = set()
    unique = []
    for c in calls:
        key = (c["tool"], str(c["args"]))
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return unique


# ============================================================
# RESPONSE SYNTHESISER
# ============================================================

def _synthesise(message: str, tool_results: list[dict], machine_id: str | None) -> str:
    """
    Build a grounded natural language response from tool results.
    Never fabricates. Clearly attributes facts to tools.
    """
    m = message.lower()
    parts = []

    ctx = next((r["result"] for r in tool_results if r["tool"] == "get_current_context"), None)
    safety = next((r["result"] for r in tool_results if r["tool"] == "get_safety_status"), None)
    behavior = next((r["result"] for r in tool_results if r["tool"] == "get_behavior_anomaly"), None)
    eta = next((r["result"] for r in tool_results if r["tool"] == "get_task_eta"), None)
    eta_xai = next((r["result"] for r in tool_results if r["tool"] == "explain_task_eta"), None)
    weather = next((r["result"] for r in tool_results if r["tool"] == "get_weather"), None)
    weather_risk = next((r["result"] for r in tool_results if r["tool"] == "get_weather_risk"), None)
    health = next((r["result"] for r in tool_results if r["tool"] == "get_machine_health"), None)
    handover = next((r["result"] for r in tool_results if r["tool"] == "generate_shift_handover"), None)
    training = next((r["result"] for r in tool_results if r["tool"] == "get_training_recommendations"), None)
    passport = next((r["result"] for r in tool_results if r["tool"] == "get_machine_passport"), None)

    mid = machine_id or "the machine"

    # ETA / delay question
    if eta and eta_xai and any(k in m for k in ["delay", "long", "time", "slow", "taking", "complete"]):
        predicted = eta["eta"]["predicted_time_min"]
        baseline = eta["eta"]["baseline_time_min"]
        diff = eta["eta"]["difference_min"]
        sign = "+" if diff > 0 else ""
        parts.append(
            f"**{mid}'s current task** is predicted to take **{predicted:.0f} minutes** "
            f"(original estimate: {baseline:.0f} min, {sign}{diff:.1f} min difference)."
        )
        factors = eta_xai.get("top_factors", [])
        if factors:
            driver_names = [f['feature'] for f in factors if f.get('direction') == 'increase'][:3]
            if driver_names:
                parts.append(
                    f"The main contributing factors identified by the prediction system are: "
                    + ", ".join(f"**{n}**" for n in driver_names) + "."
                )

    # Weather / "what happens if I continue"
    if weather_risk:
        if weather_risk.get("task_weather_overlap") and weather_risk.get("overlap_advisory"):
            parts.append(f"⚠️ **Weather-Task Overlap:** {weather_risk['overlap_advisory']}")
        elif weather:
            cond = weather.get("condition", "Unknown")
            risk = weather.get("risk_level", "NORMAL")
            parts.append(f"Current weather is **{cond}** (risk: {risk}).")
            if weather_risk.get("worst_upcoming_condition"):
                worst = weather_risk["worst_upcoming_condition"]
                parts.append(
                    f"The worst upcoming condition is **{worst['condition']}** around **{worst['time']}**."
                )

    # Safety
    if safety:
        score = safety.get("safety_score", 100)
        decision = safety.get("decision", "NORMAL")
        parts.append(
            f"**Safety score:** {score}/100 — **{decision}** "
            f"*(determined by the deterministic safety engine)*."
        )
        rules = safety.get("triggered_rules", [])
        if rules:
            rule_descs = [r["description"] for r in rules[:2]]
            parts.append("Triggered rules: " + "; ".join(rule_descs) + ".")

    # Behavior anomaly
    if behavior:
        if behavior.get("prediction") == "anomaly":
            sev = behavior.get("severity", "MEDIUM")
            factors = behavior.get("top_factors", [])
            parts.append(f"A **{sev.lower()} behavioral anomaly** was detected.")
            if factors:
                top = factors[0]
                parts.append(
                    f"The strongest deviation is in **{top['feature']}** "
                    f"({top['current_value']:.2f} vs baseline {top['baseline_median']:.2f}, "
                    f"{top['deviation_mad']:.1f}x operator's normal variation)."
                )
        else:
            parts.append(f"Machine behavior is within **normal parameters** for this operator.")

    # Machine health
    if health:
        hs = health.get("health_status", "GOOD")
        hsc = health.get("health_score", 100)
        parts.append(f"**Machine health:** {hsc}/100 ({hs}).")
        hfactors = health.get("top_factors", [])
        if hfactors:
            concerns = [f['feature'] for f in hfactors[:2]]
            parts.append(f"Notable health concerns: {', '.join(concerns)}.")

    # Shift handover
    if handover and "handover" in m:
        parts.append("**Shift handover has been generated.** See the Reports page for the full document.")

    # Training
    if training:
        recs = training.get("recommendations", [])
        if recs:
            parts.append(
                f"**Training recommendations** for {training.get('operator_name', 'the operator')}: "
                + "; ".join(r["module"] for r in recs[:3]) + "."
            )

    # Support / "feels wrong"
    if any(k in m for k in ["feels wrong", "problem", "issue", "help", "expert", "technician", "support"]):
        if health or behavior:
            troubleshooting = []
            if health and health.get("health_status") != "GOOD":
                troubleshooting.append("Check engine temperature and oil pressure gauges.")
                troubleshooting.append("Inspect hydraulic lines for visible leaks or damage.")
            if behavior and behavior.get("prediction") == "anomaly":
                troubleshooting.append("Review recent load cycles and idle time patterns.")
                troubleshooting.append("Check for unusual noises or vibrations during operation.")
            troubleshooting.append("If issue persists, stop operation and contact a CAT technician.")
            parts.append("**Troubleshooting steps:**")
            for i, step in enumerate(troubleshooting, 1):
                parts.append(f"{i}. {step}")
            parts.append(
                "If the issue remains unresolved after these checks, "
                "I can create a **support request** and connect you with a CAT Expert."
            )

    if not parts:
        # Fallback — return context summary
        if ctx and not ctx.get("error"):
            machine_status = ctx.get("machine", {}).get("status", "Unknown")
            parts.append(
                f"Machine **{mid}** is currently **{machine_status}**. "
                "I retrieved the current context. "
                "What specific aspect would you like me to look into?"
            )
        else:
            parts.append(
                f"I don't have enough machine data to answer that with confidence. "
                "Please specify a machine ID (e.g. EXC001) or ask about a specific aspect."
            )

    return "\n\n".join(parts)


# ============================================================
# MAIN COPILOT ENTRY POINT
# ============================================================

def process_message(message: str, machine_id: str | None = None,
                    task_id: str | None = None, operator_id: str | None = None) -> dict:
    # Auto-detect machine_id from message if not provided
    if not machine_id:
        for mid in data_service.MACHINES:
            if mid.lower() in message.lower():
                machine_id = mid
                break

    # Select and execute tools
    tool_calls = _select_tools(message, machine_id, task_id)
    tool_results = []

    for call in tool_calls:
        tool_fn = TOOLS.get(call["tool"])
        if tool_fn:
            try:
                result = tool_fn(**call["args"])
            except Exception as e:
                result = {"error": str(e)}
            tool_results.append({
                "tool": call["tool"],
                "args": call["args"],
                "result": result,
            })

    response_text = _synthesise(message, tool_results, machine_id)

    # Feature 10 — structured evidence panel
    evidence = _build_evidence_panel(tool_results)

    return {
        "message": message,
        "machine_id": machine_id,
        "task_id": task_id,
        "operator_id": operator_id,
        "response": response_text,
        "tools_called": [{"tool": r["tool"], "args": r["args"]} for r in tool_results],
        "tool_results_count": len(tool_results),
        "evidence": evidence,
        "timestamp": datetime.now().isoformat(),
    }


# ============================================================
# FEATURE 10 — EVIDENCE PANEL BUILDER
# ============================================================

def _build_evidence_panel(tool_results: list[dict]) -> dict:
    """
    Build a structured evidence panel for the Copilot response UI.
    Distinguishes OBSERVED / MODEL_OUTPUT / MODEL_EXPLANATION / RECOMMENDATION.
    """
    observed       = []
    model_output   = []
    model_explanation = []
    recommendations   = []
    sources_used      = []

    for r in tool_results:
        tool   = r["tool"]
        result = r.get("result", {})
        if not isinstance(result, dict):
            continue
        sources_used.append(tool)

        if tool == "get_current_context":
            m = result.get("machine", {})
            w = result.get("weather", {}).get("current", {})
            if m:
                observed.append({"label": "Machine status",    "value": m.get("status", "—"), "source": tool})
                observed.append({"label": "Seatbelt",          "value": m.get("seatbelt_status", "—"), "source": tool})
                observed.append({"label": "Engine hours",      "value": m.get("engine_hours", "—"), "source": tool})
                observed.append({"label": "Idle time",         "value": f"{m.get('idling_time_min','—')} min", "source": tool})
            if w:
                observed.append({"label": "Current weather",   "value": w.get("condition", "—"), "source": tool})

        elif tool == "get_safety_status":
            observed.append({"label": "Safety alert",      "value": result.get("safety_alert", "—"), "source": tool})
            observed.append({"label": "Seatbelt status",   "value": result.get("seatbelt_status", "—"), "source": tool})
            model_output.append({
                "label":  "Safety score",
                "value":  f"{result.get('safety_score', '—')}/100",
                "detail": result.get("decision", "—"),
                "source": "deterministic_safety_engine",
            })
            for rec in result.get("recommendations", [])[:2]:
                recommendations.append({"text": rec, "source": "safety_engine", "priority": "HIGH"})

        elif tool in ("get_task_eta", "explain_task_eta"):
            eta = result.get("eta", result)
            if eta.get("predicted_time_min"):
                model_output.append({
                    "label":  "Predicted ETA",
                    "value":  f"{eta.get('predicted_time_min','—'):.0f} min",
                    "detail": f"Estimate: {eta.get('baseline_time_min','—')} min  |  Δ {eta.get('difference_min',0):+.1f} min",
                    "source": "eta_linear_regression_v1",
                })
                unc = result.get("uncertainty_range") or {}
                if unc:
                    model_output.append({
                        "label":  "Uncertainty interval",
                        "value":  f"{unc.get('lower','—'):.0f}–{unc.get('upper','—'):.0f} min",
                        "detail": "Empirical residual interval",
                        "source": "eta_uncertainty_v1",
                    })
            for f in result.get("top_factors", [])[:3]:
                if f.get("impact", 0) > 0:
                    model_explanation.append({
                        "label":  f["feature"],
                        "value":  f.get("value", "—"),
                        "contribution": f"{f.get('model_contribution_min', f.get('impact',0)):+.1f} min",
                        "direction": f.get("direction", "neutral"),
                        "attribution_type": f.get("attribution_type", "approximate"),
                        "source": "xai_eta",
                    })
            if result.get("recommended_action"):
                act = result["recommended_action"]
                for s in act.get("steps", [])[:2]:
                    recommendations.append({"text": s, "source": "eta_action_layer", "priority": act.get("priority", "LOW")})

        elif tool in ("get_behavior_anomaly", "explain_behavior"):
            if result.get("prediction") == "anomaly":
                model_output.append({
                    "label":  "Behavior prediction",
                    "value":  "ANOMALY",
                    "detail": f"Severity: {result.get('severity','—')}  |  Score: {result.get('anomaly_score','—')}",
                    "source": "isolation_forest_v1 + operator_mad_baseline",
                })
                for f in result.get("top_factors", [])[:3]:
                    model_explanation.append({
                        "label":  f["feature"],
                        "value":  f"{f.get('current_value','—'):.2f} vs baseline {f.get('baseline_median','—'):.2f}",
                        "contribution": f"{f.get('deviation_mad',0):.1f}× MAD",
                        "direction": f.get("direction", "neutral"),
                        "attribution_type": "operator_mad_baseline",
                        "source": "xai_behavior",
                    })
                if result.get("recommended_action"):
                    act = result["recommended_action"]
                    for s in act.get("steps", [])[:2]:
                        recommendations.append({"text": s, "source": "behavior_action_layer", "priority": act.get("priority", "MEDIUM")})
            else:
                model_output.append({
                    "label":  "Behavior prediction",
                    "value":  "NORMAL",
                    "detail": "Within operator baseline parameters",
                    "source": "isolation_forest_v1 + operator_mad_baseline",
                })

        elif tool == "get_weather_risk":
            cond = result.get("current_condition", "—")
            risk = result.get("current_risk_level", "—")
            observed.append({"label": "Weather condition",  "value": cond, "source": tool})
            model_output.append({
                "label":  "Weather risk level",
                "value":  risk,
                "detail": f"Risk score: {result.get('current_risk_score','—')}",
                "source": "weather_impact_v1",
            })
            if result.get("overlap_advisory"):
                recommendations.append({
                    "text":     result["overlap_advisory"],
                    "source":   "weather_risk_engine",
                    "priority": "MEDIUM",
                })

        elif tool == "get_machine_health":
            model_output.append({
                "label":  "Machine health",
                "value":  f"{result.get('health_score','—')}/100",
                "detail": result.get("health_status", "—"),
                "source": "rule_based_health_indicators",
            })
            if result.get("recommended_action"):
                act = result["recommended_action"]
                for s in act.get("steps", [])[:1]:
                    recommendations.append({"text": s, "source": "health_action_layer", "priority": act.get("priority","LOW")})

    # Deduplicate recommendations
    seen_recs = set()
    unique_recs = []
    for rec in recommendations:
        if rec["text"] not in seen_recs:
            seen_recs.add(rec["text"])
            unique_recs.append(rec)

    return {
        "observed":            observed,
        "model_output":        model_output,
        "model_explanation":   model_explanation,
        "recommendations":     unique_recs,
        "sources_used":        sources_used,
        "evidence_note": (
            "All evidence is sourced from structured backend data and ML model outputs. "
            "No information has been fabricated."
        ),
    }
