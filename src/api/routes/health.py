"""
Health check route.
"""

from fastapi import APIRouter

from src.core.config import get_settings
from src.schemas.workflow import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check application health and configuration status."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        llm_provider=settings.LLM_PROVIDER.value,
    )
