"""
Feature 3 — Closed-loop operator feedback service.
Stores acknowledge/not-relevant/something-else responses against anomaly events.
Compares current state to previous state to detect improvement.
Feature 5 — Shift timeline event log (per machine).

NOTE: This is a prototype feedback loop.
We do NOT claim the recommendation caused any improvement.
We only report the observed change.
"""

from datetime import datetime
from typing import Literal

# ── In-memory stores ──────────────────────────────────────────
# feedback_store: machine_id → list of feedback entries
_feedback_store: dict[str, list[dict]] = {}

# timeline_store: machine_id → list of timeline events
_timeline_store: dict[str, list[dict]] = {}

# snapshot_store: machine_id → last anomaly snapshot for before/after
_snapshot_store: dict[str, dict] = {}

FeedbackChoice = Literal["ACKNOWLEDGE", "NOT_RELEVANT", "SOMETHING_ELSE"]


# ============================================================
# FEEDBACK
# ============================================================

def record_feedback(
    machine_id: str,
    operator_id: str,
    event_type: str,          # "anomaly" | "eta_delay" | "weather_risk" | "safety"
    event_id: str,
    choice: FeedbackChoice,
    note: str = "",
    anomaly_snapshot: dict | None = None,
) -> dict:
    """Record operator feedback for an intelligence event."""
    entry = {
        "feedback_id": f"FB-{machine_id}-{len(_feedback_store.get(machine_id, []))+1:04d}",
        "machine_id":  machine_id,
        "operator_id": operator_id,
        "event_type":  event_type,
        "event_id":    event_id,
        "choice":      choice,
        "note":        note,
        "timestamp":   datetime.now().isoformat(),
    }

    if machine_id not in _feedback_store:
        _feedback_store[machine_id] = []
    _feedback_store[machine_id].append(entry)

    # Store snapshot for before/after comparison
    if anomaly_snapshot:
        _snapshot_store[machine_id] = {
            "snapshot":   anomaly_snapshot,
            "recorded_at": entry["timestamp"],
            "event_id":    event_id,
        }

    # Add timeline event
    _add_timeline_event(machine_id, {
        "event_type": "feedback",
        "label":      f"Operator {_choice_label(choice)}: {event_type.replace('_', ' ')}",
        "detail":     note or _choice_label(choice),
        "severity":   "info",
    })

    return entry


def get_feedback(machine_id: str) -> list[dict]:
    return _feedback_store.get(machine_id, [])


def _choice_label(choice: str) -> str:
    return {"ACKNOWLEDGE": "Acknowledged", "NOT_RELEVANT": "Marked not relevant",
            "SOMETHING_ELSE": "Reported alternative observation"}.get(choice, choice)


# ============================================================
# BEFORE / AFTER COMPARISON
# ============================================================

