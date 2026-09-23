"""
Rule-based Safety Engine — Module 4.
LLM never touches this.  Thresholds are configurable via THRESHOLDS dict.
"""

from backend.services import data_service, weather_service
from ml.inference import safety_engine as ml_safety_engine, predict_anomaly

# ── Configurable thresholds ───────────────────────────────────
THRESHOLDS = {
    "normal_min": 85,
    "caution_min": 70,
    "check_min": 50,
    # below check_min → STOP/ESCALATE
}

# ── Penalty table ─────────────────────────────────────────────
PENALTIES = [
    {
        "rule_id": "SEATBELT_UNFASTENED",
        "condition": lambda m, _weather, _anomaly: m["seatbelt_status"] == "Unfastened",
        "penalty": 40,
        "severity": "CRITICAL",
        "description": "Operator seatbelt is unfastened.",
        "recommendation": "Operator must fasten seatbelt before continuing operations.",
    },
    {
        "rule_id": "SAFETY_ALERT_ACTIVE",
        "condition": lambda m, _weather, _anomaly: m["safety_alert_triggered"] == "Yes",
        "penalty": 20,
        "severity": "HIGH",
        "description": "Active safety alert detected on machine.",
        "recommendation": "Investigate the source of the safety alert before proceeding.",
    },
    {
        "rule_id": "HIGH_WEATHER_RISK",
        "condition": lambda m, weather, _anomaly: weather.get("risk_score", 0) >= 45,
        "penalty": 15,
        "severity": "HIGH",
        "description": "Current weather conditions present elevated operational risk.",
        "recommendation": "Review ground conditions and visibility before continuing.",
    },
    {
        "rule_id": "MEDIUM_WEATHER_RISK",
        "condition": lambda m, weather, _anomaly: 25 <= weather.get("risk_score", 0) < 45,
        "penalty": 8,
        "severity": "MEDIUM",
        "description": "Weather conditions require additional caution.",
        "recommendation": "Maintain reduced operating speed and increased awareness.",
    },
    {
        "rule_id": "BEHAVIOR_ANOMALY_HIGH",
        "condition": lambda m, _weather, anomaly: anomaly.get("anomaly") and anomaly.get("anomaly_score", 0) < -0.1,
        "penalty": 12,
        "severity": "MEDIUM",
        "description": "Behavioral anomaly detected — operation pattern deviates from operator baseline.",
        "recommendation": "Review recent operational data and confirm machine is functioning normally.",
    },
    {
        "rule_id": "EXCESSIVE_IDLE",
        "condition": lambda m, _weather, _anomaly: m.get("idling_time_min", 0) > 40,
        "penalty": 5,
        "severity": "LOW",
        "description": "Excessive idle time detected this session.",
        "recommendation": "Consider shutting down engine during extended idle periods.",
    },
    {
        "rule_id": "HIGH_ENGINE_TEMP",
        "condition": lambda m, _weather, _anomaly: m.get("engine_temp_c", 0) > 100,
        "penalty": 15,
        "severity": "HIGH",
        "description": "Engine temperature above normal operating range.",
        "recommendation": "Allow engine to cool. Check coolant level and radiator.",
    },
]


def evaluate_safety(machine_id: str) -> dict:
    machine = data_service.get_machine(machine_id)
    if not machine:
        return {"error": f"Machine {machine_id} not found"}

    weather = weather_service.get_current_weather(machine_id)
    weather_risk_score = {"Sunny": 0, "Cloudy": 10, "Windy": 25, "Rainy": 45, "Stormy": 80}.get(
        weather["condition"], 0
    )
    weather_ctx = {"risk_score": weather_risk_score}

    machine_row = {
        "Machine ID": machine["machine_id"],
        "Operator ID": machine.get("current_operator_id", "UNKNOWN"),
        "Engine Hours": machine["engine_hours"],
        "Fuel Used (L)": machine["fuel_used_l"],
        "Load Cycles": machine["load_cycles"],
        "Idling Time (min)": machine["idling_time_min"],
        "Seatbelt Status": machine["seatbelt_status"],
        "Safety Alert Triggered": machine["safety_alert_triggered"],
    }
    anomaly = predict_anomaly(machine_row)

    score = 100
    triggered_rules = []
    recommendations = []
    has_critical = False

    for rule in PENALTIES:
        try:
            fired = rule["condition"](machine, weather_ctx, anomaly)
        except Exception:
            fired = False
        if fired:
            score -= rule["penalty"]
            triggered_rules.append({
                "rule_id": rule["rule_id"],
                "severity": rule["severity"],
                "description": rule["description"],
            })
            recommendations.append(rule["recommendation"])
            if rule["severity"] == "CRITICAL":
                has_critical = True

    score = max(0, score)

    # Decision
    if has_critical or score < THRESHOLDS["check_min"]:
        decision = "STOP / ESCALATE"
        severity = "CRITICAL"
    elif score < THRESHOLDS["caution_min"]:
        decision = "SAFETY CHECK RECOMMENDED"
        severity = "HIGH"
    elif score < THRESHOLDS["normal_min"]:
        decision = "CONTINUE WITH CAUTION"
        severity = "MEDIUM"
    else:
        decision = "NORMAL"
        severity = "NORMAL"

    return {
        "machine_id": machine_id,
        "safety_score": score,
        "decision": decision,
        "severity": severity,
        "triggered_rules": triggered_rules,
        "recommendations": list(dict.fromkeys(recommendations)),  # deduplicate
        "weather_condition": weather["condition"],
        "seatbelt_status": machine["seatbelt_status"],
        "safety_alert": machine["safety_alert_triggered"],
        "behavior_anomaly": anomaly.get("anomaly", False),
        "note": "Safety decision generated by deterministic rule-based engine. Not AI-generated.",
    }
