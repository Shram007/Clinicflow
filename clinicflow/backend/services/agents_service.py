import os
from datetime import date
import json
from openai import OpenAI
from ..schemas.visit import VisitDetail

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_visit_from_transcript(transcript: str, visit_id: int) -> VisitDetail:
    prompt = (
        "You are a clinical documentation assistant. Given the following doctor voice note transcript, "
        "produce a concise SOAP note plus a short title and 1–2 sentence summary.\n\n"
        f"Transcript:\n{transcript}\n\n"
        "Respond in strict JSON with keys:\n"
        "- title (string)\n"
        "- subjective (string)\n"
        "- objective (string)\n"
        "- assessment (string)\n"
        "- plan (string)\n"
        "- summary (string)\n"
    )

    resp = client.chat.completions.create(
        model=os.getenv("VISIT_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "You are a precise medical scribe. Do not add diagnoses not implied by the note."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    content = resp.choices[0].message.content
    try:
        data = json.loads(content)
    except Exception:
        data = {
            "title": "Clinical visit",
            "subjective": transcript,
            "objective": "",
            "assessment": "",
            "plan": "",
            "summary": transcript[:200],
        }

    today = date.today().isoformat()
    return VisitDetail(
        id=visit_id,
        title=data.get("title", "Clinical visit"),
        date=today,
        summary=data.get("summary", transcript[:200]),
        subjective=data.get("subjective", ""),
        objective=data.get("objective", ""),
        assessment=data.get("assessment", ""),
        plan=data.get("plan", ""),
    )
