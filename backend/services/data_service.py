"""
Central mock data layer.
All demo machines, operators, tasks live here.
Real telemetry columns match the CSV schema exactly so the ML
inference functions receive the right column names.
"""

from datetime import datetime, timedelta
import random

# ============================================================
# MACHINES
# ============================================================

MACHINES = {
    "EXC001": {
        "machine_id": "EXC001",
        "machine_type": "Excavator",
        "model": "CAT 320",
        "year": 2019,
        "machine_age_years": 5,
        "serial_number": "SN-EXC001-2019",
        "location": "Zone A – North Pit",
        "status": "OPERATIONAL",
        "engine_hours": 4821.5,
        "fuel_used_l": 3.2,
        "load_cycles": 7,
        "idling_time_min": 22,
        "seatbelt_status": "Fastened",
        "safety_alert_triggered": "No",
        "current_operator_id": "OP-07",
        "current_task_id": "T-EXC001-001",
        "fuel_level_pct": 72,
        "hydraulic_temp_c": 68,
        "engine_temp_c": 91,
        "oil_pressure_bar": 4.2,
        "last_service_date": "2024-11-15",
        "next_service_hours": 5000,
    },
    "EXC002": {
        "machine_id": "EXC002",
        "machine_type": "Excavator",
        "model": "CAT 336",
        "year": 2021,
        "machine_age_years": 3,
        "serial_number": "SN-EXC002-2021",
        "location": "Zone B – East Slope",
        "status": "OPERATIONAL",
        "engine_hours": 2310.0,
        "fuel_used_l": 2.8,
        "load_cycles": 5,
        "idling_time_min": 14,
        "seatbelt_status": "Fastened",
        "safety_alert_triggered": "No",
        "current_operator_id": "OP-03",
        "current_task_id": "T-EXC002-001",
        "fuel_level_pct": 88,
        "hydraulic_temp_c": 62,
        "engine_temp_c": 87,
        "oil_pressure_bar": 4.5,
        "last_service_date": "2025-01-10",
        "next_service_hours": 2500,
    },
    "EXC003": {
        "machine_id": "EXC003",
        "machine_type": "Excavator",
        "model": "CAT 390",
        "year": 2018,
        "machine_age_years": 6,
        "serial_number": "SN-EXC003-2018",
        "location": "Zone C – West Ridge",
        "status": "MAINTENANCE",
        "engine_hours": 7412.3,
        "fuel_used_l": 0.0,
        "load_cycles": 0,
        "idling_time_min": 0,
        "seatbelt_status": "Fastened",
        "safety_alert_triggered": "No",
        "current_operator_id": None,
        "current_task_id": None,
        "fuel_level_pct": 45,
        "hydraulic_temp_c": 25,
        "engine_temp_c": 24,
        "oil_pressure_bar": 0.0,
        "last_service_date": "2025-08-01",
        "next_service_hours": 7500,
    },
    "LD003": {
        "machine_id": "LD003",
        "machine_type": "Wheel Loader",
        "model": "CAT 980",
        "year": 2022,
        "machine_age_years": 2,
        "serial_number": "SN-LD003-2022",
        "location": "Zone A – Stockpile",
        "status": "OPERATIONAL",
        "engine_hours": 1105.7,
        "fuel_used_l": 1.9,
        "load_cycles": 11,
        "idling_time_min": 8,
        "seatbelt_status": "Unfastened",
        "safety_alert_triggered": "Yes",
        "current_operator_id": "OP-11",
        "current_task_id": "T-LD003-001",
        "fuel_level_pct": 61,
        "hydraulic_temp_c": 71,
        "engine_temp_c": 94,
        "oil_pressure_bar": 4.0,
        "last_service_date": "2025-06-20",
        "next_service_hours": 1250,
    },
    "DZ004": {
        "machine_id": "DZ004",
        "machine_type": "Dozer",
        "model": "CAT D8",
        "year": 2020,
        "machine_age_years": 4,
        "serial_number": "SN-DZ004-2020",
        "location": "Zone D – Haul Road",
        "status": "IDLE",
        "engine_hours": 3288.1,
        "fuel_used_l": 0.4,
        "load_cycles": 1,
        "idling_time_min": 55,
        "seatbelt_status": "Fastened",
        "safety_alert_triggered": "No",
        "current_operator_id": "OP-05",
        "current_task_id": None,
        "fuel_level_pct": 55,
        "hydraulic_temp_c": 58,
        "engine_temp_c": 79,
        "oil_pressure_bar": 3.9,
        "last_service_date": "2024-12-05",
        "next_service_hours": 3500,
    },
}

