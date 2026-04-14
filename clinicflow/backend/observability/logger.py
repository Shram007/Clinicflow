"""
Structured JSON logger for ClinicFlow.

Usage::

    from clinicflow.backend.observability.logger import get_logger

    log = get_logger()
    log.info("llm_call_complete", visit_id=42, model="gpt-4o-mini", latency_ms=312.4)
    log.error("visit_generation_failed", visit_id=42, error="timeout")

Every call emits a single JSON line to stdout with at minimum::

    {
      "timestamp": "2024-01-15T10:30:00.123456",
      "level": "INFO",
      "service": "clinicflow",
      "event": "llm_call_complete",
      ...extra fields...
    }

Reading the logs
----------------
Pipe the application output through ``jq`` for pretty-printing::

    python -m clinicflow.backend | jq .

Or filter by event::

    python -m clinicflow.backend | jq 'select(.event == "llm_call_complete")'
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


_SERVICE_NAME = "clinicflow"


class _JsonFormatter(logging.Formatter):
    """Formats log records as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc)
            .isoformat(timespec="microseconds"),
            "level": record.levelname,
            "service": _SERVICE_NAME,
            "event": record.getMessage(),
        }
        # Merge any extra fields stored on the record by _StructuredAdapter
        extra = getattr(record, "_extra", {})
        payload.update(extra)
        return json.dumps(payload, default=str)


class _StructuredAdapter(logging.LoggerAdapter):
    """Wraps a Logger so keyword arguments become JSON fields."""

    def process(self, msg: str, kwargs: Any) -> tuple[str, Any]:
        extra_fields = kwargs.pop("extra_fields", {})
        existing_extra = kwargs.get("extra", {})
        existing_extra["_extra"] = extra_fields
        kwargs["extra"] = existing_extra
        return msg, kwargs

    # Convenience methods that accept keyword context
    def _log_with_fields(self, level: int, event: str, **fields: Any) -> None:
        self.log(level, event, extra_fields=fields)

    def debug(self, event: str, **fields: Any) -> None:  # type: ignore[override]
        self._log_with_fields(logging.DEBUG, event, **fields)

    def info(self, event: str, **fields: Any) -> None:  # type: ignore[override]
        self._log_with_fields(logging.INFO, event, **fields)

    def warning(self, event: str, **fields: Any) -> None:  # type: ignore[override]
        self._log_with_fields(logging.WARNING, event, **fields)

    def error(self, event: str, **fields: Any) -> None:  # type: ignore[override]
        self._log_with_fields(logging.ERROR, event, **fields)

    def critical(self, event: str, **fields: Any) -> None:  # type: ignore[override]
        self._log_with_fields(logging.CRITICAL, event, **fields)


def get_logger(name: str = _SERVICE_NAME) -> _StructuredAdapter:
    """Return a structured JSON logger.

    The logger is idempotent — calling ``get_logger()`` multiple times returns
    an adapter backed by the same underlying :class:`logging.Logger` instance,
    so handlers are never duplicated.
    """
    base_logger = logging.getLogger(name)

    if not base_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JsonFormatter())
        base_logger.addHandler(handler)
        base_logger.setLevel(logging.DEBUG)
        base_logger.propagate = False

    return _StructuredAdapter(base_logger, {})
