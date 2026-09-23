from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.copilot_service import process_message

router = APIRouter(prefix="/api/copilot", tags=["Copilot"])

class CopilotMessage(BaseModel):
    message: str
    machine_id: str | None = None
    task_id: str | None = None
    operator_id: str | None = None

@router.post("/chat")
def chat(body: CopilotMessage):
    return process_message(
        message=body.message,
        machine_id=body.machine_id,
        task_id=body.task_id,
        operator_id=body.operator_id,
    )

@router.get("/tools")
def list_tools():
    from backend.services.copilot_service import TOOLS
    return {"available_tools": list(TOOLS.keys())}
