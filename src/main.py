"""
Multi-Agent Document Intelligence & CRM Automation Platform

FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import documents, health, rag, workflow
from src.core.config import get_settings
from src.core.logging import setup_logging

# ── Initialize Logging ──────────────────────────────────────────
setup_logging()

# ── Create FastAPI App ──────────────────────────────────────────
app = FastAPI(
    title="Multi-Agent Document Intelligence Platform",
    description=(
        "A production-grade multi-agent AI system that processes business documents "
        "(emails, PDFs, JSON) through an intelligent pipeline of specialized agents "
        "using LangGraph, LangChain, and RAG."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routes ─────────────────────────────────────────────
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(workflow.router)
app.include_router(rag.router)

# ── Serve Frontend Static Files ─────────────────────────────────
app.mount("/static", StaticFiles(directory="frontend"), name="frontend")


@app.get("/", include_in_schema=False)
async def root_redirect():
    """Redirect root to frontend."""
    return RedirectResponse(url="/static/index.html")


# ── Startup Event ───────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    settings = get_settings()
    settings.ensure_directories()
    print(
        f"\n{'='*60}\n"
        f"  Multi-Agent Document Intelligence Platform\n"
        f"  LLM Provider: {settings.LLM_PROVIDER.value}\n"
        f"  Docs: http://localhost:{settings.PORT}/docs\n"
        f"  Frontend: http://localhost:{settings.PORT}\n"
        f"{'='*60}\n"
    )


# ── Run with uvicorn ────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )
