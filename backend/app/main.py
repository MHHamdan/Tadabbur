"""
Tadabbur-AI FastAPI Application

RAG-grounded Quranic knowledge platform with story connections.
"""
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes import quran, stories, rag, health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan handler.
    Runs on startup and shutdown.
    """
    # Startup
    print(f"Starting {settings.app_name}...")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")

    yield

    # Shutdown
    print(f"Shutting down {settings.app_name}...")


app = FastAPI(
    title=settings.app_name,
    description="RAG-grounded Quranic knowledge platform with story connections",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred",
        },
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(quran.router, prefix="/api/v1/quran", tags=["Quran"])
app.include_router(stories.router, prefix="/api/v1/stories", tags=["Stories"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs" if settings.debug else "disabled",
    }
