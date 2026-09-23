"""
Intelligence Service — Features 6, 7, 8, 9.

Feature 6: Advanced what-if simulation (reuses existing eta_model)
Feature 7: Model transparency / honesty panel
Feature 8: Fleet attribution audit card
Feature 9: Safety counterfactual (reruns deterministic safety engine)

No new ML models. No retraining. No fabricated statistics.
"""

from datetime import datetime
from backend.services import data_service
from backend.services.safety_service import evaluate_safety, PENALTIES
from ml.inference import (
    predict_eta_with_uncertainty,
    compare_eta_scenarios,
    weather_impact_engine,
    eta_model,
    anomaly_features,
    operator_baselines,
)


# ============================================================
# FEATURE 6 — ADVANCED WHAT-IF SIMULATION
# ============================================================

def run_what_if(machine_id: str, task_id: str | None = None) -> dict:
    """
    Extended scenario simulation panel.
    Reuses the existing eta_model — no new model created.
    All scenarios clearly labelled as 'Scenario simulation, not guaranteed prediction.'
    """
    task = None
    if task_id:
        task = data_service.get_task(task_id)
    if not task:
        task = data_service.get_current_task_for_machine(machine_id)
    if not task:
        return {"error": f"No active task found for {machine_id}"}

    base_row = {
        "Task Type":           task["task_type"],
        "Weather":             task["weather"],
        "Operator Skill":      task["operator_skill"],
        "Machine Age (yrs)":   task["machine_age_years"],
        "Estimated Time (min)": task["estimated_time_min"],
    }

    current_eta = predict_eta_with_uncertainty(base_row)

    # ── Weather scenarios (existing) ──────────────────────────
    weather_scenarios = {
        "If Sunny":  {"Weather": "Sunny"},
        "If Cloudy": {"Weather": "Cloudy"},
        "If Rainy":  {"Weather": "Rainy"},
        "If Windy":  {"Weather": "Windy"},
    }
    weather_what_if = compare_eta_scenarios(base_row, weather_scenarios)

    # ── Extended scenarios ────────────────────────────────────
    extended_scenarios = {}

    # Task delay: current delay continuing
    if current_eta["difference_min"] > 2:
        extended_scenarios["Delay continues at current pace"] = {}  # no change = same ETA

    # Skilled operator swap
    if task["operator_skill"] != "Expert":
        extended_scenarios["If Expert operator"] = {"Operator Skill": "Expert"}

    # Newer machine
    if task["machine_age_years"] > 3:
        extended_scenarios[f"If newer machine (3 yrs)"] = {"Machine Age (yrs)": 3}

    # Older machine (risk scenario)
    if task["machine_age_years"] < 7:
        extended_scenarios["If older machine (7 yrs)"] = {"Machine Age (yrs)": 7}

    extended_what_if = None
    if extended_scenarios:
        extended_what_if = compare_eta_scenarios(base_row, extended_scenarios)

    return {
        "machine_id":   machine_id,
        "task_id":      task["task_id"],
        "task_type":    task["task_type"],
        "current_eta":  current_eta,
        "weather_scenarios": weather_what_if,
        "extended_scenarios": extended_what_if,
        "disclaimer": (
            "Scenario simulation — not a guaranteed prediction. "
            "All scenarios use the existing ETA model with modified inputs. "
            "Results describe model output under hypothetical conditions."
        ),
        "generated_at": datetime.now().isoformat(),
    }


# ============================================================
# FEATURE 7 — MODEL TRANSPARENCY PANEL
# ============================================================

MODEL_TRANSPARENCY = {
    "eta_model": {
        "name":            "Task ETA Prediction",
        "algorithm":       "Linear Regression",
        "training_data":   "500 synthetic task records",
        "held_out_mae_min": 4.21,
        "uncertainty_method": "Empirical residual interval (held-out residuals)",
        "features_used": [
            "Task Type (one-hot encoded)",
            "Weather (one-hot encoded)",
            "Operator Skill (one-hot encoded)",
            "Machine Age (years)",
            "Estimated Time (minutes)",
        ],
        "version": "eta_lr_v1",
        "file":    "ml/models/eta_linear_regression_v1.joblib",
        "limitations": [
            "Trained on synthetic data only — not validated on real CAT telemetry.",
            "Linear model assumes additive feature contributions.",
            "Uncertainty interval is empirical, not Bayesian.",
        ],
    },
    "behavior_model": {
        "name":      "Behavioral Anomaly Detection",
        "algorithm": "Isolation Forest + Personalised Operator MAD Baseline",
        "training_data": "Synthetic machine telemetry records",
        "features_used": [
            "Fuel Used (L)",
            "Load Cycles",
            "Idling Time (min)",
            "Fuel per Load Cycle (derived)",
            "Idle Ratio (derived)",
        ],
        "version": "anomaly_if_v1 + operator_mad_v1",
        "files": [
            "ml/models/anomaly_isolation_forest_v1.joblib",
            "ml/models/operator_baseline_mad_v1.joblib",
        ],
        "limitations": [
            "Trained on synthetic data only.",
            "Anomaly threshold is fixed — not dynamically tuned per machine type.",
            "MAD baseline requires sufficient historical data per operator.",
        ],
    },
    "safety_engine": {
        "name":      "Safety Decision Engine",
        "algorithm": "Deterministic rule-based engine",
        "rules":     len(PENALTIES),
        "thresholds": {
            "NORMAL":   "85–100",
            "CAUTION":  "70–84",
            "CHECK":    "50–69",
            "ESCALATE": "< 50 or any CRITICAL rule",
        },
        "note": "Not ML-based. LLM never overrides safety decisions.",
        "limitations": [
            "Rules are manually defined — may not cover all real-world edge cases.",
            "Penalty weights are fixed and not trained from data.",
        ],
    },
    "weather_model": {
        "name":      "Weather Impact Lookup",
        "algorithm": "Pre-computed lookup table (avg delays by task type × weather)",
        "file":      "ml/models/weather_impact_v1.joblib",
        "limitations": [
            "Based on synthetic task/weather combinations.",
            "Does not account for real-time meteorological data.",
        ],
    },
    "general_disclaimer": (
        "This is a hackathon prototype. "
        "All models are trained on synthetic data and have NOT been validated on real CAT machinery telemetry. "
        "Results should not be used to make real operational safety decisions."
    ),
}


