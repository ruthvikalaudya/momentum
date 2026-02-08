"""API routes - FastAPI endpoints."""

from pathlib import Path
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..config import get_settings
from ..services import parse_csv_file, rank_stocks, calculate_analytics

router = APIRouter()
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# In-memory storage for current session
_current_stocks: list = []
_current_analytics = None


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page."""
    settings = get_settings()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "settings": settings,
        "stocks": _current_stocks,
        "analytics": _current_analytics,
    })


@router.post("/upload", response_class=HTMLResponse)
async def upload_csv(request: Request, file: UploadFile = File(...)):
    """Handle CSV file upload and process stocks."""
    global _current_stocks, _current_analytics
    settings = get_settings()
    
    # Validate file size
    content = await file.read()
    max_size = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(400, f"File too large. Max size: {settings.max_file_size_mb}MB")
    
    # Validate file type
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files are accepted")
    
    try:
        # Parse and rank stocks
        stock_data = parse_csv_file(content)
        _current_stocks = rank_stocks(stock_data)
        _current_analytics = calculate_analytics(_current_stocks)
    except Exception as e:
        raise HTTPException(400, f"Error processing CSV: {str(e)}")
    
    return templates.TemplateResponse("partials/results.html", {
        "request": request,
        "stocks": _current_stocks,
        "analytics": _current_analytics,
        "settings": settings,
    })


@router.get("/stocks", response_class=HTMLResponse)
async def get_stocks(
    request: Request,
    sort_by: str = "rank",
    sort_dir: str = "asc",
    industry: str = "",
    sector: str = "",
    search: str = "",
    top_only: bool = False,
):
    """Get filtered and sorted stock table."""
    settings = get_settings()
    filtered = _current_stocks
    
    # Apply filters
    if industry:
        filtered = [s for s in filtered if s.data.industry == industry]
    if sector:
        filtered = [s for s in filtered if s.data.sector == sector]
    if search:
        search_lower = search.lower()
        filtered = [s for s in filtered if search_lower in s.data.symbol.lower() or search_lower in s.data.description.lower()]
    if top_only:
        filtered = [s for s in filtered if s.is_top]
    
    # Apply sorting
    sort_map = {
        "rank": lambda s: s.rank,
        "symbol": lambda s: s.data.symbol,
        "score": lambda s: s.total_score,
        "confidence": lambda s: s.confidence,
        "price_mom": lambda s: s.components.price_momentum,
        "vol_mom": lambda s: s.components.volume_momentum,
        "industry": lambda s: s.data.industry,
        "perf_1w": lambda s: s.data.perf_1w,
    }
    
    if sort_by in sort_map:
        reverse = sort_dir == "desc"
        filtered = sorted(filtered, key=sort_map[sort_by], reverse=reverse)
    
    return templates.TemplateResponse("partials/stock_table.html", {
        "request": request,
        "stocks": filtered,
        "settings": settings,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
    })


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": get_settings().app_version}