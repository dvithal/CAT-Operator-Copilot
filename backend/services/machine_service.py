"""
Machine Service — Module 3 (Digital Passport + QR).
One QR per machine, encodes only the machine_id.
"""

import io
import base64
from backend.services import data_service, weather_service
from backend.services.xai_service import explain_machine_health
from backend.services.safety_service import evaluate_safety
from ml.inference import predict_anomaly


def get_passport(machine_id: str) -> dict:
    machine = data_service.get_machine(machine_id)
    if not machine:
        return {"error": f"Machine {machine_id} not found"}

    operator = None
    if machine.get("current_operator_id"):
        operator = data_service.get_operator(machine["current_operator_id"])

    task = data_service.get_current_task_for_machine(machine_id)
    weather = weather_service.get_current_weather(machine_id)
    safety = evaluate_safety(machine_id)
    health = explain_machine_health(machine_id)

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
    behavior = predict_anomaly(machine_row)

    return {
        "machine_id": machine["machine_id"],
        "machine_type": machine["machine_type"],
        "model": machine["model"],
        "year": machine["year"],
        "serial_number": machine["serial_number"],
        "location": machine["location"],
        "status": machine["status"],
        "current_operator": operator,
        "engine_hours": machine["engine_hours"],
        "fuel_used_l": machine["fuel_used_l"],
        "fuel_level_pct": machine["fuel_level_pct"],
        "load_cycles": machine["load_cycles"],
        "idle_time_min": machine["idling_time_min"],
        "seatbelt_status": machine["seatbelt_status"],
        "safety_alert": machine["safety_alert_triggered"],
        "current_task": task,
        "task_status": task["status"] if task else None,
        "health": {
            "score": health["health_score"],
            "status": health["health_status"],
        },
        "behavior": {
            "anomaly": behavior["anomaly"],
            "anomaly_score": behavior["anomaly_score"],
            "status": "ANOMALY" if behavior["anomaly"] else "NORMAL",
        },
        "weather": {
            "condition": weather["condition"],
            "risk_level": weather["risk_level"],
        },
        "safety_score": safety["safety_score"],
        "safety_decision": safety["decision"],
        "last_service_date": machine["last_service_date"],
        "next_service_hours": machine["next_service_hours"],
    }


def get_qr_code(machine_id: str) -> dict:
    """Generate a base64-encoded PNG QR code that encodes only the machine_id."""
    try:
        import qrcode
        from PIL import Image

        qr_data = f"CAT-MACHINE-{machine_id}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")

        return {
            "machine_id": machine_id,
            "qr_data": qr_data,
            "qr_image_base64": b64,
            "format": "PNG",
            "note": "One QR per machine. Scan to open Digital Machine Passport.",
        }
    except ImportError:
        return {
            "machine_id": machine_id,
            "qr_data": f"CAT-MACHINE-{machine_id}",
            "qr_image_base64": None,
            "error": "qrcode library not installed. Run: pip install qrcode[pil]",
        }


def get_machine_list() -> list[dict]:
    machines = data_service.get_all_machines()
    result = []
    for m in machines:
        safety = evaluate_safety(m["machine_id"])
        health = explain_machine_health(m["machine_id"])
        machine_row = {
            "Machine ID": m["machine_id"],
            "Operator ID": m.get("current_operator_id", "UNKNOWN"),
            "Engine Hours": m["engine_hours"],
            "Fuel Used (L)": m["fuel_used_l"],
            "Load Cycles": m["load_cycles"],
            "Idling Time (min)": m["idling_time_min"],
            "Seatbelt Status": m["seatbelt_status"],
            "Safety Alert Triggered": m["safety_alert_triggered"],
        }
        behavior = predict_anomaly(machine_row)
        task = data_service.get_current_task_for_machine(m["machine_id"])
        result.append({
            "machine_id": m["machine_id"],
            "machine_type": m["machine_type"],
            "model": m["model"],
            "status": m["status"],
            "location": m["location"],
            "current_operator_id": m.get("current_operator_id"),
            "current_task": task["task_type"] if task else None,
            "safety_score": safety["safety_score"],
            "safety_decision": safety["decision"],
            "health_score": health["health_score"],
            "health_status": health["health_status"],
            "behavior_anomaly": behavior["anomaly"],
            "fuel_level_pct": m["fuel_level_pct"],
            "engine_hours": m["engine_hours"],
        })
    return result