# ============================================================
# OPERATORS
# ============================================================

OPERATORS = {
    "OP-07": {
        "operator_id": "OP-07",
        "name": "James Mwangi",
        "skill_level": "Expert",
        "years_experience": 12,
        "certifications": ["CAT Operator Level 3", "Safety Leadership", "Hydraulics"],
        "shift": "Day",
        "shift_start": "06:00",
        "shift_end": "18:00",
        "total_engine_hours": 14820,
        "safety_incidents_lifetime": 0,
        "last_training_date": "2025-05-10",
        "training_modules_completed": ["Efficiency", "Safety Refresher", "Machine Familiarization"],
    },
    "OP-03": {
        "operator_id": "OP-03",
        "name": "Amara Diallo",
        "skill_level": "Intermediate",
        "years_experience": 5,
        "certifications": ["CAT Operator Level 2", "Safety Awareness"],
        "shift": "Day",
        "shift_start": "06:00",
        "shift_end": "18:00",
        "total_engine_hours": 5340,
        "safety_incidents_lifetime": 1,
        "last_training_date": "2025-03-22",
        "training_modules_completed": ["Safety Awareness", "Efficiency Basics"],
    },
    "OP-11": {
        "operator_id": "OP-11",
        "name": "Sven Eriksson",
        "skill_level": "Beginner",
        "years_experience": 1,
        "certifications": ["CAT Operator Level 1"],
        "shift": "Day",
        "shift_start": "06:00",
        "shift_end": "18:00",
        "total_engine_hours": 890,
        "safety_incidents_lifetime": 2,
        "last_training_date": "2025-07-01",
        "training_modules_completed": ["Safety Awareness"],
    },
    "OP-05": {
        "operator_id": "OP-05",
        "name": "Priya Nair",
        "skill_level": "Intermediate",
        "years_experience": 6,
        "certifications": ["CAT Operator Level 2", "Dozer Specialization"],
        "shift": "Day",
        "shift_start": "06:00",
        "shift_end": "18:00",
        "total_engine_hours": 6200,
        "safety_incidents_lifetime": 0,
        "last_training_date": "2025-04-18",
        "training_modules_completed": ["Efficiency", "Safety Awareness"],
    },
}

# ============================================================
# TASKS
# ============================================================

TASKS = {
    "T-EXC001-001": {
        "task_id": "T-EXC001-001",
        "machine_id": "EXC001",
        "operator_id": "OP-07",
        "task_type": "Earth Excavation",
        "description": "Excavation of Zone A North Pit — foundation layer",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "weather": "Rainy",
        "operator_skill": "Expert",
        "machine_age_years": 5,
        "estimated_time_min": 45,
        "started_at": (datetime.now() - timedelta(minutes=18)).isoformat(),
        "zone": "Zone A",
        "phase": "Phase 2 of 3",
        "progress_pct": 40,
    },
    "T-EXC002-001": {
        "task_id": "T-EXC002-001",
        "machine_id": "EXC002",
        "operator_id": "OP-03",
        "task_type": "Material Loading",
        "description": "Load aggregate to Zone B stockpile",
        "status": "IN_PROGRESS",
        "priority": "MEDIUM",
        "weather": "Cloudy",
        "operator_skill": "Intermediate",
        "machine_age_years": 3,
        "estimated_time_min": 35,
        "started_at": (datetime.now() - timedelta(minutes=8)).isoformat(),
        "zone": "Zone B",
        "phase": "Phase 1 of 2",
        "progress_pct": 23,
    },
    "T-LD003-001": {
        "task_id": "T-LD003-001",
        "machine_id": "LD003",
        "operator_id": "OP-11",
        "task_type": "Material Loading",
        "description": "Load crushed stone to haul trucks",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "weather": "Sunny",
        "operator_skill": "Beginner",
        "machine_age_years": 2,
        "estimated_time_min": 40,
        "started_at": (datetime.now() - timedelta(minutes=5)).isoformat(),
        "zone": "Zone A",
        "phase": "Phase 1 of 3",
        "progress_pct": 12,
    },
}

