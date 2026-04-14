from fastapi import APIRouter
from ..observability.metrics import get_metrics_summary

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/health/metrics")
async def health_metrics():
    """Return in-memory LLM usage counters accumulated since the last process start."""
    return get_metrics_summary()