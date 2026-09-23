from fastapi import APIRouter
from backend.services.context_service import build_context

router = APIRouter(prefix="/api/context", tags=["Context"])

@router.get("/{machine_id}")
def get_context(machine_id: str):
    return build_context(machine_id)

@router.get("/{machine_id}/current")
def get_current_context(machine_id: str):
    return build_context(machine_id)
