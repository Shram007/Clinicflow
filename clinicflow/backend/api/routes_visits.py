from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.visit import VisitSummary, VisitDetail, VisitCreate
from ..services.agents_service import generate_visit_from_transcript

router = APIRouter()

# In-memory DB
VISITS_DB: list[VisitDetail] = []

if not VISITS_DB:
    VISITS_DB.append(
        VisitDetail(
            id=1,
            title="Chest pain consultation",
            date="2025-11-28",
            summary="Possible GERD vs anxiety-related chest discomfort.",
            subjective="Patient reports intermittent chest tightness for 3 days...",
            objective="Vitals stable. Normal ECG in clinic.",
            assessment="Likely non-cardiac chest pain, rule out GERD.",
            plan="Start PPI trial, follow-up in 2 weeks, ER precautions explained.",
        )
    )

@router.get("/visits", response_model=List[VisitSummary])
async def list_visits():
    return [
        VisitSummary(id=v.id, title=v.title, date=v.date, summary=v.summary)
        for v in VISITS_DB
    ]

@router.get("/visits/{visit_id}", response_model=VisitDetail)
async def get_visit(visit_id: int):
    for v in VISITS_DB:
        if v.id == visit_id:
            return v
    raise HTTPException(status_code=404, detail="Visit not found")

@router.post("/visits", response_model=VisitDetail)
async def create_visit(payload: VisitCreate):
    new_id = (max((v.id for v in VISITS_DB), default=0) + 1)
    visit = generate_visit_from_transcript(payload.transcript, new_id)
    VISITS_DB.append(visit)
    return visit
