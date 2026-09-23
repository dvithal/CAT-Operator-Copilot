from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Legacy inference endpoint (kept for backwards compatibility) ──
from ml.inference import run_intelligence

# ── Routers ───────────────────────────────────────────────────
from backend.routers import context_router
from backend.routers import machines_router
from backend.routers import safety_router
from backend.routers import xai_router
from backend.routers import weather_router
from backend.routers import tasks_router
from backend.routers import incidents_router
from backend.routers import support_router
from backend.routers import reports_router
from backend.routers import training_router
from backend.routers import copilot_router

# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="CAT Smart Operator Copilot API",
    description="Enterprise ML-powered API for CAT machinery operators.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount all routers ─────────────────────────────────────────
app.include_router(context_router.router)
app.include_router(machines_router.router)
app.include_router(safety_router.router)
app.include_router(xai_router.router)
app.include_router(weather_router.router)
app.include_router(tasks_router.router)
app.include_router(incidents_router.router)
app.include_router(support_router.router)
app.include_router(reports_router.router)
app.include_router(training_router.router)
app.include_router(copilot_router.router)


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "CAT Smart Operator Copilot API",
        "version": "2.0.0",
        "docs": "/docs",
    }


# ============================================================
# LEGACY — /intelligence (v1 kept intact)
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

@app.post("/intelligence")
def get_intelligence(request: IntelligenceRequest):
    task = {
        "Task Type": request.task.task_type,
        "Weather": request.task.weather,
        "Operator Skill": request.task.operator_skill,
        "Machine Age (yrs)": request.task.machine_age_years,
        "Estimated Time (min)": request.task.estimated_time_min,
    }
    machine = {
        "Machine ID": request.machine.machine_id,
        "Operator ID": request.machine.operator_id,
        "Engine Hours": request.machine.engine_hours,
        "Fuel Used (L)": request.machine.fuel_used_l,
        "Load Cycles": request.machine.load_cycles,
        "Idling Time (min)": request.machine.idling_time_min,
        "Seatbelt Status": request.machine.seatbelt_status,
        "Safety Alert Triggered": request.machine.safety_alert_triggered,
    }
    return run_intelligence(task, machine)
