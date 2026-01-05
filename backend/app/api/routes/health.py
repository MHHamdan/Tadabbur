"""
Health check endpoints for service monitoring.

SECURITY NOTES:
- /health is public (load balancer health checks)
- /ready is public (Kubernetes readiness probes)
- /health/detailed requires authentication in production
- /health/data requires authentication in production
- /health/rag requires authentication in production
- /metrics requires authentication in production
"""
from datetime import datetime
from functools import wraps
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import text, func, select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import os

from app.db.database import get_async_session
from app.core.config import settings
from app.core.observability import metrics

router = APIRouter()


# Environment detection
def is_production() -> bool:
    """Check if running in production environment."""
    env = os.getenv("ENVIRONMENT", os.getenv("ENV", "development"))
    return env.lower() in ("production", "prod")


def get_metrics_secret() -> Optional[str]:
    """
    Get metrics endpoint secret from environment.

    SECURITY: This value should NEVER be logged or included in error messages.
    """
    return os.getenv("METRICS_SECRET")


def _safe_secret_check(provided: Optional[str], expected: Optional[str]) -> bool:
    """
    Constant-time comparison of secrets to prevent timing attacks.

    SECURITY: Never log either value.
    """
    import hmac
    if not expected or not provided:
        return False
    # Use constant-time comparison
    return hmac.compare_digest(provided.encode(), expected.encode())


def _check_production_auth(request: Request) -> None:
    """
    Check production authentication for protected endpoints.

    SECURITY NOTES:
    - Uses constant-time comparison to prevent timing attacks
    - Error messages don't reveal whether secret is configured or incorrect
    - Secret values are NEVER logged

    Raises:
        HTTPException: 503 if endpoint disabled, 403 if auth fails
    """
    if not is_production():
        return  # No auth needed in development

    secret = get_metrics_secret()
    if not secret:
        # Endpoint disabled when secret not configured
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Endpoint not available"
        )

    header_secret = request.headers.get("X-Metrics-Secret")
    if not _safe_secret_check(header_secret, secret):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )


def require_metrics_auth(func):
    """
    Decorator to require authentication for sensitive endpoints in production.

    In development: No authentication required
    In production: Requires X-Metrics-Secret header or METRICS_SECRET env var
    """
    @wraps(func)
    async def wrapper(*args, request: Request = None, **kwargs):
        if not is_production():
            return await func(*args, **kwargs)

        # SECURITY: Check secret with constant-time comparison
        secret = get_metrics_secret()
        if not secret:
            # Endpoint disabled when secret not configured
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Endpoint not available"  # Don't reveal why
            )

        header_secret = request.headers.get("X-Metrics-Secret") if request else None
        if not _safe_secret_check(header_secret, secret):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"  # Don't reveal if secret exists or is wrong
            )

        return await func(*args, **kwargs)

    return wrapper


# ============================================================================
# PUBLIC ENDPOINTS (always accessible)
# ============================================================================

@router.get("/health")
async def health_check():
    """
    Basic health check.

    PUBLIC: Used by load balancers and external monitoring.
    Returns minimal information.
    """
    return {"status": "healthy", "service": settings.app_name}


