"""
Pytest configuration and fixture registration
"""

# Import all fixtures from the fixtures module
from tests.utils.fixtures import (
    sample_stock_data,
    test_scenarios,
    screener_config,
    strict_screener_config,
    mock_gateway,
    mock_failing_gateway,
    data_builder,
    expected_signals,
    performance_timer,
    MockStockDataGateway,
    TestDataBuilder,
    PerformanceTimer,
    # Import assertion helpers too
    assert_signal_detected,
    assert_no_signals,
    assert_signal_strength,
    assert_volume_ratio,
)

# Register all fixtures by importing them
__all__ = [
    "sample_stock_data",
    "test_scenarios",
    "screener_config",
    "strict_screener_config",
    "mock_gateway",
    "mock_failing_gateway",
    "data_builder",
    "expected_signals",
    "performance_timer",
    "MockStockDataGateway",
    "TestDataBuilder",
    "PerformanceTimer",
    "assert_signal_detected",
    "assert_no_signals",
    "assert_signal_strength",
    "assert_volume_ratio",
]
