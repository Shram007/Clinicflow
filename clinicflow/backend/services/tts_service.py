import os
from pathlib import Path
from fastapi import HTTPException
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

AUDIO_OUT_DIR = Path("tts_output")
AUDIO_OUT_DIR.mkdir(exist_ok=True)

def synthesize_speech(text: str, visit_id: int) -> Path:
    """
    Convert text -> speech using OpenAI TTS and save as an mp3.
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")

    try:
        audio = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",     # other voices exist; keep one stable for demo
            input=text,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")

    out_path = AUDIO_OUT_DIR / f"visit_{visit_id}.mp3"
    audio.stream_to_file(out_path)
    return out_path