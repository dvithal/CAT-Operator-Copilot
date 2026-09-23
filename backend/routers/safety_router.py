from fastapi import APIRouter
from backend.services.safety_service import evaluate_safety

router = APIRouter(prefix="/api/safety", tags=["Safety"])

@router.get("/{machine_id}")
def get_safety(machine_id: str):
    return evaluate_safety(machine_id)