def compare_behavior_state(machine_id: str, current_anomaly: dict) -> dict | None:
    """
    Compare current anomaly state to the stored snapshot.
    Returns a before/after comparison dict, or None if no prior snapshot.
    IMPORTANT: We do NOT claim the recommendation caused the improvement.
    """
    prior = _snapshot_store.get(machine_id)
    if not prior:
        return None

    prior_snap  = prior["snapshot"]
    prior_score = prior_snap.get("anomaly_score", 0)
    cur_score   = current_anomaly.get("anomaly_score", 0)
    prior_sev   = prior_snap.get("severity", "NORMAL")
    cur_sev     = current_anomaly.get("severity", "NORMAL")

    sev_order = {"NORMAL": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    prior_ord = sev_order.get(prior_sev, 0)
    cur_ord   = sev_order.get(cur_sev, 0)

    if cur_ord < prior_ord:
        trend   = "IMPROVED"
        summary = "Behavior has moved closer to the operator's normal baseline."
    elif cur_ord > prior_ord:
        trend   = "WORSENED"
        summary = "Observed deviation has increased since the last recorded state."
    else:
        trend   = "UNCHANGED"
        summary = "Behavior remains at a similar deviation level."

    # Build factor comparison
    prior_factors = {f["feature"]: f for f in prior_snap.get("top_factors", [])}
    cur_factors   = {f["feature"]: f for f in current_anomaly.get("top_factors", [])}
    all_features  = set(prior_factors) | set(cur_factors)

    factor_deltas = []
    for feat in all_features:
        p = prior_factors.get(feat, {})
        c = cur_factors.get(feat, {})
        p_mad = p.get("deviation_mad", 0)
        c_mad = c.get("deviation_mad", 0)
        delta = round(c_mad - p_mad, 2)
        factor_deltas.append({
            "feature":      feat,
            "before_mad":   round(p_mad, 2),
            "after_mad":    round(c_mad, 2),
            "delta_mad":    delta,
            "direction":    "improved" if delta < 0 else ("worsened" if delta > 0 else "unchanged"),
        })

    factor_deltas.sort(key=lambda x: abs(x["delta_mad"]), reverse=True)

    return {
        "machine_id":       machine_id,
        "comparison_type":  "before_after_feedback",
        "recorded_at":      prior["recorded_at"],
        "compared_at":      datetime.now().isoformat(),
        "before": {
            "severity":      prior_sev,
            "anomaly_score": round(prior_score, 4),
        },
        "after": {
            "severity":      cur_sev,
            "anomaly_score": round(cur_score, 4),
        },
        "trend":    trend,
        "summary":  summary,
        "factor_deltas": factor_deltas[:5],
        "disclaimer": (
            "This comparison reports an observed change in the anomaly detection output. "
            "It does not establish that any recommendation caused this change."
        ),
    }


# ============================================================
# FEATURE 5 — SHIFT TIMELINE
# ============================================================

def _add_timeline_event(machine_id: str, event: dict):
    if machine_id not in _timeline_store:
        _timeline_store[machine_id] = []
    _timeline_store[machine_id].append({
        **event,
        "timestamp": datetime.now().isoformat(),
        "time_label": datetime.now().strftime("%H:%M"),
    })


def add_timeline_event(machine_id: str, event_type: str, label: str,
                       detail: str = "", severity: str = "info",
                       is_simulated: bool = False) -> dict:
    """Public entry point to add a timeline event from any service."""
    ev = {
        "event_type":   event_type,
        "label":        label,
        "detail":       detail,
        "severity":     severity,
        "is_simulated": is_simulated,
        "timestamp":    datetime.now().isoformat(),
        "time_label":   datetime.now().strftime("%H:%M"),
    }
    if machine_id not in _timeline_store:
        _timeline_store[machine_id] = []
    _timeline_store[machine_id].append(ev)
    return ev


def get_timeline(machine_id: str) -> list[dict]:
    """Return timeline events for a machine, most recent last."""
    stored = _timeline_store.get(machine_id, [])

    # Seed with synthetic shift-start event if empty
    if not stored:
        return _synthetic_seed_timeline(machine_id)

    return sorted(stored, key=lambda e: e["timestamp"])


def _synthetic_seed_timeline(machine_id: str) -> list[dict]:
    """
    Generate a seeded demo timeline from machine/task state.
    Clearly labelled as simulated/demo data.
    """
    from backend.services.data_service import get_machine, get_current_task_for_machine
    from backend.services.safety_service import evaluate_safety
    from backend.services.xai_service import explain_behavior

    machine = get_machine(machine_id)
    if not machine:
        return []

    now = datetime.now()
    events = []

    def mins_ago(m):
        return (now - __import__('datetime').timedelta(minutes=m)).strftime("%H:%M")

    # Shift start
    events.append({
        "event_type":   "shift_start",
        "label":        "Shift started",
        "detail":       f"Operator {machine.get('current_operator_id','—')} began shift",
        "severity":     "info",
        "time_label":   mins_ago(90),
        "timestamp":    (now - __import__('datetime').timedelta(minutes=90)).isoformat(),
        "is_simulated": True,
    })

    # Task start
    task = get_current_task_for_machine(machine_id)
    if task:
        events.append({
            "event_type":   "task_start",
            "label":        f"Task started: {task['task_type']}",
            "detail":       task.get("description", ""),
            "severity":     "info",
            "time_label":   mins_ago(60),
            "timestamp":    (now - __import__('datetime').timedelta(minutes=60)).isoformat(),
            "is_simulated": True,
        })

    # Safety state
    try:
        saf = evaluate_safety(machine_id)
        if saf.get("triggered_rules"):
            for r in saf["triggered_rules"][:2]:
                events.append({
                    "event_type":   "safety_event",
                    "label":        f"Safety rule triggered: {r['rule_id']}",
                    "detail":       r["description"],
                    "severity":     r["severity"].lower(),
                    "time_label":   mins_ago(30),
                    "timestamp":    (now - __import__('datetime').timedelta(minutes=30)).isoformat(),
                    "is_simulated": True,
                })
        else:
            events.append({
                "event_type":   "safety_check",
                "label":        "Safety check: NORMAL",
                "detail":       "No safety rules triggered.",
                "severity":     "info",
                "time_label":   mins_ago(45),
                "timestamp":    (now - __import__('datetime').timedelta(minutes=45)).isoformat(),
                "is_simulated": True,
            })
    except Exception:
        pass

    # Behavior state
    try:
        beh = explain_behavior(machine_id)
        if beh.get("prediction") == "anomaly":
            events.append({
                "event_type":   "anomaly_detected",
                "label":        f"Behavioral anomaly detected ({beh.get('severity','MEDIUM')})",
                "detail":       beh.get("explanation", ""),
                "severity":     beh.get("severity", "medium").lower(),
                "time_label":   mins_ago(20),
                "timestamp":    (now - __import__('datetime').timedelta(minutes=20)).isoformat(),
                "is_simulated": True,
            })
        else:
            events.append({
                "event_type":   "behavior_normal",
                "label":        "Behavior: within normal parameters",
                "detail":       "No significant deviation from operator baseline.",
                "severity":     "info",
                "time_label":   mins_ago(20),
                "timestamp":    (now - __import__('datetime').timedelta(minutes=20)).isoformat(),
                "is_simulated": True,
            })
    except Exception:
        pass

    # Now
    events.append({
        "event_type":   "current",
        "label":        "Current state",
        "detail":       f"Machine {machine_id} — {machine.get('status','OPERATIONAL')}",
        "severity":     "info",
        "time_label":   now.strftime("%H:%M"),
        "timestamp":    now.isoformat(),
        "is_simulated": False,
    })

    # Store for future use
    _timeline_store[machine_id] = events
    return events
