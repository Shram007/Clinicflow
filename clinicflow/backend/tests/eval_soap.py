"""
Evaluation harness for ClinicFlow SOAP note generation.
Scores LLM outputs for: structural correctness, content fidelity, and generation latency.
"""
import os
import time
import pytest

# Required keys that every SOAP note output must contain
REQUIRED_KEYS = ["title", "subjective", "objective", "assessment", "plan", "summary"]

# Test transcripts with expected signal words
TEST_CASES = [
    {
        "transcript": "Patient reports a 3-day headache, denies fever. BP 130/85. Likely tension headache.",
        "expected_signals": {"subjective": ["headache"], "assessment": ["headache", "tension"]},
    },
    {
        "transcript": "45-year-old with chest tightness on exertion for 2 weeks. No radiation. EKG normal.",
        "expected_signals": {"subjective": ["chest", "exertion"], "objective": ["ekg", "normal"]},
    },
]

LATENCY_BUDGET_SECONDS = 10.0  # max acceptable generation time


@pytest.mark.parametrize("case", TEST_CASES)
def test_soap_has_all_required_keys(case):
    """Score: structural correctness — all 6 required keys must be present and non-empty."""
    from clinicflow.backend.services.agents_service import generate_visit_from_transcript
    result = generate_visit_from_transcript(case["transcript"], visit_id=1)
    for key in REQUIRED_KEYS:
        value = getattr(result, key, None)
        assert value is not None, f"[FAIL] Missing key: {key}"
        assert isinstance(value, str), f"[FAIL] Key {key} must be a string"
        assert len(value) > 0, f"[FAIL] Key {key} must not be empty"


@pytest.mark.parametrize("case", TEST_CASES)
def test_soap_content_fidelity(case):
    """Score: content fidelity — subjective/assessment must contain transcript signal words."""
    from clinicflow.backend.services.agents_service import generate_visit_from_transcript
    result = generate_visit_from_transcript(case["transcript"], visit_id=1)
    for field, signals in case["expected_signals"].items():
        field_text = getattr(result, field, "").lower()
        matched = any(sig.lower() in field_text for sig in signals)
        assert matched, (
            f"[FAIL] Field '{field}' did not contain any of {signals}. "
            f"Got: '{field_text[:120]}'"
        )


@pytest.mark.parametrize("case", TEST_CASES)
def test_soap_generation_latency(case):
    """Score: latency — generation must complete within {LATENCY_BUDGET_SECONDS}s."""
    from clinicflow.backend.services.agents_service import generate_visit_from_transcript
    start = time.perf_counter()
    generate_visit_from_transcript(case["transcript"], visit_id=1)
    elapsed = time.perf_counter() - start
    assert elapsed < LATENCY_BUDGET_SECONDS, (
        f"[FAIL] Generation took {elapsed:.2f}s — exceeded budget of {LATENCY_BUDGET_SECONDS}s"
    )


def test_soap_fallback_on_invalid_model(monkeypatch):
    """Score: self-correction — fallback must produce a valid VisitDetail even when JSON parse fails."""
    from clinicflow.backend.services import agents_service
    from unittest.mock import MagicMock

    # Force the LLM to return unparseable content
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = "NOT VALID JSON {{{"
    monkeypatch.setattr(agents_service.client.chat.completions, "create", lambda **kwargs: mock_resp)

    result = agents_service.generate_visit_from_transcript("test transcript", visit_id=99)
    for key in REQUIRED_KEYS:
        assert getattr(result, key, None) is not None, f"Fallback missing key: {key}"
