from fastapi import APIRouter
from backend.services.training_service import get_training_recommendations
from backend.services.data_service import get_all_operators

router = APIRouter(prefix="/api/training", tags=["Training"])

@router.get("/{operator_id}")
def training(operator_id: str):
    return get_training_recommendations(operator_id)

@router.get("")
def all_training():
    results = []
    for op in get_all_operators():
        results.append(get_training_recommendations(op["operator_id"]))
    return results
