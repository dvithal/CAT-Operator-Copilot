"""
Weather Service — Module 8.
Demo mock forecast.  If a real API key is wired in, swap the
_fetch_real_weather() stub.  The structure stays identical.
"""

from datetime import datetime, timedelta
import random

# ── Deterministic "current" weather per machine zone ─────────
_ZONE_WEATHER = {
    "EXC001": {"condition": "Rainy",  "temp_c": 18, "wind_kph": 22, "humidity_pct": 82},
    "EXC002": {"condition": "Cloudy", "temp_c": 21, "wind_kph": 14, "humidity_pct": 68},
    "EXC003": {"condition": "Sunny",  "temp_c": 27, "wind_kph": 9,  "humidity_pct": 45},
    "LD003":  {"condition": "Sunny",  "temp_c": 26, "wind_kph": 11, "humidity_pct": 50},
    "DZ004":  {"condition": "Windy",  "temp_c": 20, "wind_kph": 38, "humidity_pct": 55},
}

# ── Risk weights per condition ────────────────────────────────
_RISK_WEIGHTS = {
    "Sunny": 0,
    "Cloudy": 10,
    "Windy": 25,
    "Rainy": 45,
    "Stormy": 80,
}

_IMPACT_DESCRIPTIONS = {
    "Sunny": "Optimal operating conditions.",
    "Cloudy": "Slightly reduced visibility. No significant operational impact.",
    "Windy": "Elevated wind may affect load stability and operator comfort.",
    "Rainy": "Slippery ground conditions. Reduced visibility. Increased stopping distance.",
    "Stormy": "Hazardous conditions. Assess before continuing operations.",
}


def get_current_weather(machine_id: str) -> dict:
    base = _ZONE_WEATHER.get(machine_id, {"condition": "Sunny", "temp_c": 24, "wind_kph": 10, "humidity_pct": 55})
    return {
        "condition": base["condition"],
        "temperature_c": base["temp_c"],
        "wind_kph": base["wind_kph"],
        "humidity_pct": base["humidity_pct"],
        "visibility_m": _visibility(base["condition"]),
        "risk_level": _risk_level(base["condition"]),
        "operational_impact": _IMPACT_DESCRIPTIONS.get(base["condition"], ""),
        "observed_at": datetime.now().isoformat(),
    }


def get_forecast(machine_id: str) -> list[dict]:
    """Return 6 x 15-minute forecast slots."""
    base = _ZONE_WEATHER.get(machine_id, {"condition": "Sunny", "temp_c": 24, "wind_kph": 10, "humidity_pct": 55})
    slots = []
    conditions = _progression(base["condition"])
    now = datetime.now()
    for i, cond in enumerate(conditions):
        t = now + timedelta(minutes=15 * (i + 1))
        slots.append({
            "time": t.strftime("%H:%M"),
            "offset_min": 15 * (i + 1),
            "condition": cond,
            "temperature_c": base["temp_c"] + random.randint(-2, 2),
            "wind_kph": base["wind_kph"] + random.randint(-4, 8),
            "risk_level": _risk_level(cond),
            "risk_score": _RISK_WEIGHTS.get(cond, 0),
        })
    return slots


def get_weather_risk(machine_id: str, task_eta_min: float | None = None) -> dict:
    current = get_current_weather(machine_id)
    forecast = get_forecast(machine_id)

    risk_score = _RISK_WEIGHTS.get(current["condition"], 0)
    overlap = None
    overlap_details = None

    if task_eta_min is not None:
        for slot in forecast:
            if slot["offset_min"] <= task_eta_min <= slot["offset_min"] + 15:
                if slot["risk_score"] > risk_score:
                    overlap = slot
                    overlap_details = (
                        f"The predicted task completion (~{int(task_eta_min)} min from now) "
                        f"overlaps with expected {slot['condition'].lower()} conditions "
                        f"around {slot['time']}. "
                        f"Consider reviewing the task plan accordingly."
                    )
                break

    # Find highest-risk future slot
    worst = max(forecast, key=lambda s: s["risk_score"]) if forecast else None

    return {
        "machine_id": machine_id,
        "current_condition": current["condition"],
        "current_risk_score": risk_score,
        "current_risk_level": current["risk_level"],
        "task_eta_min": task_eta_min,
        "task_weather_overlap": overlap is not None,
        "overlap_slot": overlap,
        "overlap_advisory": overlap_details,
        "worst_upcoming_condition": worst,
        "forecast": forecast,
        "assessment_timestamp": datetime.now().isoformat(),
    }


# ── Internal helpers ──────────────────────────────────────────

def _visibility(condition: str) -> int:
    return {"Sunny": 10000, "Cloudy": 7000, "Windy": 8000, "Rainy": 3000, "Stormy": 800}.get(condition, 9000)


def _risk_level(condition: str) -> str:
    score = _RISK_WEIGHTS.get(condition, 0)
    if score >= 60:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    if score >= 10:
        return "LOW"
    return "NORMAL"


def _progression(current: str) -> list[str]:
    """Deterministic 6-slot weather progression for demo."""
    progressions = {
        "Sunny":  ["Sunny", "Sunny", "Cloudy", "Cloudy", "Rainy", "Rainy"],
        "Cloudy": ["Cloudy", "Cloudy", "Rainy", "Rainy", "Rainy", "Stormy"],
        "Rainy":  ["Rainy", "Rainy", "Rainy", "Cloudy", "Cloudy", "Sunny"],
        "Windy":  ["Windy", "Windy", "Windy", "Cloudy", "Cloudy", "Sunny"],
        "Stormy": ["Stormy", "Stormy", "Rainy", "Rainy", "Cloudy", "Cloudy"],
    }
    return progressions.get(current, ["Sunny"] * 6)
