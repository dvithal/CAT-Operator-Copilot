"""Report + Shift Handover generation service."""

from datetime import datetime
from backend.services import data_service
from backend.services.safety_service import evaluate_safety
from backend.services.xai_service import explain_behavior, explain_machine_health
from backend.services.task_service import get_current_task
from backend.services.weather_service import get_current_weather
from backend.services.training_service import get_training_recommendations


def generate_shift_handover(machine_id: str) -> dict:
    machine = data_service.get_machine(machine_id)
    if not machine:
        return {"error": f"Machine {machine_id} not found"}

    operator_id = machine.get("current_operator_id")
    operator = data_service.get_operator(operator_id) if operator_id else None
    task = get_current_task(machine_id)
    safety = evaluate_safety(machine_id)
    behavior = explain_behavior(machine_id)
    health = explain_machine_health(machine_id)
    weather = get_current_weather(machine_id)
    incidents = data_service.get_incidents(machine_id)
    training = get_training_recommendations(operator_id) if operator_id else {}

    completed_tasks = [t for t in data_service.TASKS.values()
                       if t.get("machine_id") == machine_id and t.get("status") == "COMPLETED"]
    pending_tasks = [t for t in data_service.TASKS.values()
                     if t.get("machine_id") == machine_id and t.get("status") == "IN_PROGRESS"]

    handover_text = _format_handover(
        machine, operator, task, safety, behavior, health, weather, incidents
    )

    report = {
        "type": "SHIFT_HANDOVER",
        "generated_at": datetime.now().isoformat(),
        "machine_id": machine_id,
        "machine_model": machine["model"],
        "operator": operator,
        "shift": operator["shift"] if operator else "Unknown",
        "current_task": task,
        "completed_tasks_count": len(completed_tasks),
        "pending_tasks": pending_tasks,
        "machine_condition": health["health_status"],
        "health_score": health["health_score"],
        "safety_score": safety["safety_score"],
        "safety_decision": safety["decision"],
        "safety_events_count": len([r for r in safety.get("triggered_rules", [])]),
        "behavior_anomaly": behavior.get("prediction") == "anomaly",
        "behavior_severity": behavior.get("severity", "NORMAL"),
        "weather_condition": weather["condition"],
        "weather_risk": weather["risk_level"],
        "incidents_count": len(incidents),
        "incidents": incidents,
        "training_recommendations": training.get("recommendations", []),
        "handover_text": handover_text,
        "note": "Report generated from structured backend data. Not AI-generated.",
    }

    data_service.store_shift_report(report)
    return report


def generate_daily_report(machine_id: str) -> dict:
    machine = data_service.get_machine(machine_id)
    if not machine:
        return {"error": f"Machine {machine_id} not found"}

    history = data_service.get_machine_history(machine_id)
    safety = evaluate_safety(machine_id)
    health = explain_machine_health(machine_id)
    behavior = explain_behavior(machine_id)
    incidents = data_service.get_incidents(machine_id)
    support_requests = data_service.get_support_requests(machine_id)

    total_engine_hours = sum(d["engine_hours"] for d in history)
    total_fuel = sum(d["fuel_used_l"] for d in history)
    total_cycles = sum(d["load_cycles"] for d in history)
    total_idle = sum(d["idling_time_min"] for d in history)
    total_tasks = sum(d["tasks_completed"] for d in history)
    safety_events_count = sum(d["safety_events"] for d in history)
    anomaly_days = sum(1 for d in history if d["anomaly_detected"])

    avg_fuel_efficiency = round(total_fuel / total_cycles, 3) if total_cycles else 0
    idle_ratio = round(total_idle / (total_engine_hours * 60) * 100, 1) if total_engine_hours else 0

    return {
        "type": "DAILY_REPORT",
        "generated_at": datetime.now().isoformat(),
        "machine_id": machine_id,
        "machine_model": machine["model"],
        "period_days": 7,
        "summary": {
            "total_engine_hours": round(total_engine_hours, 1),
            "total_fuel_used_l": round(total_fuel, 2),
            "total_load_cycles": total_cycles,
            "total_idle_min": total_idle,
            "idle_pct": idle_ratio,
            "tasks_completed": total_tasks,
            "fuel_per_load_cycle": avg_fuel_efficiency,
        },
        "safety": {
            "score": safety["safety_score"],
            "decision": safety["decision"],
            "events_count": safety_events_count,
            "triggered_rules": safety.get("triggered_rules", []),
        },
        "behavior": {
            "anomaly_days": anomaly_days,
            "current_status": behavior.get("prediction", "normal"),
            "severity": behavior.get("severity", "NORMAL"),
        },
        "machine_health": {
            "score": health["health_score"],
            "status": health["health_status"],
            "factors": health.get("top_factors", []),
        },
        "incidents": incidents,
        "support_requests": support_requests,
        "history": history,
        "note": "Report generated from structured backend data. Not AI-generated.",
    }


def _format_handover(machine, operator, task, safety, behavior, health, weather, incidents) -> str:
    lines = [
        "=" * 50,
        "SHIFT HANDOVER",
        "=" * 50,
        f"Machine:      {machine['machine_id']} — {machine['model']}",
        f"Operator:     {operator['name'] if operator else 'Unknown'}",
        f"Generated:    {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "TASK STATUS",
        "-" * 30,
    ]
    if task:
        lines += [
            f"Current Task: {task.get('task_type', 'Unknown')}",
            f"Status:       {task.get('status', 'Unknown')}",
            f"Progress:     {task.get('progress_pct', 0)}%",
            f"Predicted ETA: {task.get('eta', {}).get('predicted_time_min', 'N/A')} min",
        ]
    else:
        lines.append("Current Task: None assigned")

    lines += [
        "",
        "MACHINE CONDITION",
        "-" * 30,
        f"Health:       {health['health_status']} (score: {health['health_score']}/100)",
        f"Safety:       {safety['decision']} (score: {safety['safety_score']}/100)",
        f"Behavior:     {behavior.get('severity', 'NORMAL')}",
        "",
        "WEATHER",
        "-" * 30,
        f"Condition:    {weather['condition']}",
        f"Risk Level:   {weather['risk_level']}",
        "",
        "INCIDENTS THIS SHIFT",
        "-" * 30,
    ]

    if incidents:
        for inc in incidents:
            lines.append(f"  [{inc['severity']}] {inc['description']}")
    else:
        lines.append("  None recorded.")

    if safety.get("triggered_rules"):
        lines += ["", "SAFETY ALERTS", "-" * 30]
        for r in safety["triggered_rules"]:
            lines.append(f"  [{r['severity']}] {r['description']}")

    lines += [
        "",
        "NEXT OPERATOR NOTE",
        "-" * 30,
        "Review machine condition before continuing heavy operations.",
        "=" * 50,
    ]
    return "\n".join(lines)
