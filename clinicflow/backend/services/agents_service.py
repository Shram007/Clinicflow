import os
import time
from datetime import date
import json
from openai import OpenAI
from ..schemas.visit import VisitDetail

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPTS: dict[str, str] = {
    "v1": (
        "You are a clinical documentation assistant. Given the following doctor voice note transcript, "
        "produce a concise SOAP note plus a short title and 1–2 sentence summary.\n\n"
        "Respond in strict JSON with keys: title, subjective, objective, assessment, plan, summary."
    ),
    "v2": (
        "You are a precise medical scribe. Convert the transcript into a SOAP note. "
        "Be conservative: do not infer diagnoses not explicitly stated. "
        "Respond in strict JSON with keys: title, subjective, objective, assessment, plan, summary."
    ),
}

ACTIVE_PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v1")
if ACTIVE_PROMPT_VERSION not in PROMPTS:
    raise ValueError(
        f"PROMPT_VERSION={ACTIVE_PROMPT_VERSION!r} is not a valid version. "
        f"Choose from: {list(PROMPTS)}"
    )

def generate_visit_from_transcript(transcript: str, visit_id: int) -> VisitDetail:
    prompt = (
        f"Transcript:\n{transcript}\n\n"
        "Respond in strict JSON with keys:\n"
        "- title (string)\n"
        "- subjective (string)\n"
        "- objective (string)\n"
        "- assessment (string)\n"
        "- plan (string)\n"
        "- summary (string)\n"
    )

    print(f"[prompt_version] active={ACTIVE_PROMPT_VERSION}")
    start = time.perf_counter()
    resp = client.chat.completions.create(
        model=os.getenv("VISIT_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": PROMPTS[ACTIVE_PROMPT_VERSION]},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    latency_ms = (time.perf_counter() - start) * 1000
    usage = resp.usage
    if usage is not None:
        print(
            f"[llm_metrics] model={os.getenv('VISIT_MODEL', 'gpt-4o-mini')} "
            f"tokens_in={usage.prompt_tokens} "
            f"tokens_out={usage.completion_tokens} "
            f"total_tokens={usage.total_tokens} "
            f"latency_ms={latency_ms:.1f}"
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
