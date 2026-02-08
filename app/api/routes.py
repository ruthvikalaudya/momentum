"""API routes - FastAPI endpoints."""

import logging
from pathlib import Path
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..config import get_settings
from ..services import parse_csv_file, rank_stocks, calculate_analytics, get_market_overview

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# In-memory storage for current session
_current_stocks: list = []
_current_stock_data: list = []  # Raw StockData for market overview
_current_analytics = None
_current_market_data: list = []


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page."""
    global _current_market_data
    logger.info("Rendering home page")
    settings = get_settings()
    
    # Always fetch fresh market data on home page load
    logger.info("Fetching market overview...")
    _current_market_data = get_market_overview()
    logger.info(f"Fetched {len(_current_market_data)} market ETFs")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "settings": settings,
        "stocks": _current_stocks,
        "analytics": _current_analytics,
        "market_data": _current_market_data,
    })


@router.post("/upload", response_class=HTMLResponse)
async def upload_csv(request: Request, file: UploadFile = File(...)):
    """Handle CSV file upload and process stocks."""
    global _current_stocks, _current_analytics
    settings = get_settings()
    
    logger.info(f"Received file upload: {file.filename}")
    
    # Validate file size
    content = await file.read()
    file_size_kb = len(content) / 1024
    logger.info(f"File size: {file_size_kb:.1f} KB")
    
    max_size = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_size:
        logger.warning(f"File too large: {file_size_kb:.1f} KB > {settings.max_file_size_mb} MB")
        raise HTTPException(400, f"File too large. Max size: {settings.max_file_size_mb}MB")
    
    # Validate file type
    if not file.filename or not file.filename.endswith('.csv'):
        logger.warning(f"Invalid file type: {file.filename}")
        raise HTTPException(400, "Only CSV files are accepted")
    
    try:
        global _current_stock_data, _current_market_data
        
        # Parse and rank stocks
        logger.info("Parsing CSV data...")
        _current_stock_data = parse_csv_file(content)
        logger.info(f"Parsed {len(_current_stock_data)} stocks from CSV")
        
        logger.info("Calculating momentum scores...")
        _current_stocks = rank_stocks(_current_stock_data)
        logger.info(f"Ranked {len(_current_stocks)} stocks")
        
        logger.info("Calculating analytics...")
        _current_analytics = calculate_analytics(_current_stocks)
        logger.info(f"Analytics complete - Top 20 avg score: {_current_analytics.top_20_avg_score:.1f}")
        
        # Get market overview data
        logger.info("Getting market overview...")
        _current_market_data = get_market_overview(_current_stock_data)
        logger.info(f"Found {len(_current_market_data)} market ETFs")
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}", exc_info=True)
        raise HTTPException(400, f"Error processing CSV: {str(e)}")
    
    return templates.TemplateResponse("partials/results.html", {
        "request": request,
        "stocks": _current_stocks,
        "analytics": _current_analytics,
        "market_data": _current_market_data,
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
    top_n: int = 0,
):
    """Get filtered and sorted stock table."""
    settings = get_settings()
    filtered = _current_stocks
    
    logger.debug(f"Get stocks: sort_by={sort_by}, sort_dir={sort_dir}, industry={industry}, search={search}, top_n={top_n}")
    
    # Apply filters
    if industry:
        filtered = [s for s in filtered if s.data.industry == industry]
        logger.debug(f"Filtered by industry '{industry}': {len(filtered)} stocks")
    if sector:
        filtered = [s for s in filtered if s.data.sector == sector]
        logger.debug(f"Filtered by sector '{sector}': {len(filtered)} stocks")
    if search:
        search_lower = search.lower()
        filtered = [s for s in filtered if search_lower in s.data.symbol.lower() or search_lower in s.data.description.lower()]
        logger.debug(f"Filtered by search '{search}': {len(filtered)} stocks")
    if top_n > 0:
        filtered = [s for s in filtered if s.rank <= top_n]
        logger.debug(f"Filtered top {top_n}: {len(filtered)} stocks")
    
    # Apply sorting
    sort_map = {
        "rank": lambda s: s.rank,
        "symbol": lambda s: s.data.symbol.lower(),
        "price": lambda s: s.data.price,
        "market_cap": lambda s: s.data.market_cap,
        "score": lambda s: s.total_score,
        "confidence": lambda s: s.confidence,
        "price_mom": lambda s: s.components.price_momentum,
        "vol_mom": lambda s: s.components.volume_momentum,
        "industry": lambda s: s.data.industry.lower(),
        "perf_1w": lambda s: s.data.perf_1w,
    }
    
    if sort_by in sort_map:
        reverse = sort_dir == "desc"
        filtered = sorted(filtered, key=sort_map[sort_by], reverse=reverse)
        logger.debug(f"Sorted by {sort_by} {'desc' if reverse else 'asc'}")
    else:
        logger.warning(f"Unknown sort field: {sort_by}")
    
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