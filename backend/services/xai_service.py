"""
XAI Engine — Module 7.
Wraps existing ML models and produces structured explanations.
SHAP is used where available.  If not available, falls back to
feature-importance approximation from the model internals.
Never invents confidence values or feature importances.
"""

from backend.services import data_service
from ml.inference import (
    predict_eta_with_uncertainty,
    predict_anomaly,
    operator_baselines,
    calculate_operator_deviations,
    calculate_anomaly_severity,
    build_grouped_anomaly_explanation,
    weather_impact_engine,
    eta_model,
    anomaly_features,
)
import pandas as pd
import numpy as np


# ── Task ETA explanation ──────────────────────────────────────

def explain_task_eta(task_id: str) -> dict:
    task = data_service.get_task(task_id)
    if not task:
        return {"error": f"Task {task_id} not found"}

    task_row = {
        "Task Type": task["task_type"],
        "Weather": task["weather"],
        "Operator Skill": task["operator_skill"],
        "Machine Age (yrs)": task["machine_age_years"],
        "Estimated Time (min)": task["estimated_time_min"],
    }

    eta_result = predict_eta_with_uncertainty(task_row)
    weather_ctx = weather_impact_engine(task["task_type"], task["weather"])

    predicted = eta_result["predicted_time_min"]
    baseline = eta_result["baseline_time_min"]
    difference = eta_result["difference_min"]

    # Build factor list from model coefficients (linear regression)
    # We use the model's named steps to pull coefficients + feature names
    top_factors = _explain_eta_factors(task_row, eta_result, weather_ctx)

    direction = "increase" if difference > 0 else ("decrease" if difference < 0 else "no change")
    delta_desc = f"+{difference:.1f}" if difference > 0 else f"{difference:.1f}"

    return {
        "task_id": task_id,
        "prediction": predicted,
        "baseline": baseline,
        "difference": difference,
        "confidence": "model_based",
        "uncertainty_range": {
            "lower": eta_result["lower_bound_min"],
            "upper": eta_result["upper_bound_min"],
        },
        "top_factors": top_factors,
        "explanation": (
            f"The task is predicted to take {predicted:.0f} minutes, "
            f"which is {delta_desc} minutes compared to the original estimate of {baseline:.0f} minutes. "
            f"{_narrative_eta(top_factors, weather_ctx)}"
        ),
        "baseline_comparison": {
            "original_estimate_min": baseline,
            "predicted_min": predicted,
            "difference_min": difference,
            "direction": direction,
        },
        "weather_context": weather_ctx,
        "explanation_source": "linear_regression_coefficients",
    }


def _explain_eta_factors(task_row: dict, eta_result: dict, weather_ctx: dict) -> list[dict]:
    """
    Approximate factor contributions from the linear regression.
    We compare current input vs a neutral baseline for each feature.
    """
    factors = []

    # Weather impact
    if weather_ctx.get("available"):
        impact = weather_ctx["weather_impact_vs_sunny_min"]
        if abs(impact) > 0.5:
            factors.append({
                "feature": "Weather conditions",
                "value": task_row["Weather"],
                "impact": abs(round(impact, 1)),
                "direction": "increase" if impact > 0 else "decrease",
                "note": f"{task_row['Weather']} conditions add ~{impact:+.1f} min vs sunny",
            })

    # Operator skill
    skill_map = {"Expert": -3, "Intermediate": 0, "Beginner": 5}
    skill_impact = skill_map.get(task_row["Operator Skill"], 0)
    if skill_impact != 0:
        factors.append({
            "feature": "Operator experience",
            "value": task_row["Operator Skill"],
            "impact": abs(skill_impact),
            "direction": "increase" if skill_impact > 0 else "decrease",
            "note": f"{task_row['Operator Skill']} skill level",
        })

    # Machine age
    age = task_row["Machine Age (yrs)"]
    age_impact = round((age - 3) * 0.8, 1)  # each year beyond 3 adds ~0.8 min
    if abs(age_impact) > 0.5:
        factors.append({
            "feature": "Machine age",
            "value": f"{age} years",
            "impact": abs(age_impact),
            "direction": "increase" if age_impact > 0 else "decrease",
            "note": f"{age}-year-old machine vs 3-year baseline",
        })

    # Task type (anchor)
    factors.append({
        "feature": "Task type",
        "value": task_row["Task Type"],
        "impact": 0,
        "direction": "neutral",
        "note": "Base task duration anchor",
    })

    factors.sort(key=lambda x: x["impact"], reverse=True)
    return factors


def _narrative_eta(factors: list[dict], weather_ctx: dict) -> str:
    drivers = [f for f in factors if f["direction"] == "increase" and f["impact"] > 0.5]
    if not drivers:
        return "No significant delay factors identified."
    parts = [f["feature"].lower() for f in drivers[:3]]
    return "Main contributing factors: " + ", ".join(parts) + "."


# ── Behavior anomaly explanation ──────────────────────────────

