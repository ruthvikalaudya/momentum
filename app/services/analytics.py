"""Analytics service - calculates insights and statistics."""

import logging
from dataclasses import dataclass
from collections import Counter
from typing import Sequence

from ..models import RankedStock

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IndustryStats:
    """Industry statistics."""
    name: str
    sector: str
    count: int
    avg_score: float
    top_stock: str


@dataclass(frozen=True)
class Analytics:
    """Portfolio analytics and insights."""
    total_stocks: int
    avg_score: float
    avg_confidence: float
    top_20_avg_score: float
    earnings_safe_count: int
    trending_industries: list[IndustryStats]
    sector_distribution: dict[str, int]
    top_movers: list[str]  # Highest 1-week performance (legacy)
    top_movers_1w: list[str]  # Highest 1-week performance
    top_movers_1m: list[str]  # Highest 1-month performance
    top_movers_6m: list[str]  # Highest 6-month performance
    volume_leaders: list[str]  # Highest relative volume
    breakout_candidates: list[str]  # Near 52-week high


def _get_trending_industries(stocks: Sequence[RankedStock], limit: int = 5) -> list[IndustryStats]:
    """Get top industries by average score."""
    industry_stocks: dict[str, list[RankedStock]] = {}
    
    for stock in stocks:
        industry = stock.data.industry
        if industry not in industry_stocks:
            industry_stocks[industry] = []
        industry_stocks[industry].append(stock)
    
    # Calculate avg score per industry
    industry_stats = []
    for name, ind_stocks in industry_stocks.items():
        if len(ind_stocks) < 2:  # Skip industries with only 1 stock
            continue
        avg = sum(s.total_score for s in ind_stocks) / len(ind_stocks)
        top = min(ind_stocks, key=lambda s: s.rank)
        # Get sector from top stock (all stocks in same industry typically have same sector)
        sector = top.data.sector
        industry_stats.append(IndustryStats(name, sector, len(ind_stocks), avg, top.data.symbol))
    
    # Sort by avg score
    industry_stats.sort(key=lambda x: x.avg_score, reverse=True)
    logger.debug(f"Found {len(industry_stats)} industries with 2+ stocks")
    return industry_stats[:limit]


def _get_sector_distribution(stocks: Sequence[RankedStock]) -> dict[str, int]:
    """Get stock count by sector."""
    return dict(Counter(s.data.sector for s in stocks))


def _get_top_movers_1w(stocks: Sequence[RankedStock], limit: int = 5) -> list[str]:
    """Get stocks with highest 1-week performance."""
    sorted_stocks = sorted(stocks, key=lambda s: s.data.perf_1w, reverse=True)
    movers = [s.data.symbol for s in sorted_stocks[:limit]]
    logger.debug(f"Top weekly movers: {movers}")
    return movers


def _get_top_movers_1m(stocks: Sequence[RankedStock], limit: int = 5) -> list[str]:
    """Get stocks with highest 1-month performance."""
    sorted_stocks = sorted(stocks, key=lambda s: s.data.perf_1m, reverse=True)
    movers = [s.data.symbol for s in sorted_stocks[:limit]]
    logger.debug(f"Top monthly movers: {movers}")
    return movers


def _get_top_movers_6m(stocks: Sequence[RankedStock], limit: int = 5) -> list[str]:
    """Get stocks with highest 6-month performance."""
    sorted_stocks = sorted(stocks, key=lambda s: s.data.perf_6m, reverse=True)
    movers = [s.data.symbol for s in sorted_stocks[:limit]]
    logger.debug(f"Top 6-month movers: {movers}")
    return movers


def _get_volume_leaders(stocks: Sequence[RankedStock], limit: int = 5) -> list[str]:
    """Get stocks with highest relative volume."""
    sorted_stocks = sorted(stocks, key=lambda s: s.data.rel_volume, reverse=True)
    leaders = [s.data.symbol for s in sorted_stocks[:limit]]
    logger.debug(f"Volume leaders: {leaders}")
    return leaders


def _get_breakout_candidates(stocks: Sequence[RankedStock], limit: int = 5) -> list[str]:
    """Get stocks nearest to 52-week high."""
    def proximity(s: RankedStock) -> float:
        if s.data.high_52w <= 0:
            return 0
        return s.data.price / s.data.high_52w
    
    sorted_stocks = sorted(stocks, key=proximity, reverse=True)
    candidates = [s.data.symbol for s in sorted_stocks[:limit]]
    logger.debug(f"Breakout candidates: {candidates}")
    return candidates


def calculate_analytics(stocks: Sequence[RankedStock]) -> Analytics:
    """Calculate comprehensive analytics for ranked stocks."""
    logger.info(f"Calculating analytics for {len(stocks)} stocks")
    
    if not stocks:
        logger.warning("No stocks to analyze")
        return Analytics(
            total_stocks=0, avg_score=0, avg_confidence=0, top_20_avg_score=0,
            earnings_safe_count=0, trending_industries=[], sector_distribution={},
            top_movers=[], top_movers_1w=[], top_movers_1m=[], top_movers_6m=[],
            volume_leaders=[], breakout_candidates=[]
        )
    
    top_20 = [s for s in stocks if s.is_top]
    top_movers_1w = _get_top_movers_1w(stocks)
    top_movers_1m = _get_top_movers_1m(stocks)
    top_movers_6m = _get_top_movers_6m(stocks)
    
    analytics = Analytics(
        total_stocks=len(stocks),
        avg_score=sum(s.total_score for s in stocks) / len(stocks),
        avg_confidence=sum(s.confidence for s in stocks) / len(stocks),
        top_20_avg_score=sum(s.total_score for s in top_20) / len(top_20) if top_20 else 0,
        earnings_safe_count=sum(1 for s in stocks if s.earnings_safe),
        trending_industries=_get_trending_industries(stocks),
        sector_distribution=_get_sector_distribution(stocks),
        top_movers=top_movers_1w,  # Legacy field
        top_movers_1w=top_movers_1w,
        top_movers_1m=top_movers_1m,
        top_movers_6m=top_movers_6m,
        volume_leaders=_get_volume_leaders(stocks),
        breakout_candidates=_get_breakout_candidates(stocks),
    )
    
    logger.info(f"Analytics: avg_score={analytics.avg_score:.1f}, top_20_avg={analytics.top_20_avg_score:.1f}")
    return analytics