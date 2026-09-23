from fastapi import APIRouter
from backend.services.report_service import generate_shift_handover, generate_daily_report
from backend.services.data_service import get_shift_reports

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/shift/{machine_id}")
def shift_handover(machine_id: str):
    return generate_shift_handover(machine_id)

@router.get("/daily/{machine_id}")
def daily_report(machine_id: str):
    return generate_daily_report(machine_id)

@router.get("/history/{machine_id}")
def report_history(machine_id: str):
    return get_shift_reports(machine_id)
