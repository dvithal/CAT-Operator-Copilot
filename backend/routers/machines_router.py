from fastapi import APIRouter
from backend.services.machine_service import get_passport, get_qr_code, get_machine_list
from backend.services.data_service import get_machine_history, get_machine

router = APIRouter(prefix="/api/machines", tags=["Machines"])

@router.get("")
def list_machines():
    return get_machine_list()

@router.get("/{machine_id}")
def get_machine_detail(machine_id: str):
    m = get_machine(machine_id)
    return m or {"error": f"Machine {machine_id} not found"}

@router.get("/{machine_id}/passport")
def machine_passport(machine_id: str):
    return get_passport(machine_id)

@router.get("/{machine_id}/qr")
def machine_qr(machine_id: str):
    return get_qr_code(machine_id)

@router.get("/{machine_id}/history")
def machine_history(machine_id: str):
    return {"machine_id": machine_id, "history": get_machine_history(machine_id)}
