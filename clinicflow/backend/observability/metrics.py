"""
LLM-native metrics tracking for ClinicFlow.

Captures per-call metrics (token counts, latency, cost) and maintains
lightweight in-memory counters that can be exposed via the health endpoint.

Usage::

    from clinicflow.backend.observability.metrics import record_llm_call, get_metrics_summary

    record_llm_call(
        model="gpt-4o-mini",
        input_tokens=512,
        output_tokens=256,
        total_tokens=768,
        latency_ms=310.5,
    )

    summary = get_metrics_summary()
    # {"total_calls": 1, "total_tokens": 768, "total_cost_usd": 0.000174, ...}

Cost estimates
--------------
Rates are approximate public list prices for ``gpt-4o-mini``
(as of early 2025). Update ``_COST_PER_TOKEN`` if rates change or if you add
other models.
"""

from __future__ import annotations

from typing import Any

from .logger import get_logger

log = get_logger()

# ---------------------------------------------------------------------------
# Per-token cost rates (USD).  Only gpt-4o-mini is listed; unknown models
# fall back to 0 so cost_estimate_usd is always present but may be 0.
# ---------------------------------------------------------------------------
_COST_PER_TOKEN: dict[str, dict[str, float]] = {
    "gpt-4o-mini": {
        "input":  0.150 / 1_000_000,   # $0.150 per 1M input tokens
        "output": 0.600 / 1_000_000,   # $0.600 per 1M output tokens
    },
    "gpt-4o": {
        "input":  2.50 / 1_000_000,
        "output": 10.00 / 1_000_000,
    },
}


# ---------------------------------------------------------------------------
# In-memory counters (reset on process restart)
# ---------------------------------------------------------------------------
_counters: dict[str, Any] = {
    "total_calls": 0,
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "total_tokens": 0,
    "total_cost_usd": 0.0,
    "total_latency_ms": 0.0,
}


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Return an approximate USD cost for the given token counts and model."""
    rates = _COST_PER_TOKEN.get(model, {})
    return (
        input_tokens * rates.get("input", 0.0)
        + output_tokens * rates.get("output", 0.0)
    )


def record_llm_call(
    *,
    model: str,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    latency_ms: float,
    **extra: Any,
) -> None:
    """Record a single LLM API call and emit a structured log line.

    Parameters
    ----------
    model:         The model identifier returned by the API (``resp.model``).
    input_tokens:  ``resp.usage.prompt_tokens``
    output_tokens: ``resp.usage.completion_tokens``
    total_tokens:  ``resp.usage.total_tokens``
    latency_ms:    Wall-clock time for the API call in milliseconds.
    **extra:       Any additional context fields (e.g. ``visit_id``).
    """
    cost = _estimate_cost(model, input_tokens, output_tokens)

    # Update counters
    _counters["total_calls"] += 1
    _counters["total_input_tokens"] += input_tokens
    _counters["total_output_tokens"] += output_tokens
    _counters["total_tokens"] += total_tokens
    _counters["total_cost_usd"] += cost
    _counters["total_latency_ms"] += latency_ms

    log.info(
        "llm_call_complete",
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        latency_ms=round(latency_ms, 2),
        cost_estimate_usd=round(cost, 8),
        **extra,
    )


def get_metrics_summary() -> dict[str, Any]:
    """Return a snapshot of the in-memory counters.

    Suitable for embedding in health-check or monitoring endpoints.
    """
    avg_latency = (
        _counters["total_latency_ms"] / _counters["total_calls"]
        if _counters["total_calls"] > 0
        else 0.0
    )
    return {
        "total_calls": _counters["total_calls"],
        "total_input_tokens": _counters["total_input_tokens"],
        "total_output_tokens": _counters["total_output_tokens"],
        "total_tokens": _counters["total_tokens"],
        "total_cost_usd": round(_counters["total_cost_usd"], 6),
        "avg_latency_ms": round(avg_latency, 2),
    }
