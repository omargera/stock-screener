"""
Unit tests for TechnicalAnalysisService
"""

import numpy as np
import pandas as pd

from services.technical_analysis_service import TechnicalAnalysisService


class TestTechnicalAnalysisService:
    """Test cases for TechnicalAnalysisService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.service = TechnicalAnalysisService()

    def test_calculate_all_indicators(self, sample_stock_data):
        """Test that all indicators are calculated"""
        result = self.service.calculate_all_indicators(sample_stock_data)

        # Check that original columns are preserved
        assert "Open" in result.columns
        assert "High" in result.columns
        assert "Low" in result.columns
        assert "Close" in result.columns
        assert "Volume" in result.columns

        # Check that new indicators are added
        expected_indicators = [
            "SMA_20",
            "SMA_50",
            "EMA_12",
            "EMA_26",
            "Volume_MA_20",
            "Volume_ROC",
            "OBV",
            "Price_Volatility",
            "ATR",
            "Resistance",
            "Support",
            "Pivot",
            "Price_Change_Pct",
            "Price_vs_SMA20",
            "Price_vs_SMA50",
        ]

        for indicator in expected_indicators:
            assert indicator in result.columns, f"Missing indicator: {indicator}"

    def test_moving_averages_calculation(self, data_builder):
        """Test moving averages calculation accuracy"""
        # Create data with known values
        data = data_builder("TEST", 100.0).with_basic_data(50).build()

        # Set specific close prices for testing
        close_prices = [100 + i for i in range(50)]  # Linear increase
        data["Close"] = close_prices

        result = self.service.calculate_all_indicators(data)

        # Test SMA_20 calculation (manual verification for last value)
        expected_sma_20 = np.mean(close_prices[-20:])
        actual_sma_20 = result["SMA_20"].iloc[-1]
        assert (
            abs(actual_sma_20 - expected_sma_20) < 0.01
        ), f"SMA_20 calculation incorrect: expected {expected_sma_20}, got {actual_sma_20}"

        # Test that SMA_20 values increase (given increasing prices)
        sma_values = result["SMA_20"].dropna()
        assert len(sma_values) >= 20, "SMA_20 should have at least 20 values"
        assert (
            sma_values.iloc[-1] > sma_values.iloc[0]
        ), "SMA_20 should increase with increasing prices"

    def test_volume_indicators(self, data_builder):
        """Test volume indicator calculations"""
        data = data_builder("TEST", 100.0).with_basic_data(30).build()

        # Set specific volume pattern
        volumes = [1000000 * (1 + 0.1 * i) for i in range(30)]  # Increasing volume
        data["Volume"] = volumes

        result = self.service.calculate_all_indicators(data)

        # Test Volume_MA_20
        expected_vol_ma = np.mean(volumes[-20:])
        actual_vol_ma = result["Volume_MA_20"].iloc[-1]
        assert (
            abs(actual_vol_ma - expected_vol_ma) < 1000
        ), f"Volume MA calculation incorrect: expected {expected_vol_ma}, got {actual_vol_ma}"

        # Test Volume_ROC
        volume_roc = result["Volume_ROC"].iloc[-1]
        expected_roc = (volumes[-1] - volumes[-2]) / volumes[-2]
        assert abs(volume_roc - expected_roc) < 0.01, "Volume ROC calculation incorrect"

        # Test OBV (should increase with increasing prices and volume)
        obv_values = result["OBV"].dropna()
        assert len(obv_values) > 0, "OBV should have values"
        assert (
            obv_values.iloc[-1] > obv_values.iloc[0]
        ), "OBV should increase with rising prices"

    def test_support_resistance_calculation(self, data_builder):
        """Test support and resistance level calculations"""
        data = data_builder("TEST", 100.0).with_basic_data(30).build()

        # Create clear support and resistance levels
        for i in range(len(data)):
            data.iloc[i, data.columns.get_loc("High")] = 110.0  # Resistance at 110
            data.iloc[i, data.columns.get_loc("Low")] = 90.0  # Support at 90

        result = self.service.calculate_all_indicators(data)

        # Test resistance calculation
        resistance = result["Resistance"].iloc[-1]
        assert resistance == 110.0, f"Resistance should be 110.0, got {resistance}"

        # Test support calculation
        support = result["Support"].iloc[-1]
        assert support == 90.0, f"Support should be 90.0, got {support}"

    def test_volatility_measures(self, sample_stock_data):
        """Test volatility calculations"""
        result = self.service.calculate_all_indicators(sample_stock_data)

        # Test Price Volatility
        volatility = result["Price_Volatility"].dropna()
        assert len(volatility) > 0, "Price volatility should have values"
        assert all(v >= 0 for v in volatility), "Volatility should be non-negative"

        # Test ATR
        atr = result["ATR"].dropna()
        assert len(atr) > 0, "ATR should have values"
        assert all(a >= 0 for a in atr), "ATR should be non-negative"

    def test_price_change_calculations(self, data_builder):
        """Test price change percentage calculations"""
        data = data_builder("TEST", 100.0).with_basic_data(25).build()

        # Set specific price pattern
        close_prices = [100, 102, 104, 103, 105]  # Known price changes
        data["Close"][:5] = close_prices

        result = self.service.calculate_all_indicators(data)

        # Test Price_Change_Pct calculation
        expected_changes = [
            np.nan,  # First value
            0.02,  # (102-100)/100 = 2%
            (104 - 102) / 102,  # ~1.96%
            (103 - 104) / 104,  # ~-0.96%
            (105 - 103) / 103,  # ~1.94%
        ]

        for i in range(1, 5):  # Skip first NaN value
            actual = result["Price_Change_Pct"].iloc[i]
            expected = expected_changes[i]
            assert (
                abs(actual - expected) < 0.001
            ), f"Price change calculation incorrect at index {i}: expected {expected}, got {actual}"

    def test_get_latest_indicators(self, sample_stock_data):
        """Test retrieving latest indicator values"""
        enhanced_data = self.service.calculate_all_indicators(sample_stock_data)
        indicators = self.service.get_latest_indicators(enhanced_data)

        # Check that all expected indicators are present
        expected_keys = [
            "sma_20",
            "sma_50",
            "volume_ma_20",
            "price_volatility",
            "resistance",
            "support",
            "atr",
            "obv",
            "price_change_pct",
            "price_vs_sma20",
            "price_vs_sma50",
        ]

        for key in expected_keys:
            assert key in indicators, f"Missing indicator in latest values: {key}"

        # Check that values are reasonable
        assert indicators["sma_20"] > 0, "SMA_20 should be positive"
        assert indicators["volume_ma_20"] > 0, "Volume MA should be positive"
        assert (
            indicators["resistance"] >= indicators["support"]
        ), "Resistance should be >= support"

    def test_empty_data_handling(self):
        """Test handling of empty data"""
        empty_data = pd.DataFrame()
        indicators = self.service.get_latest_indicators(empty_data)

        assert indicators == {}, "Should return empty dict for empty data"

    def test_insufficient_data_handling(self, data_builder):
        """Test handling of insufficient data"""
        # Create data with only 5 days (insufficient for most indicators)
        data = data_builder("TEST", 100.0).with_basic_data(5).build()

        result = self.service.calculate_all_indicators(data)

        # SMA_20 should be NaN for insufficient data
        sma_20_values = result["SMA_20"].dropna()
        assert len(sma_20_values) == 0, "SMA_20 should be NaN with insufficient data"

        # But basic calculations should still work
        assert "Price_Change_Pct" in result.columns
        price_changes = result["Price_Change_Pct"].dropna()
        assert len(price_changes) == 4, "Should have 4 price change values for 5 days"

    def test_data_integrity(self, sample_stock_data):
        """Test that original data is not modified"""
        original_data = sample_stock_data.copy()

        # Calculate indicators
        result = self.service.calculate_all_indicators(sample_stock_data)

        # Original data should be unchanged
        pd.testing.assert_frame_equal(sample_stock_data, original_data)

        # Result should have more columns
        assert len(result.columns) > len(original_data.columns)

    def test_obv_calculation_logic(self, data_builder):
        """Test OBV calculation with known price/volume patterns"""
        data = data_builder("TEST", 100.0).with_basic_data(10).build()

        # Set up known pattern: alternating up/down days
        close_prices = [100, 102, 101, 103, 102, 104, 103, 105, 104, 106]
        volumes = [1000000] * 10

        data["Close"] = close_prices
        data["Volume"] = volumes

        result = self.service.calculate_all_indicators(data)
        obv = result["OBV"].values

        # Manual OBV calculation verification
        expected_obv = [0]  # Start at 0
        for i in range(1, len(close_prices)):
            if close_prices[i] > close_prices[i - 1]:
                expected_obv.append(expected_obv[-1] + volumes[i])
            elif close_prices[i] < close_prices[i - 1]:
                expected_obv.append(expected_obv[-1] - volumes[i])
            else:
                expected_obv.append(expected_obv[-1])

        for i in range(len(expected_obv)):
            assert (
                abs(obv[i] - expected_obv[i]) < 1
            ), f"OBV calculation incorrect at index {i}: expected {expected_obv[i]}, got {obv[i]}"

    def test_atr_calculation(self, data_builder):
        """Test ATR calculation with known OHLC data"""
        data = data_builder("TEST", 100.0).with_basic_data(20).build()

        # Set up known OHLC pattern
        for i in range(len(data)):
            data.iloc[i, data.columns.get_loc("High")] = 105.0
            data.iloc[i, data.columns.get_loc("Low")] = 95.0
            data.iloc[i, data.columns.get_loc("Close")] = 100.0
            data.iloc[i, data.columns.get_loc("Open")] = 100.0

        result = self.service.calculate_all_indicators(data)
        atr = result["ATR"].dropna()

        # With consistent 10-point range, ATR should be around 10
        assert len(atr) > 0, "ATR should have values"
        assert all(
            8 <= a <= 12 for a in atr
        ), f"ATR values should be around 10, got {list(atr)}"

    def test_performance_with_large_dataset(self, performance_timer):
        """Test performance with larger dataset"""
        from tests.utils.test_data_generator import StockDataGenerator

        # Generate large dataset
        generator = StockDataGenerator("TEST", 100.0)
        large_data = generator.generate_basic_data(1000)  # 1000 days

        performance_timer.start()
        result = self.service.calculate_all_indicators(large_data)
        performance_timer.stop()

        # Should complete in reasonable time (under 1 second)
        assert (
            performance_timer.elapsed < 1.0
        ), f"Calculation took too long: {performance_timer.elapsed} seconds"

        # Should have all indicators
        assert len(result) == 1000, "Should preserve all data points"
        assert len(result.columns) > 10, "Should have added indicators"