@router.get("/ready")
async def readiness_check(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Readiness check - verifies the service is ready to accept traffic.

    PUBLIC: Used by Kubernetes readiness probes.
    """
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "not_ready"}


# ============================================================================
# PROTECTED ENDPOINTS (gated in production)
# ============================================================================

@router.get("/health/detailed")
async def detailed_health_check(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Detailed health check for all dependencies.

    PROTECTED IN PRODUCTION: Reveals internal service details.
    Requires X-Metrics-Secret header in production.
    """
    # Gate in production - use centralized secure check
    _check_production_auth(request)

    health_status = {
        "status": "healthy",
        "environment": "production" if is_production() else "development",
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


@router.get("/metrics")
async def get_metrics(request: Request):
    """
    Get application metrics.

    PROTECTED IN PRODUCTION: Reveals operational data.
    Requires X-Metrics-Secret header in production.
    """
    # Gate in production - use centralized secure check
    _check_production_auth(request)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production" if is_production() else "development",
        "metrics": metrics.get_summary(),
    }


@router.get("/health/data")
async def data_health_check(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Check health of data stores.

    PROTECTED IN PRODUCTION: Reveals data counts and schema info.
    Requires X-Metrics-Secret header in production.
    """
    # Gate in production - use centralized secure check
    _check_production_auth(request)

    from app.models.quran import QuranVerse, Translation
    from app.models.tafseer import TafseerSource, TafseerChunk
    from app.models.story import Story, StorySegment
    from app.models.audit import AuditLog

    data_status = {
        "status": "healthy",
        "environment": "production" if is_production() else "development",
        "checks": {},
        "counts": {},
    }

    try:
        # Check verse count
        result = await session.execute(select(func.count()).select_from(QuranVerse))
        verse_count = result.scalar()
        data_status["counts"]["quran_verses"] = verse_count
        if verse_count == 6236:
            data_status["checks"]["quran_verses"] = {"status": "pass", "expected": 6236, "actual": verse_count}
        else:
            data_status["checks"]["quran_verses"] = {"status": "warn", "expected": 6236, "actual": verse_count}
            if verse_count == 0:
                data_status["status"] = "degraded"

        # Check tafseer sources
        result = await session.execute(select(func.count()).select_from(TafseerSource))
        source_count = result.scalar()
        data_status["counts"]["tafseer_sources"] = source_count
        data_status["checks"]["tafseer_sources"] = {
            "status": "pass" if source_count > 0 else "warn",
            "count": source_count
        }

        # Check tafseer chunks
        result = await session.execute(select(func.count()).select_from(TafseerChunk))
        chunk_count = result.scalar()
        data_status["counts"]["tafseer_chunks"] = chunk_count
        data_status["checks"]["tafseer_chunks"] = {
            "status": "pass" if chunk_count > 0 else "warn",
            "count": chunk_count
        }

        # Check stories
        result = await session.execute(select(func.count()).select_from(Story))
        story_count = result.scalar()
        data_status["counts"]["stories"] = story_count
        data_status["checks"]["stories"] = {
            "status": "pass" if story_count >= 25 else "warn",
            "count": story_count,
            "expected_min": 25
        }

        # Check translations
        result = await session.execute(select(func.count()).select_from(Translation))
        translation_count = result.scalar()
        data_status["counts"]["translations"] = translation_count

        # Check recent audit logs (system is logging)
        result = await session.execute(
            select(func.count()).select_from(AuditLog)
        )
        audit_count = result.scalar()
        data_status["counts"]["audit_logs"] = audit_count

    except Exception as e:
        data_status["status"] = "unhealthy"
        data_status["error"] = str(e)

    return data_status


@router.get("/health/rag")
async def rag_health_check(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Check RAG pipeline health.

    PROTECTED IN PRODUCTION: Reveals RAG configuration.
    Requires X-Metrics-Secret header in production.
    """
    # Gate in production - use centralized secure check
    _check_production_auth(request)

    rag_status = {
        "status": "healthy",
        "environment": "production" if is_production() else "development",
        "checks": {},
    }

    # Check Qdrant collection
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://{settings.qdrant_host}:{settings.qdrant_port}/collections/tafseer_chunks",
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                vector_count = data.get("result", {}).get("points_count", 0)
                rag_status["checks"]["qdrant_collection"] = {
                    "status": "pass" if vector_count > 0 else "warn",
                    "vector_count": vector_count
                }
            else:
                rag_status["checks"]["qdrant_collection"] = {
                    "status": "warn",
                    "message": "Collection not found - run ingestion first"
                }
    except Exception as e:
        rag_status["checks"]["qdrant_collection"] = {
            "status": "fail",
            "error": str(e)
        }
        rag_status["status"] = "degraded"

    # Check LLM API configuration (don't reveal key)
    if settings.anthropic_api_key:
        rag_status["checks"]["llm_api"] = {"status": "pass", "provider": "anthropic", "configured": True}
    else:
        rag_status["checks"]["llm_api"] = {
            "status": "warn",
            "message": "LLM API not configured"
        }
        rag_status["status"] = "degraded"

    return rag_status


# ============================================================================
# SECURITY INFO ENDPOINT (only in development)
# ============================================================================

@router.get("/health/security")
async def security_check(request: Request):
    """
    Security configuration check.

    ONLY AVAILABLE IN DEVELOPMENT.
    """
    if is_production():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )

    return {
        "environment": "development",
        "metrics_secret_configured": bool(get_metrics_secret()),
        "protected_endpoints": [
            "/health/detailed",
            "/health/data",
            "/health/rag",
            "/metrics",
        ],
        "public_endpoints": [
            "/health",
            "/ready",
        ],
        "note": "In production, protected endpoints require X-Metrics-Secret header"
    }
