"""Confidence score calculation - measures signal alignment."""

from ..models import StockData, ScoreComponents


def calculate_confidence(stock: StockData, components: ScoreComponents = None) -> float:
    """Calculate confidence score based on multiple signal alignment.
    
    Args:
        stock: Stock data
        components: Optional score components (if available) to include momentum strength
    """
    score = 0.0
    
    # Price above SMA50
    if stock.sma_50 > 0 and stock.price > stock.sma_50:
        score += 15.0
    
    # Price above SMA200
    if stock.sma_200 > 0 and stock.price > stock.sma_200:
        score += 10.0
    
    # Near 52-week high (>90%)
    if stock.high_52w > 0 and (stock.price / stock.high_52w) > 0.90:
        score += 10.0
    
    # Near All-Time High (>80%) - major confidence boost
    if stock.high_all_time > 0 and stock.high_all_time >= stock.price:
        ath_proximity = stock.price / stock.high_all_time
        if ath_proximity >= 0.95:
            score += 20.0  # At or very near ATH - highest confidence
        elif ath_proximity >= 0.85:
            score += 15.0  # Within 15% of ATH
        elif ath_proximity >= 0.70:
            score += 10.0  # Within 30% of ATH
        elif ath_proximity >= 0.50:
            score += 5.0   # Within 50% of ATH
        # Below 50% of ATH = no confidence points
    elif stock.high_all_time > 0 and stock.price > stock.high_all_time:
        # Making new ATH - maximum confidence!
        score += 20.0
    
    # Volume confirmation (rel_vol > 1.2)
    if stock.rel_volume > 1.2:
        score += 10.0
    
    # All timeframes positive momentum
    if all([stock.perf_1w > 0, stock.perf_1m > 0, stock.perf_3m > 0, stock.perf_6m > 0]):
        score += 15.0
    
    # Low volatility (<5%)
    if stock.volatility_1m < 5:
        score += 5.0
    
    # Momentum score contribution (if available)
    if components is not None:
        total_momentum = components.price_momentum + components.volume_momentum
        # Scale: max momentum ~60 (35+25), normalize to 15 points max
        momentum_contribution = min((total_momentum / 60) * 15, 15.0)
        score += momentum_contribution
    
    return min(score, 100.0)