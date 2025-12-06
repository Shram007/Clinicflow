from fastapi import APIRouter
from ..schemas.visit import VisitSummary, VisitDetail

router = APIRouter()

MOCK_VISITS = [
    VisitSummary(
        id=1,
        title="Chest pain consultation",
        date="2025-11-28",
        summary="Possible GERD vs anxiety-related chest discomfort.",
    ),
    VisitSummary(
        id=2,
        title="Migraine follow-up",
        date="2025-11-20",
        summary="Improvement with prophylactic medication.",
    ),
]

@router.get("/visits", response_model=list[VisitSummary])
async def list_visits():
    return MOCK_VISITS
