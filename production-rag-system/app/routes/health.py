from fastapi import APIRouter

from app.models import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        dependencies={
            "api": "up",
            "vector_db": "stubbed",
            "cache": "in-memory",
            "llm": "stubbed",
        },
    )
