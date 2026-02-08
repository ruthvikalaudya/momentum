"""Stability score calculation - pure function."""

from ..config import get_settings
from ..models import StockData


def _mcap_score(market_cap: float) -> float:
    """Calculate market cap score - larger caps get higher scores."""
    settings = get_settings()
    mcap_billions = market_cap / 1_000_000_000
    
    if mcap_billions >= settings.mcap_mega:
        return 20.0
    if mcap_billions >= settings.mcap_large:
        return 16.0
    if mcap_billions >= settings.mcap_mid_high:
        return 12.0
    if mcap_billions >= settings.mcap_mid:
        return 8.0
    if mcap_billions >= settings.mcap_small:
        return 5.0
    return 2.0


def _beta_score(beta: float) -> float:
    """Calculate beta score - moderate beta is ideal."""
    settings = get_settings()
    
    if 0.5 <= beta <= settings.beta_stable_max:
        return 15.0
    if beta <= settings.beta_moderate_max:
        return 12.0
    if beta <= settings.beta_high_max:
        return 8.0
    if beta <= settings.beta_very_high_max:
        return 4.0
    return 0.0


def calculate_stability_score(stock: StockData) -> float:
    """Calculate stability score from market cap and beta."""
    mcap = _mcap_score(stock.market_cap) * 0.60
    beta = _beta_score(stock.beta) * 0.40
    
    return mcap + beta