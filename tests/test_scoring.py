"""Tests for scoring modules."""
import pytest
from app.core.price_momentum import calculate_price_momentum
from app.core.volume_momentum import calculate_volume_momentum
from app.core.technical import calculate_technical_strength
from app.core.breakout import calculate_breakout_score
from app.core.stability import calculate_stability_score
from app.core.scoring import calculate_total_score, calculate_components
from app.models import StockData, ScoreComponents


@pytest.fixture
def sample_stock():
    """Create a sample stock for testing."""
    return StockData(
        symbol="AAPL",
        description="Apple Inc.",
        sector="Technology",
        industry="Consumer Electronics",
        price=185.50,
        market_cap=3000000000000,
        beta=1.15,
        volume_1d=75000000,
        volume_1w=80000000,
        avg_volume_90d=65000000,
        earnings_date=None,
        perf_1w=2.5,
        perf_1m=8.3,
        perf_3m=15.2,
        perf_6m=25.0,
        perf_1y=35.0,
        volatility_1m=2.5,
        high_52w=195.00,
        sma_50=180.25,
        sma_200=165.50,
        rel_volume=1.5,
        volume_change=10.0,
        indexes="S&P 500, NASDAQ 100"
    )


class TestPriceMomentum:
    """Test price momentum calculations."""
    
    def test_calculate_price_momentum(self, sample_stock):
        """Calculate price momentum for sample stock."""
        score = calculate_price_momentum(sample_stock)
        assert isinstance(score, float)
        assert score > 0  # Positive performance should give positive score


class TestVolumeMomentum:
    """Test volume momentum calculations."""
    
    def test_calculate_volume_momentum(self, sample_stock):
        """Calculate volume momentum for sample stock."""
        score = calculate_volume_momentum(sample_stock)
        assert isinstance(score, float)
        assert score > 0  # High relative volume should give positive score


class TestTechnical:
    """Test technical score calculations."""
    
    def test_calculate_technical(self, sample_stock):
        """Calculate technical score for sample stock."""
        score = calculate_technical_strength(sample_stock)
        assert isinstance(score, float)
        assert score > 0  # Price above SMAs should give positive score


class TestBreakout:
    """Test breakout score calculations."""
    
    def test_calculate_breakout(self, sample_stock):
        """Calculate breakout score for sample stock."""
        score = calculate_breakout_score(sample_stock)
        assert isinstance(score, float)
        assert score >= 0


class TestStability:
    """Test stability score calculations."""
    
    def test_calculate_stability(self, sample_stock):
        """Calculate stability score for sample stock."""
        score = calculate_stability_score(sample_stock)
        assert isinstance(score, float)
        assert score > 0  # Low volatility should give good stability score


class TestTotalScore:
    """Test total score calculation."""
    
    def test_calculate_components(self, sample_stock):
        """Calculate all components for sample stock."""
        components = calculate_components(sample_stock)
        assert isinstance(components, ScoreComponents)
        assert components.price_momentum > 0
        assert components.volume_momentum > 0
        assert components.technical_strength >= 0
        assert components.breakout_score >= 0
        assert components.stability_score >= 0
    
    def test_total_score_calculation(self):
        """Total score should apply weights."""
        components = ScoreComponents(
            price_momentum=30.0,
            volume_momentum=20.0,
            technical_strength=8.0,
            breakout_score=7.0,
            stability_score=6.0
        )
        total = calculate_total_score(components)
        assert isinstance(total, float)
        assert total > 0