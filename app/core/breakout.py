"""Breakout score calculation - pure function."""

from ..config import get_settings
from ..models import StockData


def calculate_breakout_score(stock: StockData) -> float:
    """Calculate breakout potential score based on 52W proximity, ATH proximity, and volume.
    
    This score heavily rewards stocks trading near their all-time highs.
    Stocks far from ATH are penalized significantly.
    """
    settings = get_settings()
    
    # Calculate 52-week high proximity
    if stock.high_52w <= 0:
        proximity_52w = 50.0
    else:
        proximity_52w = (stock.price / stock.high_52w) * 100
    
    # Calculate all-time high proximity (critical factor)
    if stock.high_all_time <= 0 or stock.high_all_time < stock.price:
        # If no ATH data or ATH is lower than current price (new ATH), use 52w high
        proximity_ath = proximity_52w
    else:
        proximity_ath = (stock.price / stock.high_all_time) * 100
    
    # Base score from 52-week high proximity
    if proximity_52w >= settings.high_52w_breakout_threshold:  # >= 95%
        # Near or at 52-week high
        if stock.rel_volume >= settings.rel_vol_breakout_threshold:
            base_score = 25.0  # Strong breakout signal
        else:
            base_score = 20.0
    elif proximity_52w >= settings.high_52w_near_threshold:  # >= 90%
        if stock.rel_volume >= settings.rel_vol_near_threshold:
            base_score = 18.0
        else:
            base_score = 15.0
    elif proximity_52w >= settings.high_52w_uptrend_threshold:  # >= 80%
        base_score = 12.0
    elif proximity_52w >= 70:
        base_score = 8.0
    else:
        base_score = 5.0
    
    # ATH Proximity Multiplier - critical for identifying true leaders
    # Stocks at or near ATH get a bonus, stocks far from ATH get heavily penalized
    if proximity_ath >= 95:
        # At or very near all-time high - these are the leaders!
        ath_multiplier = 1.3  # 30% bonus
    elif proximity_ath >= 85:
        # Within 15% of ATH - still good
        ath_multiplier = 1.1
    elif proximity_ath >= 70:
        # 15-30% below ATH - caution
        ath_multiplier = 0.9
    elif proximity_ath >= 50:
        # 30-50% below ATH - significant discount, likely weak
        ath_multiplier = 0.7
    elif proximity_ath >= 30:
        # 50-70% below ATH - deeply discounted, avoid for momentum
        ath_multiplier = 0.5
    else:
        # More than 70% below ATH - severely underperforming
        ath_multiplier = 0.3
    
    final_score = base_score * ath_multiplier
    
    # Cap at max score
    return min(final_score, 30.0)