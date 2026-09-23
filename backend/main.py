from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ml.inference import run_intelligence


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="CAT Operator Copilot API",
    description="AI intelligence API for machine operators",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# REQUEST SCHEMAS
# ============================================================

class TaskInput(BaseModel):

    task_type: str
    weather: str
    operator_skill: str
    machine_age_years: float
    estimated_time_min: float


class MachineInput(BaseModel):

    machine_id: str
    operator_id: str
    engine_hours: float
    fuel_used_l: float
    load_cycles: float
    idling_time_min: float
    seatbelt_status: str
    safety_alert_triggered: str


class IntelligenceRequest(BaseModel):

    task: TaskInput
    machine: MachineInput


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "CAT Operator Copilot API"
    }


# ============================================================
# INTELLIGENCE ENDPOINT
# ============================================================

@app.post("/intelligence")
def get_intelligence(
    request: IntelligenceRequest
):

    task = {
        "Task Type":
            request.task.task_type,

        "Weather":
            request.task.weather,

        "Operator Skill":
            request.task.operator_skill,

        "Machine Age (yrs)":
            request.task.machine_age_years,

        "Estimated Time (min)":
            request.task.estimated_time_min
    }

    machine = {
        "Machine ID":
            request.machine.machine_id,

        "Operator ID":
            request.machine.operator_id,

        "Engine Hours":
            request.machine.engine_hours,

        "Fuel Used (L)":
            request.machine.fuel_used_l,

        "Load Cycles":
            request.machine.load_cycles,

        "Idling Time (min)":
            request.machine.idling_time_min,

        "Seatbelt Status":
            request.machine.seatbelt_status,

        "Safety Alert Triggered":
            request.machine.safety_alert_triggered
    }

    result = run_intelligence(
        task,
        machine
    )

    return result