from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
from ..schemas.voice import VoiceUploadResponse
from ..services.stt_service import transcribe_audio

router = APIRouter()

AUDIO_DIR = Path("audio_uploads")
AUDIO_DIR.mkdir(exist_ok=True)

@router.post("/voice/upload", response_model=VoiceUploadResponse)
async def upload_voice(file: UploadFile = File(...)):
    if not (file.content_type and file.content_type.startswith("audio/")):
        raise HTTPException(status_code=400, detail="File must be an audio type")
    uid = uuid.uuid4().hex
    ext = Path(file.filename or "recording.webm").suffix or ".webm"
    out_path = AUDIO_DIR / f"{uid}{ext}"
    content = await file.read()
    with out_path.open("wb") as f:
        f.write(content)
    transcript_text = transcribe_audio(out_path)
    return VoiceUploadResponse(visit_id=1, transcript=transcript_text or "")
