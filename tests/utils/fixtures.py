"""
Test fixtures and mock utilities for stock screener tests
"""

from typing import Optional
from unittest.mock import Mock

import pandas as pd
import pytest

from gateways.stock_data_gateway import StockDataGateway
from services.screener_service import ScreenerConfiguration
from tests.utils.test_data_generator import StockDataGenerator, generate_test_scenarios


@pytest.fixture
def sample_stock_data():
    """Generate sample stock data for testing"""
    generator = StockDataGenerator("TEST", 100.0)
    return generator.generate_basic_data(60)


@pytest.fixture
def test_scenarios():
    """Generate all test scenarios"""
    return generate_test_scenarios()


@pytest.fixture
def screener_config():
    """Standard screener configuration for testing"""
    return ScreenerConfiguration(
        period="3mo", volume_spike_threshold=2.0, breakout_threshold=0.02
    )


@pytest.fixture
def strict_screener_config():
    """Strict screener configuration for testing edge cases"""
    return ScreenerConfiguration(
        period="3mo",
        volume_spike_threshold=3.0,  # Higher threshold
        breakout_threshold=0.05,  # Higher threshold
    )


class MockStockDataGateway(StockDataGateway):
    """Mock stock data gateway for testing"""

    def __init__(self, test_data: Optional[dict[str, pd.DataFrame]] = None):
        self.test_data = test_data or generate_test_scenarios()
        self.fetch_count = 0
        self.last_symbol = None
        self.last_period = None

    def fetch_stock_data(
        self, symbol: str, period: str = "3mo"
    ) -> Optional[pd.DataFrame]:
        """
        Mock fetch that returns test data based on symbol

        Args:
            symbol (str): Stock symbol (maps to test scenario)
            period (str): Time period

        Returns:
            pd.DataFrame: Test data or None
        """
        self.fetch_count += 1
        self.last_symbol = symbol
        self.last_period = period

        # Map symbols to test scenarios
        symbol_mapping = {
            "TEST_RESISTANCE": "resistance_breakout",
            "TEST_MA": "ma_breakout",
            "TEST_VOLUME": "volume_spike",
            "TEST_NONE": "no_signal",
            "TEST_FALSE": "false_breakout",
            "TEST": "resistance_breakout",  # Default
        }

        scenario = symbol_mapping.get(symbol, "no_signal")
        return self.test_data.get(scenario)

    def test_connection(self) -> bool:
        """Mock connection test"""
        return True


@pytest.fixture
def mock_gateway():
    """Mock stock data gateway"""
    return MockStockDataGateway()


@pytest.fixture
def mock_failing_gateway():
    """Mock gateway that simulates failures"""
    gateway = Mock()
    gateway.fetch_stock_data.return_value = None
    gateway.test_connection.return_value = False
    return gateway


class TestDataBuilder:
    """Builder class for creating custom test data"""

    def __init__(self, symbol: str = "TEST", base_price: float = 100.0):
        self.generator = StockDataGenerator(symbol, base_price)
        self.data = None

    def with_basic_data(self, days: int = 60):
        """Add basic data"""
        self.data = self.generator.generate_basic_data(days)
        return self

    def with_resistance_at(self, level: float, from_day: int = 30, to_day: int = 50):
        """Add resistance level"""
        if self.data is None:
            self.with_basic_data()

        for i in range(from_day, min(to_day, len(self.data))):
            self.data.iloc[i, self.data.columns.get_loc("High")] = min(
                self.data.iloc[i]["High"], level
            )
        return self

    def with_breakout_on_day(
        self, day: int, price: float, volume_multiplier: float = 2.0
    ):
        """Add breakout on specific day"""
        if self.data is None:
            self.with_basic_data()

        if day < len(self.data):
            self.data.iloc[day, self.data.columns.get_loc("Close")] = price
            self.data.iloc[day, self.data.columns.get_loc("High")] = price * 1.01
            self.data.iloc[day, self.data.columns.get_loc("Volume")] = int(
                self.data.iloc[day]["Volume"] * volume_multiplier
            )
        return self

    def with_volume_spike_on_day(self, day: int, multiplier: float = 3.0):
        """Add volume spike on specific day"""
        if self.data is None:
            self.with_basic_data()

        if day < len(self.data):
            self.data.iloc[day, self.data.columns.get_loc("Volume")] = int(
                self.data.iloc[day]["Volume"] * multiplier
            )
        return self

    def build(self) -> pd.DataFrame:
        """Build and return the data"""
        if self.data is None:
            self.with_basic_data()
        return self.data


@pytest.fixture
def data_builder():
    """Test data builder fixture"""
    return TestDataBuilder


def create_expected_signals(
    breakout: bool = False,
    breakout_type: str = None,
    breakout_strength: float = 0.0,
    volume_spike: bool = False,
    volume_ratio: float = 0.0,
) -> dict:
    """
    Create expected signal results for testing

    Args:
        breakout (bool): Whether breakout signal expected
        breakout_type (str): Type of breakout
        breakout_strength (float): Breakout strength
        volume_spike (bool): Whether volume spike expected
        volume_ratio (float): Volume ratio

    Returns:
        dict: Expected signals structure
    """
    return {
        "breakout": {
            "signal": breakout,
            "type": breakout_type,
            "strength": breakout_strength,
        },
        "volume": {"signal": volume_spike, "ratio": volume_ratio},
    }


@pytest.fixture
def expected_signals():
    """Factory for creating expected signal results"""
    return create_expected_signals


# Performance testing utilities
class PerformanceTimer:
    """Simple performance timer for testing"""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        import time

        self.start_time = time.time()

    def stop(self):
        import time

        self.end_time = time.time()

    @property
    def elapsed(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


@pytest.fixture
def performance_timer():
    """Performance timer fixture"""
    return PerformanceTimer()


# Assertion helpers
def assert_signal_detected(result, signal_type: str = "any"):
    """Assert that a signal was detected"""
    if signal_type == "any":
        assert result.signals.has_any_signal, "Expected a signal to be detected"
    elif signal_type == "breakout":
        assert result.signals.breakout.signal, "Expected breakout signal to be detected"
    elif signal_type == "volume":
        assert result.signals.volume.signal, "Expected volume signal to be detected"


def assert_no_signals(result):
    """Assert that no signals were detected"""
    assert not result.signals.has_any_signal, "Expected no signals to be detected"


def assert_signal_strength(result, min_strength: float = 0.0):
    """Assert signal strength meets minimum threshold"""
    if result.signals.breakout.signal:
        assert (
            result.signals.breakout.strength >= min_strength
        ), f"Breakout strength {result.signals.breakout.strength} below minimum {min_strength}"


def assert_volume_ratio(result, min_ratio: float = 0.0):
    """Assert volume ratio meets minimum threshold"""
    if result.signals.volume.signal:
        assert (
            result.signals.volume.volume_ratio >= min_ratio
        ), f"Volume ratio {result.signals.volume.volume_ratio} below minimum {min_ratio}"


# Export assertion helpers
__all__ = [
    "assert_signal_detected",
    "assert_no_signals",
    "assert_signal_strength",
    "assert_volume_ratio",
]
