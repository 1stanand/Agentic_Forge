import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from forge.core.config import get_settings
from forge.core.db import get_cursor
from forge.core.job_runner import mark_stale_jobs_failed
from forge.api.routes import auth, chat, generate, settings, admin

# Configure logging
config = get_settings()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Forge Agentic",
    version="1.0.0",
    description="AI-powered ATDD feature file generation platform"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Forge server starting...")

    # Mark stale jobs as failed (older than 1 hour)
    try:
        mark_stale_jobs_failed(age_seconds=3600)
        logger.info("Stale jobs marked as failed")
    except Exception as e:
        logger.error(f"Error marking stale jobs: {e}")

    logger.info("Forge server started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Forge server shutting down...")


# Health check BEFORE routes/mounts (so it's not caught by static mount)
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "Forge Agentic"}


# Register API routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(generate.router)
app.include_router(settings.router)
app.include_router(admin.router)


# Mount static files for frontend LAST (catches everything else)
static_path = Path(__file__).parent.parent.parent / "static"
if static_path.exists():
    app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")
    logger.info(f"Static files mounted from {static_path}")
else:
    logger.warning(f"Static files path does not exist: {static_path}")


logger.info("FastAPI app initialized with auth router")
