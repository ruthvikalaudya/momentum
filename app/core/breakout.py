"""Breakout score calculation - pure function."""

from ..config import get_settings
from ..models import StockData


def calculate_breakout_score(stock: StockData) -> float:
    """Calculate breakout potential score based on 52W proximity and volume."""
    settings = get_settings()
    
    if stock.high_52w <= 0:
        return 5.0
    
    proximity = (stock.price / stock.high_52w) * 100
    
    # Breakout imminent - near high with strong volume
    if proximity >= settings.high_52w_breakout_threshold:
        if stock.rel_volume >= settings.rel_vol_breakout_threshold:
            return 25.0
        return 15.0
    
    # Consolidating near highs
    if proximity >= settings.high_52w_near_threshold:
        if stock.rel_volume >= settings.rel_vol_near_threshold:
            return 15.0
        return 10.0
    
    # In uptrend but not near highs
    if proximity >= settings.high_52w_uptrend_threshold:
        return 10.0
    
    return 5.0