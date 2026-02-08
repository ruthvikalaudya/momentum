"""Stock data models - immutable data structures."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class StockData:
    """Raw stock data from CSV - immutable."""
    
    symbol: str
    description: str
    sector: str
    industry: str
    price: float
    market_cap: float
    beta: float
    volume_1d: float
    volume_1w: float
    avg_volume_90d: float
    earnings_date: Optional[date]
    change_1d: float  # Day change %
    perf_1w: float
    perf_1m: float
    perf_3m: float
    perf_6m: float
    perf_ytd: float  # Year-to-date %
    perf_1y: float
    volatility_1m: float
    high_52w: float
    high_all_time: float
    sma_50: float
    sma_200: float
    rel_volume: float
    volume_change: float
    indexes: str = ""


@dataclass(frozen=True)
class ScoreComponents:
    """Individual score components - immutable."""
    
    price_momentum: float
    volume_momentum: float
    technical_strength: float
    breakout_score: float
    stability_score: float


@dataclass(frozen=True)
class RankedStock:
    """Stock with calculated scores - immutable."""
    
    data: StockData
    components: ScoreComponents
    total_score: float
    confidence: float
    rank: int
    is_top: bool
    earnings_safe: bool