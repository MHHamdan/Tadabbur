"""
Health check endpoints for service monitoring.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.db.database import get_async_session
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": settings.app_name}


@router.get("/health/detailed")
async def detailed_health_check(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Detailed health check for all dependencies.
    Returns status of each service component.
    """
    health_status = {
        "status": "healthy",
        "services": {}
    }

    # Check PostgreSQL
    try:
        await session.execute(text("SELECT 1"))
        health_status["services"]["postgres"] = {"status": "healthy"}
    except Exception as e:
        health_status["services"]["postgres"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"

    # Check Qdrant
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{settings.qdrant_host}:{settings.qdrant_port}/readiness",
                timeout=5.0
            )
            if response.status_code == 200:
                health_status["services"]["qdrant"] = {"status": "healthy"}
            else:
                health_status["services"]["qdrant"] = {
                    "status": "unhealthy",
                    "error": f"Status code: {response.status_code}"
                }
                health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["services"]["qdrant"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"

    # Check Redis
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        await r.close()
        health_status["services"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"

    return health_status


@router.get("/ready")
async def readiness_check(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Readiness check - verifies the service is ready to accept traffic.
    """
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "not_ready"}
