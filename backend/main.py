"""
AgriNova AI — FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import register_exception_handlers

# Import all models so Base.metadata sees them
import app.models  # noqa: F401

# Import routers
from app.api.v1.auth import router as auth_router
from app.api.v1.farms import router as farms_router
from app.api.v1.knowledge import router as knowledge_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    # Startup: create tables (dev mode with SQLite)
    if settings.is_sqlite:
        await init_db()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Precision Agriculture Platform — from seed to harvest.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ──
register_exception_handlers(app)

# ── Routers ──
app.include_router(auth_router, prefix="/api/v1")
app.include_router(farms_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def health_check():
    """API health check endpoint."""
    return {
        "status": "success",
        "message": f"{settings.APP_NAME} API is running",
        "version": "1.0.0",
    }


@app.get("/api/v1/health", tags=["Health"])
async def api_health():
    """API v1 health check."""
    return {"status": "success", "message": "API v1 is healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
