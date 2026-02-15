"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/api/health")
async def health_check():
    """
    Health check endpoint.

    Returns application status and version.
    """
    return {
        "status": "healthy",
        "version": "2.0.0-dev"
    }