# ============================================================
# INCIDENTS (in-memory store)
# ============================================================

INCIDENTS: list[dict] = []
_incident_counter = 1

def create_incident(machine_id: str, operator_id: str, category: str,
                    description: str, severity: str, task_id: str | None = None) -> dict:
    global _incident_counter
    incident = {
        "incident_id": f"INC-{_incident_counter:04d}",
        "machine_id": machine_id,
        "operator_id": operator_id,
        "task_id": task_id,
        "category": category,
        "description": description,
        "severity": severity,
        "timestamp": datetime.now().isoformat(),
        "status": "OPEN",
    }
    INCIDENTS.append(incident)
    _incident_counter += 1
    return incident

def get_incidents(machine_id: str | None = None) -> list[dict]:
    if machine_id:
        return [i for i in INCIDENTS if i["machine_id"] == machine_id]
    return list(INCIDENTS)

def update_incident_status(incident_id: str, status: str) -> dict | None:
    for i in INCIDENTS:
        if i["incident_id"] == incident_id:
            i["status"] = status
            return i
    return None

# ============================================================
# SUPPORT REQUESTS (in-memory store)
# ============================================================

SUPPORT_REQUESTS: list[dict] = []
_support_counter = 1

def create_support_request(machine_id: str, operator_id: str, description: str,
                            troubleshooting_steps: list[str], xai_findings: str,
                            safety_state: str, task_id: str | None = None) -> dict:
    global _support_counter
    req = {
        "request_id": f"SR-{_support_counter:04d}",
        "machine_id": machine_id,
        "operator_id": operator_id,
        "task_id": task_id,
        "description": description,
        "troubleshooting_steps": troubleshooting_steps,
        "xai_findings": xai_findings,
        "safety_state": safety_state,
        "timestamp": datetime.now().isoformat(),
        "status": "PENDING",
    }
    SUPPORT_REQUESTS.append(req)
    _support_counter += 1
    return req

def get_support_requests(machine_id: str | None = None) -> list[dict]:
    if machine_id:
        return [r for r in SUPPORT_REQUESTS if r["machine_id"] == machine_id]
    return list(SUPPORT_REQUESTS)

# ============================================================
# SHIFT REPORTS (in-memory store)
# ============================================================

SHIFT_REPORTS: list[dict] = []

def store_shift_report(report: dict) -> dict:
    SHIFT_REPORTS.append(report)
    return report

def get_shift_reports(machine_id: str | None = None) -> list[dict]:
    if machine_id:
        return [r for r in SHIFT_REPORTS if r.get("machine_id") == machine_id]
    return list(SHIFT_REPORTS)

# ============================================================
# HELPERS
# ============================================================

def get_machine(machine_id: str) -> dict | None:
    return MACHINES.get(machine_id)

def get_operator(operator_id: str) -> dict | None:
    return OPERATORS.get(operator_id)

def get_task(task_id: str) -> dict | None:
    return TASKS.get(task_id)

def get_current_task_for_machine(machine_id: str) -> dict | None:
    machine = MACHINES.get(machine_id)
    if not machine or not machine.get("current_task_id"):
        return None
    return TASKS.get(machine["current_task_id"])

def get_all_machines() -> list[dict]:
    return list(MACHINES.values())

def get_all_operators() -> list[dict]:
    return list(OPERATORS.values())

def get_machine_history(machine_id: str) -> list[dict]:
    """Return synthetic shift history for a machine."""
    history = []
    base = datetime.now()
    task_types = ["Earth Excavation", "Material Loading", "Grading", "Trenching"]
    for i in range(7, 0, -1):
        day = base - timedelta(days=i)
        history.append({
            "date": day.strftime("%Y-%m-%d"),
            "engine_hours": round(random.uniform(7.5, 10.2), 1),
            "fuel_used_l": round(random.uniform(1.8, 4.5), 2),
            "load_cycles": random.randint(4, 14),
            "idling_time_min": random.randint(10, 45),
            "tasks_completed": random.randint(1, 3),
            "task_type": random.choice(task_types),
            "safety_events": random.randint(0, 1),
            "anomaly_detected": random.choice([False, False, False, True]),
        })
    return history
