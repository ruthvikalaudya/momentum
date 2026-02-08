"""Confidence score calculation - measures signal alignment."""

from ..models import StockData


def calculate_confidence(stock: StockData) -> float:
    """Calculate confidence score based on multiple signal alignment."""
    score = 0.0
    
    # Price above SMA50
    if stock.sma_50 > 0 and stock.price > stock.sma_50:
        score += 20.0
    
    # Price above SMA200
    if stock.sma_200 > 0 and stock.price > stock.sma_200:
        score += 15.0
    
    # Near 52-week high (>90%)
    if stock.high_52w > 0 and (stock.price / stock.high_52w) > 0.90:
        score += 15.0
    
    # Volume confirmation (rel_vol > 1.2)
    if stock.rel_volume > 1.2:
        score += 20.0
    
    # All timeframes positive momentum
    if all([stock.perf_1w > 0, stock.perf_1m > 0, stock.perf_3m > 0, stock.perf_6m > 0]):
        score += 20.0
    
    # Low volatility (<5%)
    if stock.volatility_1m < 5:
        score += 10.0
    
    return min(score, 100.0)