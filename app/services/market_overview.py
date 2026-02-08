"""Market overview service - fetches major index ETF data from Yahoo Finance."""

import logging
import json
from dataclasses import dataclass
from typing import Optional
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

# Major market ETFs to track
MARKET_ETFS = ["SPY", "QQQ", "IWM"]

ETF_NAMES = {
    "SPY": "S&P 500",
    "QQQ": "NASDAQ 100",
    "IWM": "Russell 2000",
}


@dataclass(frozen=True)
class MarketETF:
    """Market ETF data."""
    symbol: str
    name: str
    price: float
    change_1d: float  # Day change %
    change_1w: float  # Week change %
    change_1m: float  # Month change %
    change_3m: float  # 3 Month change %
    change_6m: float  # 6 Month change %
    change_ytd: float  # Year to date %
    change_1y: float  # 1 Year change %


def _fetch_yahoo_finance_data(symbol: str) -> Optional[dict]:
    """Fetch ETF data from Yahoo Finance API with multiple time periods."""
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Fetch current price and day change
        url_1d = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        req = urllib.request.Request(url_1d, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        result = data['chart']['result'][0]
        meta = result['meta']
        
        price = meta.get('regularMarketPrice', 0)
        prev_close = meta.get('chartPreviousClose', meta.get('previousClose', 0))
        change_1d = ((price - prev_close) / prev_close * 100) if prev_close else 0
        
        # Fetch 1 year data to calculate all periods
        url_1y = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1y"
        req = urllib.request.Request(url_1y, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data_1y = json.loads(response.read().decode('utf-8'))
        
        result_1y = data_1y['chart']['result'][0]
        closes = result_1y.get('indicators', {}).get('quote', [{}])[0].get('close', [])
        timestamps = result_1y.get('timestamp', [])
        
        # Filter out None values
        closes = [c for c in closes if c is not None]
        
        if len(closes) > 0:
            current = closes[-1]
            
            # Calculate returns for different periods
            # Approximate: 5 trading days = 1 week, 21 = 1 month, 63 = 3 months, 126 = 6 months, 252 = 1 year
            change_1w = ((current - closes[-6]) / closes[-6] * 100) if len(closes) >= 6 else 0
            change_1m = ((current - closes[-22]) / closes[-22] * 100) if len(closes) >= 22 else 0
            change_3m = ((current - closes[-64]) / closes[-64] * 100) if len(closes) >= 64 else 0
            change_6m = ((current - closes[-127]) / closes[-127] * 100) if len(closes) >= 127 else 0
            change_1y = ((current - closes[0]) / closes[0] * 100) if len(closes) > 0 else 0
            
            # Calculate YTD (from first trading day of the year)
            # Find the first close of the current year
            import datetime
            current_year = datetime.datetime.now().year
            ytd_start_price = closes[0]  # Default to start of data
            
            for i, ts in enumerate(timestamps):
                if ts:
                    dt = datetime.datetime.fromtimestamp(ts)
                    if dt.year == current_year:
                        ytd_start_price = closes[i] if i < len(closes) and closes[i] else closes[0]
                        break
            
            change_ytd = ((current - ytd_start_price) / ytd_start_price * 100) if ytd_start_price else 0
        else:
            change_1w = change_1m = change_3m = change_6m = change_ytd = change_1y = 0
        
        return {
            'price': price,
            'change_1d': change_1d,
            'change_1w': change_1w,
            'change_1m': change_1m,
            'change_3m': change_3m,
            'change_6m': change_6m,
            'change_ytd': change_ytd,
            'change_1y': change_1y,
        }
        
    except urllib.error.URLError as e:
        logger.error(f"Network error fetching {symbol}: {e}")
        return None
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Error parsing {symbol} data: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return None


def get_market_overview(stocks=None) -> list[MarketETF]:
    """Fetch market ETF data from Yahoo Finance.
    
    Args:
        stocks: Unused, kept for API compatibility
    """
    market_data = []
    
    for symbol in MARKET_ETFS:
        logger.info(f"Fetching {symbol} data from Yahoo Finance...")
        data = _fetch_yahoo_finance_data(symbol)
        
        if data:
            market_data.append(MarketETF(
                symbol=symbol,
                name=ETF_NAMES.get(symbol, symbol),
                price=data['price'],
                change_1d=data['change_1d'],
                change_1w=data['change_1w'],
                change_1m=data['change_1m'],
                change_3m=data['change_3m'],
                change_6m=data['change_6m'],
                change_ytd=data['change_ytd'],
                change_1y=data['change_1y'],
            ))
            logger.info(f"Found {symbol}: ${data['price']:.2f} (1D: {data['change_1d']:+.2f}%, YTD: {data['change_ytd']:+.2f}%)")
        else:
            logger.warning(f"Could not fetch {symbol} data")
    
    return market_data