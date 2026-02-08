# Momentum Stock Scorer

A modern web application for analyzing and ranking stocks based on multi-factor momentum scoring. Upload TradingView CSV exports and get instant momentum rankings with confidence scores.

## Features

- **Multi-Factor Scoring**: Combines 5 momentum dimensions:
  - Price Momentum (40%): Multi-timeframe returns (1W, 1M, 3M, 6M)
  - Volume Momentum (30%): Relative volume analysis with trend detection
  - Technical (10%): EMA positioning and beta analysis
  - Breakout (10%): 52-week range position and new high detection
  - Stability (10%): ATR-based volatility assessment

- **Confidence Scoring**: Each stock gets a confidence score based on:
  - Data completeness
  - Index membership (S&P 500, Russell 1000)
  - Market cap tier
  - Earnings timing safety

- **Interactive Dashboard**:
  - Real-time filtering and search
  - Industry breakdowns
  - Top movers identification
  - Breakout candidates
  - Mobile-responsive design

## Quick Start

```bash
# Navigate to the project
cd momentum

# Install dependencies
pip install -e .

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Open in browser
open http://localhost:8000
```

## Project Structure

```
momentum/
├── app/
│   ├── api/           # FastAPI routes
│   ├── core/          # Scoring algorithms (small, focused modules)
│   │   ├── price_momentum.py
│   │   ├── volume_momentum.py
│   │   ├── technical.py
│   │   ├── breakout.py
│   │   ├── stability.py
│   │   └── scoring.py
│   ├── models/        # Pydantic data models
│   ├── services/      # Business logic
│   │   ├── csv_parser.py
│   │   ├── confidence.py
│   │   ├── stock_ranker.py
│   │   └── analytics.py
│   ├── templates/     # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── components/
│   │   └── partials/
│   ├── config.py      # Configuration
│   └── main.py        # App entry point
├── tests/             # Pytest test suite
├── pyproject.toml     # Project config
└── README.md
```

## CSV Format

The app expects TradingView-style CSV exports with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Symbol | Stock ticker | AAPL |
| Description | Company name | Apple Inc. |
| Industry | Industry classification | Consumer Electronics |
| Market Capitalization | Market cap in USD | 3000000000000 |
| Price | Current price | 185.50 |
| Perf 1W | 1-week performance % | 2.5 |
| Perf 1M | 1-month performance % | 8.3 |
| Perf 3M | 3-month performance % | 15.2 |
| Perf 6M | 6-month performance % | 25.0 |
| Relative Volume | Current vs 30D avg | 1.5 |
| Relative Volume 1W | 1-week rel volume | 1.8 |
| Relative Volume 1M | 1-month rel volume | 1.3 |
| EMA (50) | 50-day EMA | 180.25 |
| EMA (200) | 200-day EMA | 165.50 |
| Beta 1Y | 1-year beta | 1.15 |
| ATR (14D) | 14-day ATR % | 2.5 |
| 52W High | 52-week high | 195.00 |
| 52W Low | 52-week low | 140.00 |
| Avg Volume 30D | 30-day avg volume | 75000000 |
| Indexes | Index membership | S&P 500, NASDAQ 100 |
| Earnings | Next earnings date | 2025-02-15 |

## Scoring Formula

### Price Momentum (40 points max)
```
Score = (1W × 0.15 + 1M × 0.25 + 3M × 0.30 + 6M × 0.30) × scaling
- Timeframe alignment bonus: +5 for 1W > 0 & 1M > 3M/3 & 3M > 6M/2
```

### Volume Momentum (30 points max)
```
Score = (RelVol × 10) + (RelVol1W × 8) + (RelVol1M × 5)
- Volume ratio bonus: +5 if 1W > 1M (increasing interest)
```

### Technical (10 points max)
```
- Price > EMA50: +3
- Price > EMA200: +3
- EMA50 > EMA200: +2 (golden cross)
- Beta in optimal range (0.8-1.5): +2
```

### Breakout (10 points max)
```
- Position in 52W range × 8
- New 52W high bonus: +2
```

### Stability (10 points max)
```
- Base: 10 - (ATR% / 2)
- Optimal range (2-8%): bonus applied
```

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Main dashboard |
| POST | /upload | Upload CSV file |
| GET | /stocks | Get filtered stocks (HTMX) |

## Tech Stack

- **Backend**: FastAPI, Pydantic
- **Frontend**: Jinja2, HTMX, Tailwind CSS
- **Testing**: Pytest

## License

MIT