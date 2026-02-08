"""Stock ranking service - orchestrates scoring and ranking."""

from datetime import date, timedelta
from typing import Sequence

from ..config import get_settings
from ..models import StockData, RankedStock
from ..core.scoring import calculate_components, calculate_total_score
from .confidence import calculate_confidence


def _is_earnings_safe(stock: StockData, days: int) -> bool:
    """Check if stock is safe from earnings announcement."""
    if stock.earnings_date is None:
        return True
    today = date.today()
    delta = abs((stock.earnings_date - today).days)
    return delta > days


def _create_ranked_stock(stock: StockData, rank: int, top_count: int, earnings_days: int) -> RankedStock:
    """Create a RankedStock from StockData with all calculations."""
    components = calculate_components(stock)
    total = calculate_total_score(components)
    confidence = calculate_confidence(stock)
    earnings_safe = _is_earnings_safe(stock, earnings_days)
    
    return RankedStock(
        data=stock,
        components=components,
        total_score=total,
        confidence=confidence,
        rank=rank,
        is_top=rank <= top_count,
        earnings_safe=earnings_safe,
    )


def rank_stocks(stocks: Sequence[StockData]) -> list[RankedStock]:
    """Score and rank all stocks, returning sorted list."""
    settings = get_settings()
    
    # Calculate scores for all stocks
    scored = []
    for stock in stocks:
        components = calculate_components(stock)
        total = calculate_total_score(components)
        scored.append((stock, components, total))
    
    # Sort by total score descending
    scored.sort(key=lambda x: x[2], reverse=True)
    
    # Create RankedStock objects with proper ranks
    return [
        RankedStock(
            data=stock,
            components=components,
            total_score=total,
            confidence=calculate_confidence(stock),
            rank=idx + 1,
            is_top=(idx + 1) <= settings.top_stocks_count,
            earnings_safe=_is_earnings_safe(stock, settings.earnings_exclusion_days),
        )
        for idx, (stock, components, total) in enumerate(scored)
    ]