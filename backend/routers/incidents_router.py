from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.data_service import create_incident, get_incidents, update_incident_status

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

class IncidentCreate(BaseModel):
    machine_id: str
    operator_id: str
    category: str
    description: str
    severity: str = "MEDIUM"
    task_id: str | None = None

class StatusUpdate(BaseModel):
    status: str

@router.get("")
def list_incidents(machine_id: str | None = None):
    return get_incidents(machine_id)

@router.post("")
def new_incident(body: IncidentCreate):
    return create_incident(
        body.machine_id, body.operator_id, body.category,
        body.description, body.severity, body.task_id
    )

@router.patch("/{incident_id}/status")
def patch_status(incident_id: str, body: StatusUpdate):
    result = update_incident_status(incident_id, body.status)
    return result or {"error": f"Incident {incident_id} not found"}
