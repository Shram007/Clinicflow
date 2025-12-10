import os
from pathlib import Path
from fastapi import HTTPException
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_audio(path: Path) -> str:
    if not path.exists():
        raise HTTPException(status_code=500, detail="Audio file not found on server")
    try:
        with path.open("rb") as f:
            model = os.getenv("STT_MODEL", "gpt-4o-mini-transcribe")
            resp = client.audio.transcriptions.create(model=model, file=f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {e}")
    return getattr(resp, "text", "")
