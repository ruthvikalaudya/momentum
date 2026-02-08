"""Volume momentum calculation - pure function."""

from ..config import get_settings
from ..models import StockData


def _cap_score(value: float, cap: float) -> float:
    """Cap a score value at maximum."""
    return min(max(value, 0), cap)


def _weekly_volume_ratio(stock: StockData, cap: float) -> float:
    """Calculate weekly volume ratio score."""
    if stock.avg_volume_90d <= 0:
        return 0.0
    weekly_daily_avg = stock.volume_1w / 5
    ratio = weekly_daily_avg / stock.avg_volume_90d
    return _cap_score((ratio - 1) * 10, cap) if ratio > 1 else 0.0


def _daily_volume_ratio(stock: StockData, cap: float) -> float:
    """Calculate daily volume ratio score."""
    if stock.avg_volume_90d <= 0:
        return 0.0
    ratio = stock.volume_1d / stock.avg_volume_90d
    return _cap_score((ratio - 1) * 10, cap) if ratio > 1 else 0.0


def _relative_volume_score(stock: StockData, cap: float) -> float:
    """Calculate relative volume score."""
    return _cap_score((stock.rel_volume - 1) * 10, cap) if stock.rel_volume > 1 else 0.0


def calculate_volume_momentum(stock: StockData) -> float:
    """Calculate volume momentum score from volume metrics."""
    settings = get_settings()
    cap = settings.volume_score_cap
    
    weekly = _weekly_volume_ratio(stock, cap) * 0.40
    daily = _daily_volume_ratio(stock, cap) * 0.30
    rel_vol = _relative_volume_score(stock, cap) * 0.30
    
    return weekly + daily + rel_vol