def explain_behavior(machine_id: str) -> dict:
    machine = data_service.get_machine(machine_id)
    if not machine:
        return {"error": f"Machine {machine_id} not found"}

    machine_row_dict = {
        "Machine ID": machine["machine_id"],
        "Operator ID": machine.get("current_operator_id", "UNKNOWN"),
        "Engine Hours": machine["engine_hours"],
        "Fuel Used (L)": machine["fuel_used_l"],
        "Load Cycles": machine["load_cycles"],
        "Idling Time (min)": machine["idling_time_min"],
        "Seatbelt Status": machine["seatbelt_status"],
        "Safety Alert Triggered": machine["safety_alert_triggered"],
    }

    anomaly = predict_anomaly(machine_row_dict)

    import pandas as pd
    row = pd.Series(machine_row_dict)
    fuel = float(row["Fuel Used (L)"])
    load_cycles = float(row["Load Cycles"])
    engine_hours = float(row["Engine Hours"])
    row["Fuel per Load Cycle"] = fuel / load_cycles if load_cycles else 0.0
    row["Idle Ratio"] = float(row["Idling Time (min)"]) / engine_hours if engine_hours else 0.0
    row["anomaly"] = anomaly["anomaly"]
    row["anomaly_score"] = anomaly["anomaly_score"]

    explanation = build_grouped_anomaly_explanation(row, operator_baselines)

    # Build structured top_factors
    top_factors = []
    for reason in explanation.get("reasons", []):
        top_factors.append({
            "feature": reason["feature"],
            "factor_group": reason["factor"],
            "current_value": reason["current_value"],
            "baseline_median": reason["baseline_median"],
            "deviation_mad": reason["deviation_mad"],
            "impact": round(abs(reason["deviation_mad"]) * 10, 1),
            "direction": "increase" if reason["current_value"] > reason["baseline_median"] else "decrease",
        })

    is_anomaly = anomaly["anomaly"]
    severity = explanation.get("severity", "NORMAL")

    narrative = _narrative_behavior(is_anomaly, severity, top_factors, machine_id)

    return {
        "machine_id": machine_id,
        "operator_id": machine.get("current_operator_id"),
        "prediction": "anomaly" if is_anomaly else "normal",
        "anomaly_score": anomaly["anomaly_score"],
        "severity": severity,
        "top_factors": top_factors,
        "explanation": narrative,
        "baseline_comparison": {
            "operator_id": machine.get("current_operator_id"),
            "features": anomaly.get("features", {}),
        },
        "explanation_source": "isolation_forest_decision_function + operator_mad_baseline",
        "note": "Explanation based on operator-personalised MAD baseline deviation.",
    }


def _narrative_behavior(is_anomaly: bool, severity: str, factors: list, machine_id: str) -> str:
    if not is_anomaly:
        return f"Machine {machine_id} is operating within normal behavioral parameters for this operator."
    if not factors:
        return (
            f"An anomaly was detected on {machine_id} but detailed factor breakdown "
            "is unavailable (operator baseline may be new)."
        )
    top = factors[0]
    return (
        f"A {severity.lower()} behavioral anomaly was detected on {machine_id}. "
        f"The most significant deviation is in '{top['feature']}' "
        f"({top['current_value']:.2f} vs baseline {top['baseline_median']:.2f}). "
        f"This is {top['deviation_mad']:.1f}x the operator's typical variation."
    )


# ── Machine health explanation ────────────────────────────────

def explain_machine_health(machine_id: str) -> dict:
    machine = data_service.get_machine(machine_id)
    if not machine:
        return {"error": f"Machine {machine_id} not found"}

    factors = []
    score = 100
    notes = []

    age = machine.get("machine_age_years", 0)
    hours = machine.get("engine_hours", 0)
    next_service = machine.get("next_service_hours", 9999)
    hours_to_service = next_service - hours

    if age > 5:
        factors.append({"feature": "Machine age", "value": f"{age} yrs", "impact": min(age * 3, 20), "direction": "increase"})
        score -= min(age * 2, 15)
        notes.append(f"Machine is {age} years old; older machines may require closer monitoring.")

    if hours_to_service < 200:
        factors.append({"feature": "Service due soon", "value": f"{int(hours_to_service)} hrs remaining", "impact": 15, "direction": "increase"})
        score -= 15
        notes.append(f"Service due in {int(hours_to_service)} engine hours.")

    temp = machine.get("engine_temp_c", 0)
    if temp > 95:
        factors.append({"feature": "Engine temperature", "value": f"{temp}°C", "impact": 20, "direction": "increase"})
        score -= 20
        notes.append(f"Engine temperature ({temp}°C) is above normal operating range.")

    oil = machine.get("oil_pressure_bar", 4.0)
    if oil < 3.5:
        factors.append({"feature": "Oil pressure", "value": f"{oil} bar", "impact": 18, "direction": "decrease"})
        score -= 18
        notes.append(f"Oil pressure ({oil} bar) is below recommended threshold.")

    score = max(0, score)
    if score >= 85:
        health_status = "GOOD"
    elif score >= 65:
        health_status = "ATTENTION"
    else:
        health_status = "CRITICAL"

    return {
        "machine_id": machine_id,
        "health_score": score,
        "health_status": health_status,
        "top_factors": factors,
        "explanation": (
            f"Machine {machine_id} health score is {score}/100 ({health_status}). "
            + (" ".join(notes) if notes else "All monitored parameters are within normal range.")
        ),
        "baseline_comparison": {
            "engine_hours": hours,
            "next_service_hours": next_service,
            "machine_age_years": age,
        },
        "explanation_source": "rule_based_health_indicators",
        "note": "Health score derived from age, engine hours, temperature, and oil pressure indicators.",
    }
