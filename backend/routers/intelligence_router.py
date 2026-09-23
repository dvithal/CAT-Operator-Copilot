"""
Intelligence Router — new endpoints for features 3, 5, 6, 7, 8, 9.
All existing routes remain unchanged.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.intelligence_service import (
    run_what_if,
    get_model_transparency,
    get_fleet_attribution_audit,
    safety_counterfactual,
)
from backend.services.feedback_service import (
    record_feedback,
    get_feedback,
    compare_behavior_state,
    get_timeline,
    add_timeline_event,
)
from backend.services.xai_service import explain_behavior

router = APIRouter(prefix="/api/intelligence", tags=["Intelligence"])


# ── Feature 6: What-if simulation ────────────────────────────
@router.get("/whatif/{machine_id}")
def what_if(machine_id: str, task_id: str | None = None):
    return run_what_if(machine_id, task_id)


# ── Feature 7: Model transparency ────────────────────────────
@router.get("/transparency")
def model_transparency():
    return get_model_transparency()


# ── Feature 8: Fleet attribution audit ───────────────────────
@router.get("/fleet-audit")
def fleet_audit():
    return get_fleet_attribution_audit()


# ── Feature 9: Safety counterfactual ─────────────────────────
@router.get("/safety-counterfactual/{machine_id}")
def safety_cf(machine_id: str):
    return safety_counterfactual(machine_id)


# ── Feature 3: Feedback ───────────────────────────────────────
class FeedbackBody(BaseModel):
    operator_id: str
    event_type: str
    event_id: str
    choice: str   # ACKNOWLEDGE | NOT_RELEVANT | SOMETHING_ELSE
    note: str = ""

@router.post("/feedback/{machine_id}")
def submit_feedback(machine_id: str, body: FeedbackBody):
    # Capture current anomaly snapshot for before/after
    try:
        snapshot = explain_behavior(machine_id)
    except Exception:
        snapshot = None

    entry = record_feedback(
        machine_id  = machine_id,
        operator_id = body.operator_id,
        event_type  = body.event_type,
        event_id    = body.event_id,
        choice      = body.choice,
        note        = body.note,
        anomaly_snapshot = snapshot,
    )
    return entry

@router.get("/feedback/{machine_id}")
def get_machine_feedback(machine_id: str):
    return get_feedback(machine_id)

@router.get("/feedback/{machine_id}/comparison")
def behavior_comparison(machine_id: str):
    try:
        current = explain_behavior(machine_id)
        result  = compare_behavior_state(machine_id, current)
        return result or {"message": "No prior snapshot available for comparison."}
    except Exception as e:
        return {"error": str(e)}


# ── Feature 5: Shift timeline ─────────────────────────────────
@router.get("/timeline/{machine_id}")
def shift_timeline(machine_id: str):
    return {"machine_id": machine_id, "events": get_timeline(machine_id)}


class TimelineEvent(BaseModel):
    event_type: str
    label: str
    detail: str = ""
    severity: str = "info"
    is_simulated: bool = False

@router.post("/timeline/{machine_id}")
def post_timeline_event(machine_id: str, body: TimelineEvent):
    return add_timeline_event(
        machine_id   = machine_id,
        event_type   = body.event_type,
        label        = body.label,
        detail       = body.detail,
        severity     = body.severity,
        is_simulated = body.is_simulated,
    )
