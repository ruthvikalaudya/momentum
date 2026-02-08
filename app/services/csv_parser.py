"""CSV file parsing service - converts raw CSV to StockData models."""

import io
from datetime import datetime
from typing import Optional
import pandas as pd

from ..models import StockData


# Column name mappings - configurable
COLUMN_MAP = {
    "symbol": "Symbol",
    "description": "Description",
    "sector": "Sector",
    "industry": "Industry",
    "price": "Price",
    "market_cap": "Market capitalization",
    "beta": "Beta 1 year",
    "volume_1d": "Volume 1 day",
    "volume_1w": "Volume 1 week",
    "avg_volume_90d": "Average Volume 90 days",
    "earnings_date": "Upcoming earnings date",
    "perf_1w": "Performance % 1 week",
    "perf_1m": "Performance % 1 month",
    "perf_3m": "Performance % 3 months",
    "perf_6m": "Performance % 6 months",
    "perf_1y": "Performance % 1 year",
    "volatility_1m": "Volatility 1 month",
    "high_52w": "High 52 weeks",
    "sma_50": "Simple Moving Average (50) 1 day",
    "sma_200": "Simple Moving Average (200) 1 day",
    "rel_volume": "Relative Volume 1 day",
    "volume_change": "Volume Change % 1 day",
    "indexes": "Index",
}


def _safe_float(value, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def _parse_date(value) -> Optional[datetime]:
    """Parse date string to datetime."""
    if pd.isna(value) or not value:
        return None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


def _row_to_stock(row: pd.Series) -> StockData:
    """Convert a DataFrame row to StockData model."""
    return StockData(
        symbol=str(row.get(COLUMN_MAP["symbol"], "")),
        description=str(row.get(COLUMN_MAP["description"], "")),
        sector=str(row.get(COLUMN_MAP["sector"], "")),
        industry=str(row.get(COLUMN_MAP["industry"], "")),
        price=_safe_float(row.get(COLUMN_MAP["price"])),
        market_cap=_safe_float(row.get(COLUMN_MAP["market_cap"])),
        beta=_safe_float(row.get(COLUMN_MAP["beta"]), 1.0),
        volume_1d=_safe_float(row.get(COLUMN_MAP["volume_1d"])),
        volume_1w=_safe_float(row.get(COLUMN_MAP["volume_1w"])),
        avg_volume_90d=_safe_float(row.get(COLUMN_MAP["avg_volume_90d"])),
        earnings_date=_parse_date(row.get(COLUMN_MAP["earnings_date"])),
        perf_1w=_safe_float(row.get(COLUMN_MAP["perf_1w"])),
        perf_1m=_safe_float(row.get(COLUMN_MAP["perf_1m"])),
        perf_3m=_safe_float(row.get(COLUMN_MAP["perf_3m"])),
        perf_6m=_safe_float(row.get(COLUMN_MAP["perf_6m"])),
        perf_1y=_safe_float(row.get(COLUMN_MAP["perf_1y"])),
        volatility_1m=_safe_float(row.get(COLUMN_MAP["volatility_1m"])),
        high_52w=_safe_float(row.get(COLUMN_MAP["high_52w"])),
        sma_50=_safe_float(row.get(COLUMN_MAP["sma_50"])),
        sma_200=_safe_float(row.get(COLUMN_MAP["sma_200"])),
        rel_volume=_safe_float(row.get(COLUMN_MAP["rel_volume"]), 1.0),
        volume_change=_safe_float(row.get(COLUMN_MAP["volume_change"])),
        indexes=str(row.get(COLUMN_MAP["indexes"], "")),
    )


def parse_csv_file(content: bytes | str) -> list[StockData]:
    """Parse CSV content and return list of StockData objects."""
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    
    df = pd.read_csv(io.StringIO(content))
    return [_row_to_stock(row) for _, row in df.iterrows()]