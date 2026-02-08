"""FastAPI application entry point."""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .api import router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Create static directory if it doesn't exist
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)