from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.visit import VisitSummary, VisitDetail, VisitCreate
from ..services.agents_service import generate_visit_from_transcript
from fastapi.responses import FileResponse
from services.tts_service import synthesize_speech

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
@router.get("/visits/{visit_id}/summary_audio")
async def get_visit_summary_audio(visit_id: int):
    visit = next((v for v in VISITS_DB if v.id == visit_id), None)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    spoken_text = (
        f"Visit {visit.id}. {visit.title}. "
        f"Assessment: {visit.assessment}. "
        f"Plan: {visit.plan}."
    )

    audio_path = synthesize_speech(spoken_text, visit_id)

    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=audio_path.name,
    )