"""Technical strength calculation - pure function."""

from ..models import StockData


def _trend_score(stock: StockData) -> float:
    """Calculate trend score based on price vs moving averages."""
    score = 0.0
    
    if stock.sma_50 > 0:
        sma50_ratio = (stock.price / stock.sma_50) - 1
        score += min(sma50_ratio * 50, 25)
    
    if stock.sma_200 > 0:
        sma200_ratio = (stock.price / stock.sma_200) - 1
        score += min(sma200_ratio * 25, 25)
    
    return min(max(score, 0), 50)


def _proximity_52w(stock: StockData) -> float:
    """Calculate 52-week high proximity score."""
    if stock.high_52w <= 0:
        return 0.0
    return (stock.price / stock.high_52w) * 100


def _volatility_adjustment(volatility: float) -> float:
    """Lower volatility is better for stability."""
    if volatility < 3:
        return 15.0
    if volatility < 5:
        return 10.0
    if volatility < 8:
        return 5.0
    return 0.0


def calculate_technical_strength(stock: StockData) -> float:
    """Calculate technical strength score."""
    trend = _trend_score(stock) * 0.40
    proximity = _proximity_52w(stock) * 0.40
    volatility_adj = _volatility_adjustment(stock.volatility_1m) * 0.20
    
    return trend + proximity + volatility_adj