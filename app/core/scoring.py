"""Main scoring orchestration - combines all component scores."""

from ..config import get_settings
from ..models import StockData, ScoreComponents
from .price_momentum import calculate_price_momentum
from .volume_momentum import calculate_volume_momentum
from .technical import calculate_technical_strength
from .breakout import calculate_breakout_score
from .stability import calculate_stability_score


def calculate_components(stock: StockData) -> ScoreComponents:
    """Calculate all score components for a stock."""
    return ScoreComponents(
        price_momentum=calculate_price_momentum(stock),
        volume_momentum=calculate_volume_momentum(stock),
        technical_strength=calculate_technical_strength(stock),
        breakout_score=calculate_breakout_score(stock),
        stability_score=calculate_stability_score(stock),
    )


def calculate_total_score(components: ScoreComponents) -> float:
    """Calculate weighted total score from components."""
    settings = get_settings()
    
    return (
        components.price_momentum * settings.weight_price +
        components.volume_momentum * settings.weight_volume +
        components.technical_strength * settings.weight_technical +
        components.breakout_score * settings.weight_breakout +
        components.stability_score * settings.weight_stability
    )