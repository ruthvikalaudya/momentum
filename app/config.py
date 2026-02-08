"""Application configuration - all configurable values in one place."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    app_name: str = "Momentum Stock Ranker"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Scoring weights (must sum to 1.0)
    weight_price: float = 0.40
    weight_volume: float = 0.30
    weight_technical: float = 0.10
    weight_breakout: float = 0.10
    weight_stability: float = 0.10
    
    # Price momentum sub-weights
    price_weight_6m: float = 0.35
    price_weight_3m: float = 0.25
    price_weight_1m: float = 0.20
    price_weight_1y: float = 0.10
    price_weight_1w: float = 0.10
    
    # Volume scoring caps
    volume_score_cap: float = 25.0
    
    # Technical thresholds
    high_52w_breakout_threshold: float = 95.0
    high_52w_near_threshold: float = 90.0
    high_52w_uptrend_threshold: float = 85.0
    rel_vol_breakout_threshold: float = 1.5
    rel_vol_near_threshold: float = 1.2
    
    # Market cap tiers (in billions)
    mcap_mega: float = 100.0
    mcap_large: float = 50.0
    mcap_mid_high: float = 20.0
    mcap_mid: float = 10.0
    mcap_small: float = 2.0
    
    # Beta thresholds
    beta_stable_max: float = 1.0
    beta_moderate_max: float = 1.5
    beta_high_max: float = 2.0
    beta_very_high_max: float = 2.5
    
    # Display settings
    top_stocks_count: int = 20
    max_file_size_mb: int = 10
    
    # Earnings filter (days before/after to exclude)
    earnings_exclusion_days: int = 5
    
    class Config:
        env_file = ".env"
        env_prefix = "MOMENTUM_"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()