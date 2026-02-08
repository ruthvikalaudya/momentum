"""FastAPI application entry point."""

import logging
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .api import router

# Configure logging
def setup_logging():
    """Configure application logging."""
    settings = get_settings()
    
    # Set log level based on debug setting
    log_level = logging.DEBUG if settings.debug else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

logger = setup_logging()
settings = get_settings()

logger.info(f"Starting {settings.app_name} v{settings.app_version}")
logger.info(f"Debug mode: {settings.debug}")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Create static directory if it doesn't exist
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(exist_ok=True)
logger.info(f"Static directory: {static_dir}")

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routes
app.include_router(router)
logger.info("Routes registered successfully")


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Application shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)