def get_model_transparency() -> dict:
    return {
        **MODEL_TRANSPARENCY,
        "retrieved_at": datetime.now().isoformat(),
    }


# ============================================================
# FEATURE 8 — FLEET ATTRIBUTION AUDIT
# ============================================================

def get_fleet_attribution_audit() -> dict:
    """
    Aggregated observed attribution statistics across all machines.
    Does NOT claim fairness certification.
    Clearly states 'Insufficient data' when sample is too small.
    """
    from backend.services.xai_service import explain_behavior
    from backend.services.safety_service import evaluate_safety

    machines = data_service.get_all_machines()
    MIN_MEANINGFUL = 5   # minimum machines for any statistical claim

    operator_flags:  dict[str, int] = {}
    context_flags:   int = 0
    machine_flags:   int = 0
    total_anomalies: int = 0
    total_safety:    int = 0
    by_operator:     dict[str, dict] = {}

    operator_task_weather: dict[str, list] = {}

    for m in machines:
        mid = m["machine_id"]
        oid = m.get("current_operator_id", "UNKNOWN")

        # Behavior
        try:
            beh = explain_behavior(mid)
            if beh.get("prediction") == "anomaly":
                total_anomalies += 1
                operator_flags[oid] = operator_flags.get(oid, 0) + 1

                # Check if context factors explain it
                ctx = beh.get("context_analysis", {})
                cf  = ctx.get("context_factors", [])
                explained_by_context = any(
                    c["alignment"] in ("consistent_with_deviation", "may_explain_deviation")
                    for c in cf
                )
                if explained_by_context:
                    context_flags += 1

                # Machine age context
                age = m.get("machine_age_years", 0)
                if age > 5:
                    machine_flags += 1
        except Exception:
            pass

        # Safety
        try:
            saf = evaluate_safety(mid)
            if saf.get("triggered_rules"):
                total_safety += 1

            # Per-operator summary
            if oid not in by_operator:
                by_operator[oid] = {
                    "operator_id":     oid,
                    "anomaly_count":   0,
                    "safety_count":    0,
                    "task_weather_exposure": [],
                }
            by_operator[oid]["anomaly_count"] += (1 if beh.get("prediction") == "anomaly" else 0)
            by_operator[oid]["safety_count"]  += (1 if saf.get("triggered_rules") else 0)
        except Exception:
            pass

        # Task/weather exposure
        task = data_service.get_current_task_for_machine(mid)
        if task and oid not in ("UNKNOWN", None):
            by_operator.setdefault(oid, {"operator_id": oid, "anomaly_count": 0, "safety_count": 0, "task_weather_exposure": []})
            by_operator[oid]["task_weather_exposure"].append({
                "task_type": task.get("task_type"),
                "weather":   task.get("weather"),
            })

    n = len(machines)

    # Distributions
    if n < MIN_MEANINGFUL:
        statistical_note = (
            f"Only {n} machines in the current dataset. "
            "Insufficient data for a meaningful fleet comparison. "
            "Attribution distribution shown for reference only."
        )
    else:
        statistical_note = (
            f"Based on {n} machines in the current demo dataset. "
            "Patterns reflect synthetic data and should not be generalised."
        )

    return {
        "audit_type": "FLEET_ATTRIBUTION_AUDIT",
        "period":     "Current shift (demo data)",
        "machine_count": n,
        "total_anomalies": total_anomalies,
        "total_safety_events": total_safety,
        "attribution_distribution": {
            "operator_flagged_count": sum(operator_flags.values()),
            "context_explained_count": context_flags,
            "machine_context_count": machine_flags,
            "note": (
                "An event is 'context-explained' when current task type, weather, or machine age "
                "is consistent with the observed deviation (not causal attribution)."
            ),
        },
        "by_operator": list(by_operator.values()),
        "operator_flag_counts": operator_flags,
        "statistical_note":  statistical_note,
        "disclaimer": (
            "This audit reports observed statistics from the demo dataset. "
            "It does NOT constitute a fairness certification. "
            "Do not label any operator as unfairly treated based on this synthetic sample."
        ),
        "generated_at": datetime.now().isoformat(),
    }


