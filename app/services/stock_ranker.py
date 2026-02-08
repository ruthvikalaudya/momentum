"""Stock ranking service - orchestrates scoring and ranking."""

import logging
from datetime import date, timedelta
from typing import Sequence

from ..config import get_settings
from ..models import StockData, RankedStock
from ..core.scoring import calculate_components, calculate_total_score
from .confidence import calculate_confidence

logger = logging.getLogger(__name__)


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
    logger.info(f"Ranking {len(stocks)} stocks...")
    
    # Calculate scores for all stocks
    scored = []
    for i, stock in enumerate(stocks):
        components = calculate_components(stock)
        total = calculate_total_score(components)
        scored.append((stock, components, total))
        
        if (i + 1) % 50 == 0:
            logger.debug(f"Scored {i + 1}/{len(stocks)} stocks")
    
    # Sort by total score descending
    scored.sort(key=lambda x: x[2], reverse=True)
    logger.info(f"Sorted stocks by score. Top score: {scored[0][2]:.1f}, Bottom: {scored[-1][2]:.1f}")
    
    # Create RankedStock objects with proper ranks
    ranked = [
        RankedStock(
            data=stock,
            components=components,
            total_score=total,
            confidence=calculate_confidence(stock, components),
            rank=idx + 1,
            is_top=(idx + 1) <= settings.top_stocks_count,
            earnings_safe=_is_earnings_safe(stock, settings.earnings_exclusion_days),
        )
        for idx, (stock, components, total) in enumerate(scored)
    ]
    
    # Log top 5 stocks
    logger.info("Top 5 stocks:")
    for s in ranked[:5]:
        logger.info(f"  #{s.rank} {s.data.symbol}: {s.total_score:.1f} (conf: {s.confidence:.0f}%)")
    
    return ranked