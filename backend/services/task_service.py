"""Task Service — Module 8 (ETA + what-if)."""

from backend.services import data_service, weather_service
from ml.inference import (
    predict_eta_with_uncertainty,
    compare_eta_scenarios,
    eta_what_if,
    weather_impact_engine,
)


def get_task_eta(task_id: str) -> dict:
    task = data_service.get_task(task_id)
    if not task:
        return {"error": f"Task {task_id} not found"}

    task_row = _task_to_row(task)
    eta = predict_eta_with_uncertainty(task_row)
    weather_ctx = weather_impact_engine(task["task_type"], task["weather"])
    weather_risk = weather_service.get_weather_risk(
        task["machine_id"], task_eta_min=eta["predicted_time_min"]
    )

    scenarios = {
        "If Sunny":  {"Weather": "Sunny"},
        "If Cloudy": {"Weather": "Cloudy"},
        "If Rainy":  {"Weather": "Rainy"},
        "If Windy":  {"Weather": "Windy"},
    }
    what_if = compare_eta_scenarios(task_row, scenarios)

    return {
        "task_id": task_id,
        "task_type": task["task_type"],
        "status": task["status"],
        "progress_pct": task.get("progress_pct", 0),
        "eta": eta,
        "weather_context": weather_ctx,
        "weather_risk": weather_risk,
        "what_if_scenarios": what_if,
        "operator_skill": task["operator_skill"],
        "machine_age_years": task["machine_age_years"],
        "current_weather": task["weather"],
    }


def get_current_task(machine_id: str) -> dict | None:
    task = data_service.get_current_task_for_machine(machine_id)
    if not task:
        return None
    task_row = _task_to_row(task)
    eta = predict_eta_with_uncertainty(task_row)
    return {**task, "eta": eta}


def _task_to_row(task: dict) -> dict:
    return {
        "Task Type": task["task_type"],
        "Weather": task["weather"],
        "Operator Skill": task["operator_skill"],
        "Machine Age (yrs)": task["machine_age_years"],
        "Estimated Time (min)": task["estimated_time_min"],
    }
