from fastapi import APIRouter
from backend.services.xai_service import explain_task_eta, explain_behavior, explain_machine_health

router = APIRouter(prefix="/api/xai", tags=["XAI"])

@router.get("/task/{task_id}")
def xai_task(task_id: str):
    return explain_task_eta(task_id)

@router.get("/behavior/{machine_id}")
def xai_behavior(machine_id: str):
    return explain_behavior(machine_id)

@router.get("/machine/{machine_id}")
def xai_machine(machine_id: str):
    return explain_machine_health(machine_id)
