from fastapi import APIRouter, Query
from backend.services.weather_service import get_current_weather, get_forecast, get_weather_risk

router = APIRouter(prefix="/api/weather", tags=["Weather"])

@router.get("/{machine_id}")
def weather(machine_id: str):
    return {
        "current": get_current_weather(machine_id),
        "forecast": get_forecast(machine_id),
    }

@router.get("/{machine_id}/risk")
def weather_risk(machine_id: str, eta_min: float | None = Query(default=None)):
    return get_weather_risk(machine_id, task_eta_min=eta_min)
