"""Training recommendation service."""

from backend.services import data_service
from backend.services.safety_service import evaluate_safety
from ml.inference import predict_anomaly


TRAINING_RULES = [
    {
        "rule_id": "EFFICIENCY_TRAINING",
        "trigger": lambda safety, anomaly, op: anomaly.get("anomaly") and
                   any(f.get("factor") == "Idling behavior" for f in anomaly.get("reasons", [])),
        "module": "Efficiency & Fuel Optimization",
        "reason": "Repeated excessive idle time detected — operator deviating from baseline.",
        "priority": "HIGH",
    },
    {
        "rule_id": "SAFETY_REFRESHER",
        "trigger": lambda safety, anomaly, op: any(
            r["rule_id"] in ("SEATBELT_UNFASTENED", "SAFETY_ALERT_ACTIVE")
            for r in safety.get("triggered_rules", [])
        ),
        "module": "Safety Refresher",
        "reason": "Safety event detected — seatbelt or active safety alert.",
        "priority": "CRITICAL",
    },
    {
        "rule_id": "MACHINE_FAMILIARIZATION",
        "trigger": lambda safety, anomaly, op: (op or {}).get("safety_incidents_lifetime", 0) >= 2,
        "module": "Machine Familiarization",
        "reason": "Operator has recorded multiple lifetime safety incidents.",
        "priority": "MEDIUM",
    },
    {
        "rule_id": "FUEL_EFFICIENCY",
        "trigger": lambda safety, anomaly, op: anomaly.get("anomaly") and
                   any(f.get("factor") == "Fuel efficiency" for f in anomaly.get("reasons", [])),
        "module": "Fuel Efficiency & Load Management",
        "reason": "Fuel usage deviating significantly from operator baseline.",
        "priority": "MEDIUM",
    },
    {
        "rule_id": "ADVANCED_OPERATIONS",
        "trigger": lambda safety, anomaly, op: (op or {}).get("skill_level") == "Beginner",
        "module": "Advanced Machine Operations",
        "reason": "Operator is classified as Beginner level.",
        "priority": "LOW",
    },
]


def get_training_recommendations(operator_id: str) -> dict:
    operator = data_service.get_operator(operator_id)
    if not operator:
        return {"error": f"Operator {operator_id} not found"}

    # Find machine this operator is on
    machine = None
    for m in data_service.get_all_machines():
        if m.get("current_operator_id") == operator_id:
            machine = m
            break

    safety_result = {}
    anomaly = {}
    if machine:
        safety_result = evaluate_safety(machine["machine_id"])
        machine_row = {
            "Machine ID": machine["machine_id"],
            "Operator ID": operator_id,
            "Engine Hours": machine["engine_hours"],
            "Fuel Used (L)": machine["fuel_used_l"],
            "Load Cycles": machine["load_cycles"],
            "Idling Time (min)": machine["idling_time_min"],
            "Seatbelt Status": machine["seatbelt_status"],
            "Safety Alert Triggered": machine["safety_alert_triggered"],
        }
        anomaly = predict_anomaly(machine_row)

    recommendations = []
    for rule in TRAINING_RULES:
        try:
            if rule["trigger"](safety_result, anomaly, operator):
                recommendations.append({
                    "rule_id": rule["rule_id"],
                    "module": rule["module"],
                    "reason": rule["reason"],
                    "priority": rule["priority"],
                    "already_completed": rule["module"] in operator.get("training_modules_completed", []),
                })
        except Exception:
            pass

    recommendations.sort(
        key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(x["priority"], 4)
    )

    return {
        "operator_id": operator_id,
        "operator_name": operator["name"],
        "skill_level": operator["skill_level"],
        "last_training_date": operator["last_training_date"],
        "completed_modules": operator.get("training_modules_completed", []),
        "recommendations": recommendations,
        "total_recommendations": len(recommendations),
    }
