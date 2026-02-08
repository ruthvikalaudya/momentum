"""Price momentum calculation - pure function."""

from ..config import get_settings
from ..models import StockData


def calculate_price_momentum(stock: StockData) -> float:
    """Calculate weighted price momentum score from performance metrics."""
    settings = get_settings()
    
    return (
        stock.perf_6m * settings.price_weight_6m +
        stock.perf_3m * settings.price_weight_3m +
        stock.perf_1m * settings.price_weight_1m +
        stock.perf_1y * settings.price_weight_1y +
        stock.perf_1w * settings.price_weight_1w
    )