# ClinicFlow Observability

This package provides **structured JSON logging** and **LLM-native metrics tracking** for the ClinicFlow backend.

## Modules

### `logger.py` — Structured JSON logging

Every log call emits a single JSON line to **stdout** with the following guaranteed fields:

| Field | Example |
|---|---|
| `timestamp` | `"2024-01-15T10:30:00.123456+00:00"` |
| `level` | `"INFO"` |
| `service` | `"clinicflow"` |
| `event` | `"llm_call_complete"` |
| …extra fields… | `visit_id`, `model`, `latency_ms`, … |

**Usage:**

```python
from clinicflow.backend.observability.logger import get_logger

log = get_logger()
log.info("voice_upload_received", visit_id=7, filename="audio.webm")
log.error("visit_generation_failed", visit_id=7, error="timeout")
```

**Reading logs:**

```bash
# Pretty-print all JSON log lines
python -m clinicflow.backend | jq .

# Filter to LLM call events only
python -m clinicflow.backend | jq 'select(.event == "llm_call_complete")'

# Aggregate total tokens across all calls
python -m clinicflow.backend | jq '[select(.event == "llm_call_complete") | .total_tokens] | add'
```

---

### `metrics.py` — LLM metrics tracking

`record_llm_call(...)` captures per-request metrics and updates in-memory counters. It also calls the structured logger, so every LLM call automatically emits a `llm_call_complete` log line.

**Tracked fields per call:**

| Field | Source |
|---|---|
| `model` | `resp.model` |
| `input_tokens` | `resp.usage.prompt_tokens` |
| `output_tokens` | `resp.usage.completion_tokens` |
| `total_tokens` | `resp.usage.total_tokens` |
| `latency_ms` | `time.perf_counter()` wall-clock |
| `cost_estimate_usd` | Approximate, using known per-token rates |

**Cost rates** (approximate, as of early 2025):

| Model | Input | Output |
|---|---|---|
| `gpt-4o-mini` | $0.150 / 1M tokens | $0.600 / 1M tokens |
| `gpt-4o` | $2.50 / 1M tokens | $10.00 / 1M tokens |

Unknown models produce `cost_estimate_usd = 0`.

**Usage:**

```python
from clinicflow.backend.observability.metrics import record_llm_call, get_metrics_summary

record_llm_call(
    model="gpt-4o-mini",
    input_tokens=512,
    output_tokens=256,
    total_tokens=768,
    latency_ms=310.5,
    visit_id=42,          # optional extra context
)

summary = get_metrics_summary()
# {
#   "total_calls": 1,
#   "total_input_tokens": 512,
#   "total_output_tokens": 256,
#   "total_tokens": 768,
#   "total_cost_usd": 0.0002304,
#   "avg_latency_ms": 310.5
# }
```

---

## Health endpoint

`GET /api/health/metrics` returns the in-memory counters since the last process start:

```json
{
  "total_calls": 5,
  "total_input_tokens": 3120,
  "total_output_tokens": 1540,
  "total_tokens": 4660,
  "total_cost_usd": 0.001392,
  "avg_latency_ms": 284.3
}
```

Counters reset on process restart. For persistent metrics, forward the JSON log lines to a log aggregator (e.g. Cloud Logging, Datadog, or Loki).

---

## Log events emitted by `agents_service.py`

| Event | Level | When |
|---|---|---|
| `llm_call_start` | INFO | Before the OpenAI API call |
| `llm_call_complete` | INFO | After a successful API call (via `record_llm_call`) |
| `visit_generation_fallback` | WARNING | JSON parse of LLM response failed, using defaults |
| `visit_generation_failed` | ERROR | OpenAI API call raised an exception |
