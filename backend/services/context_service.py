"""
Context Engine — Module 2.
Collects and normalises context from all data sources.
Does NOT make safety decisions.
"""

from datetime import datetime
from backend.services import data_service
from backend.services import weather_service
from ml.inference import predict_anomaly, predict_eta_with_uncertainty, safety_engine


def build_context(machine_id: str) -> dict:
    machine = data_service.get_machine(machine_id)
    if not machine:
        return {"error": f"Machine {machine_id} not found"}

    operator = None
    if machine.get("current_operator_id"):
        operator = data_service.get_operator(machine["current_operator_id"])

    task = data_service.get_current_task_for_machine(machine_id)

    weather = weather_service.get_current_weather(machine_id)
    forecast = weather_service.get_forecast(machine_id)

    # ── ML outputs ────────────────────────────────────────────
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

    behavior_prediction = predict_anomaly(machine_row)
    safety_result = safety_engine(machine_row)

    task_prediction = None
    if task:
        task_row = {
            "Task Type": task["task_type"],
            "Weather": task["weather"],
            "Operator Skill": task["operator_skill"],
            "Machine Age (yrs)": task["machine_age_years"],
            "Estimated Time (min)": task["estimated_time_min"],
        }
        task_prediction = predict_eta_with_uncertainty(task_row)

    return {
        "machine": {
            "machine_id": machine["machine_id"],
            "machine_type": machine["machine_type"],
            "model": machine["model"],
            "status": machine["status"],
            "engine_hours": machine["engine_hours"],
            "fuel_used_l": machine["fuel_used_l"],
            "fuel_level_pct": machine["fuel_level_pct"],
            "load_cycles": machine["load_cycles"],
            "idling_time_min": machine["idling_time_min"],
            "seatbelt_status": machine["seatbelt_status"],
            "safety_alert_triggered": machine["safety_alert_triggered"],
            "hydraulic_temp_c": machine["hydraulic_temp_c"],
            "engine_temp_c": machine["engine_temp_c"],
            "oil_pressure_bar": machine["oil_pressure_bar"],
        },
        "operator": operator,
        "task": task,
        "weather": {
            "current": weather,
            "forecast": forecast,
        },
        "safety": safety_result,
        "behavior_prediction": behavior_prediction,
        "task_prediction": task_prediction,
        "timestamp": datetime.now().isoformat(),
    }
