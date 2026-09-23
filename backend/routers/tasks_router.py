from fastapi import APIRouter
from backend.services.task_service import get_task_eta, get_current_task
from backend.services.data_service import TASKS

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("")
def list_tasks():
    return list(TASKS.values())

@router.get("/{task_id}")
def get_task(task_id: str):
    return TASKS.get(task_id) or {"error": f"Task {task_id} not found"}

@router.get("/{task_id}/eta")
def task_eta(task_id: str):
    return get_task_eta(task_id)

@router.get("/machine/{machine_id}/current")
def current_task(machine_id: str):
    t = get_current_task(machine_id)
    return t or {"message": f"No active task for {machine_id}"}