# ============================================================
# FEATURE 9 — SAFETY COUNTERFACTUAL
# ============================================================

def safety_counterfactual(machine_id: str) -> dict:
    """
    Reruns the EXISTING deterministic safety engine with modified inputs.
    Does NOT create a new ML model.
    Clearly labelled as 'Counterfactual scenario — does not override actual safety state.'
    """
    machine = data_service.get_machine(machine_id)
    if not machine:
        return {"error": f"Machine {machine_id} not found"}

    # Actual safety state
    actual = evaluate_safety(machine_id)

    # Build counterfactuals by changing one input at a time
    counterfactuals = []

    def _run_cf(label: str, override: dict) -> dict:
        """Run safety engine with one field overridden."""
        modified = {**machine, **override}
        # Temporarily patch data_service for the eval
        from backend.services import weather_service
        from ml.inference import predict_anomaly

        weather = weather_service.get_current_weather(machine_id)
        weather_risk_score = {
            "Sunny": 0, "Cloudy": 10, "Windy": 25, "Rainy": 45, "Stormy": 80
        }.get(weather["condition"], 0)
        weather_ctx = {"risk_score": weather_risk_score}

        machine_row = {
            "Machine ID":            modified["machine_id"],
            "Operator ID":           modified.get("current_operator_id", "UNKNOWN"),
            "Engine Hours":          modified["engine_hours"],
            "Fuel Used (L)":         modified["fuel_used_l"],
            "Load Cycles":           modified["load_cycles"],
            "Idling Time (min)":     modified["idling_time_min"],
            "Seatbelt Status":       modified["seatbelt_status"],
            "Safety Alert Triggered": modified["safety_alert_triggered"],
        }
        anomaly = predict_anomaly(machine_row)

        score = 100
        triggered = []
        has_critical = False

        for rule in PENALTIES:
            try:
                fired = rule["condition"](modified, weather_ctx, anomaly)
            except Exception:
                fired = False
            if fired:
                score -= rule["penalty"]
                triggered.append(rule["rule_id"])
                if rule["severity"] == "CRITICAL":
                    has_critical = True

        score = max(0, score)
        from backend.services.safety_service import THRESHOLDS
        if has_critical or score < THRESHOLDS["check_min"]:
            decision = "STOP / ESCALATE"
        elif score < THRESHOLDS["caution_min"]:
            decision = "SAFETY CHECK RECOMMENDED"
        elif score < THRESHOLDS["normal_min"]:
            decision = "CONTINUE WITH CAUTION"
        else:
            decision = "NORMAL"

        return {
            "label":            label,
            "override":         override,
            "safety_score":     score,
            "decision":         decision,
            "triggered_rules":  triggered,
            "score_delta":      score - actual["safety_score"],
        }

    # Counterfactual 1: seatbelt fastened (if currently unfastened)
    if machine["seatbelt_status"] == "Unfastened":
        counterfactuals.append(_run_cf(
            "If seatbelt were fastened",
            {"seatbelt_status": "Fastened"}
        ))

    # Counterfactual 2: no safety alert (if currently triggered)
    if machine["safety_alert_triggered"] == "Yes":
        counterfactuals.append(_run_cf(
            "If safety alert were resolved",
            {"safety_alert_triggered": "No"}
        ))

    # Counterfactual 3: both resolved
    if machine["seatbelt_status"] == "Unfastened" and machine["safety_alert_triggered"] == "Yes":
        counterfactuals.append(_run_cf(
            "If both seatbelt fastened and alert resolved",
            {"seatbelt_status": "Fastened", "safety_alert_triggered": "No"}
        ))

    # Counterfactual 4: idle reduced (if excessive)
    if machine.get("idling_time_min", 0) > 40:
        counterfactuals.append(_run_cf(
            "If idle time reduced to 20 min",
            {"idling_time_min": 20}
        ))

    if not counterfactuals:
        counterfactuals.append({
            "label":        "Current inputs are optimal",
            "override":     {},
            "safety_score": actual["safety_score"],
            "decision":     actual["decision"],
            "score_delta":  0,
        })

    return {
        "machine_id":     machine_id,
        "actual": {
            "safety_score": actual["safety_score"],
            "decision":     actual["decision"],
            "severity":     actual["severity"],
        },
        "counterfactuals": counterfactuals,
        "disclaimer": (
            "Counterfactual scenario — these scores show what the deterministic safety engine "
            "would produce if specific inputs were different. "
            "This does not override the actual safety state. "
            "Safety decisions remain with the deterministic rule-based engine."
        ),
        "generated_at": datetime.now().isoformat(),
    }
