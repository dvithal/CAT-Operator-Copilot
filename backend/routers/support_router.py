from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.data_service import create_support_request, get_support_requests

router = APIRouter(prefix="/api/support", tags=["Support"])

class SupportCreate(BaseModel):
    machine_id: str
    operator_id: str
    description: str
    troubleshooting_steps: list[str] = []
    xai_findings: str = ""
    safety_state: str = "UNKNOWN"
    task_id: str | None = None

@router.get("")
def list_requests(machine_id: str | None = None):
    return get_support_requests(machine_id)

@router.post("")
def new_request(body: SupportCreate):
    return create_support_request(
        body.machine_id, body.operator_id, body.description,
        body.troubleshooting_steps, body.xai_findings,
        body.safety_state, body.task_id
    )
