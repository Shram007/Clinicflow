import os
import time
from datetime import date
import json
from openai import OpenAI
from ..schemas.visit import VisitDetail
from ..observability import get_logger, record_llm_call

log = get_logger()

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

    log.info("llm_call_start", visit_id=visit_id, prompt_version=ACTIVE_PROMPT_VERSION)
    start = time.perf_counter()
    try:
        resp = client.chat.completions.create(
            model=os.getenv("VISIT_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": PROMPTS[ACTIVE_PROMPT_VERSION]},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
    except Exception as exc:
        log.error("visit_generation_failed", visit_id=visit_id, error=str(exc))
        raise
    latency_ms = (time.perf_counter() - start) * 1000

    usage = resp.usage
    if usage is not None:
        record_llm_call(
            model=resp.model,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            latency_ms=latency_ms,
            visit_id=visit_id,
        )

    content = resp.choices[0].message.content
    try:
        data = json.loads(content)
    except Exception:
        log.warning(
            "visit_generation_fallback",
            visit_id=visit_id,
            reason="json_parse_failed",
        )
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
