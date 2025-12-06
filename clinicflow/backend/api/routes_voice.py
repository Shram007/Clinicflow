from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import os

router = APIRouter()

class UploadResponse(BaseModel):
    visit_id: str
    transcript: str

def _save_upload(file: UploadFile, visit_id: Optional[str]) -> Path:
    base = Path(__file__).resolve().parents[2]
    out_dir = base / "audio"
    out_dir.mkdir(parents=True, exist_ok=True)
    vid = visit_id or "tmp"
    ext = os.path.splitext(file.filename or "recording.webm")[1] or ".webm"
    out_path = out_dir / f"{vid}{ext}"
    with out_path.open("wb") as f:
        f.write(file.file.read())
    return out_path

def _transcribe(path: Path) -> str:
    provider = os.environ.get("STT_PROVIDER", "").lower()
    api_key = os.environ.get("OPENAI_API_KEY")
    if provider in {"openai", "whisper"} and api_key:
        try:
            from openai import OpenAI
            client = OpenAI()
            with path.open("rb") as f:
                r = client.audio.transcriptions.create(model="whisper-1", file=f)
            return getattr(r, "text", "") or ""
        except Exception:
            return ""
    return ""

@router.post("/voice/upload", response_model=UploadResponse)
async def upload_voice(file: UploadFile = File(...), visit_id: Optional[str] = Form(None)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="missing file")
    saved = _save_upload(file, visit_id)
    text = _transcribe(saved)
    return UploadResponse(visit_id=(visit_id or "tmp"), transcript=(text or "Transcription pending"))
