from fastapi import APIRouter
from schemas.visit import VisitSummary, VisitDetail

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

@router.get("/visits/{visit_id}", response_model=VisitDetail)
async def get_visit(visit_id: int):
    base = next((v for v in MOCK_VISITS if v.id == visit_id), None) or MOCK_VISITS[0]
    return VisitDetail(
        id=base.id,
        title=base.title,
        date=base.date,
        summary=base.summary,
        subjective="Patient reports intermittent chest tightness for 3 days...",
        objective="Vitals stable. Normal ECG in clinic.",
        assessment="Likely non-cardiac chest pain, rule out GERD.",
        plan="Start PPI trial, follow-up in 2 weeks, ER precautions explained.",
    )