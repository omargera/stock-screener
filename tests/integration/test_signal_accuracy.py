"""
Signal accuracy tests to ensure the screener identifies the right entry points
"""

import numpy as np

from services.screener_service import ScreenerConfiguration, StockScreenerService
from services.signal_detection_service import SignalDetectionService
from services.technical_analysis_service import TechnicalAnalysisService
from tests.utils.test_data_generator import StockDataGenerator


class TestSignalAccuracy:
    """Tests to verify signal detection accuracy for entry points"""

    def setup_method(self):
        """Set up test services"""
        self.config = ScreenerConfiguration(
            period="3mo", volume_spike_threshold=2.0, breakout_threshold=0.02
        )
        self.technical_service = TechnicalAnalysisService()
        self.signal_service = SignalDetectionService(
            volume_spike_threshold=2.0, breakout_threshold=0.02
        )

    def test_resistance_breakout_entry_point(self, data_builder):
        """Test identification of resistance breakout entry points"""
        # Create clear resistance breakout scenario
        data = (
            data_builder("TEST", 100.0)
            .with_basic_data(60)
            .with_resistance_at(110.0, 30, 55)  # Strong resistance at 110
            .with_breakout_on_day(56, 112.5, 3.0)  # Clear breakout with volume
            .build()
        )

        enhanced_data = self.technical_service.calculate_all_indicators(data)
        signals = self.signal_service.detect_all_signals(enhanced_data)

        # Should detect resistance breakout
        assert signals.breakout.signal, "Should detect resistance breakout"
        assert signals.breakout.signal_type.value == "Resistance Breakout"

        # Should have reasonable strength
        assert (
            signals.breakout.strength > 0.02
        ), "Breakout strength should be significant"
        assert (
            signals.breakout.strength < 0.10
        ), "Breakout strength should be reasonable"

        # Should have volume confirmation
        assert signals.volume.signal, "Should detect volume spike"
        assert (
            signals.volume.volume_ratio >= 2.5
        ), "Volume should be significantly elevated"

    def test_moving_average_breakout_entry_point(self, data_builder):
        """Test identification of moving average breakout entry points"""
        # Create MA breakout scenario with clear trend reversal
        data = data_builder("TEST", 100.0).with_basic_data(60).build()

        # Create downtrend then reversal
        for i in range(40):
            decline_factor = 1 - (i / 40) * 0.15  # 15% decline
            price = 100.0 * decline_factor
            data.iloc[i, data.columns.get_loc("Close")] = price

        # Consolidation period
        for i in range(40, 50):
            data.iloc[i, data.columns.get_loc("Close")] = 85.0 + np.random.uniform(
                -1, 1
            )

        # Clear breakout above SMA 20
        for i in range(50, 60):
            data.iloc[i, data.columns.get_loc("Close")] = 87.0 + (i - 50) * 0.5
            if i == 55:  # Breakout day
                data.iloc[i, data.columns.get_loc("Volume")] = int(
                    data.iloc[i]["Volume"] * 2.5
                )

        enhanced_data = self.technical_service.calculate_all_indicators(data)
        signals = self.signal_service.detect_all_signals(enhanced_data)

        # Should detect MA breakout
        assert signals.breakout.signal, "Should detect MA breakout"
        assert signals.breakout.signal_type.value == "MA Breakout"

        # Should confirm uptrend
        latest_sma20 = enhanced_data["SMA_20"].iloc[-1]
        latest_sma50 = enhanced_data["SMA_50"].iloc[-1]
        assert latest_sma20 > latest_sma50, "SMA 20 should be above SMA 50 for uptrend"

    def test_false_breakout_rejection(self, data_builder):
        """Test that false breakouts are properly rejected"""
        # Create false breakout scenario
        data = (
            data_builder("TEST", 100.0)
            .with_basic_data(60)
            .with_resistance_at(110.0, 30, 55)
            .build()
        )

        # Day 56: Brief spike above resistance but close below
        breakout_day = 56
        data.iloc[breakout_day, data.columns.get_loc("High")] = 112.0  # Spike above
        data.iloc[breakout_day, data.columns.get_loc("Close")] = 109.0  # Close below
        data.iloc[breakout_day, data.columns.get_loc("Volume")] = int(
            data.iloc[breakout_day]["Volume"] * 0.8  # Low volume
        )

        enhanced_data = self.technical_service.calculate_all_indicators(data)
        signals = self.signal_service.detect_all_signals(enhanced_data)

        # Should NOT detect breakout
        assert not signals.breakout.signal, "Should reject false breakout"

    def test_volume_confirmation_requirement(self, data_builder):
        """Test that volume confirmation is required for valid signals"""
        # Create price breakout without volume confirmation
        data = (
            data_builder("TEST", 100.0)
            .with_basic_data(60)
            .with_resistance_at(110.0, 30, 55)
            .build()
        )

        # Day 56: Price breaks resistance but volume is low
        breakout_day = 56
        data.iloc[breakout_day, data.columns.get_loc("Close")] = 112.0
        data.iloc[breakout_day, data.columns.get_loc("High")] = 113.0
        data.iloc[breakout_day, data.columns.get_loc("Volume")] = int(
            data.iloc[breakout_day]["Volume"] * 0.5  # Very low volume
        )

        enhanced_data = self.technical_service.calculate_all_indicators(data)
        signals = self.signal_service.detect_all_signals(enhanced_data)

        # Should NOT detect breakout without volume confirmation
        assert not signals.breakout.signal, "Should require volume confirmation"

    def test_multiple_timeframe_consistency(self):
        """Test signal consistency across different timeframes"""
        generator = StockDataGenerator("TEST", 100.0)

        # Generate same pattern at different scales
        short_data = generator.generate_resistance_breakout_scenario()

        # Test with different periods (simulate different timeframes)
        configs = [
            ScreenerConfiguration(
                period="1mo", volume_spike_threshold=2.0, breakout_threshold=0.02
            ),
            ScreenerConfiguration(
                period="3mo", volume_spike_threshold=2.0, breakout_threshold=0.02
            ),
        ]

        results = []
        for config in configs:
            service = SignalDetectionService(
                volume_spike_threshold=config.volume_spike_threshold,
                breakout_threshold=config.breakout_threshold,
            )
            enhanced_data = self.technical_service.calculate_all_indicators(short_data)
            signals = service.detect_all_signals(enhanced_data)
            results.append(signals)

        # Should detect signals consistently
        for i, signals in enumerate(results):
            assert signals.breakout.signal, f"Config {i} should detect breakout"
            assert signals.volume.signal, f"Config {i} should detect volume spike"

    def test_signal_timing_accuracy(self, data_builder):
        """Test that signals are detected at the right time"""
        data = data_builder("TEST", 100.0).with_basic_data(60).build()

        # Create resistance at day 40-50, breakout at day 55
        resistance_level = 110.0
        for i in range(30, 50):
            data.iloc[i, data.columns.get_loc("High")] = resistance_level
            data.iloc[i, data.columns.get_loc("Close")] = resistance_level - 2.0

        # No breakout at day 50 (should not signal)
        data.iloc[50, data.columns.get_loc("Close")] = resistance_level - 1.0

        # Clear breakout at day 55
        data.iloc[55, data.columns.get_loc("Close")] = resistance_level + 2.0
        data.iloc[55, data.columns.get_loc("High")] = resistance_level + 3.0
        data.iloc[55, data.columns.get_loc("Volume")] = int(
            data.iloc[55]["Volume"] * 3.0
        )

        # Test signal detection at different points
        enhanced_data = self.technical_service.calculate_all_indicators(data)

        # Truncate to day 50 (should not signal)
        early_data = enhanced_data.iloc[:51]  # Up to day 50
        early_signals = self.signal_service.detect_all_signals(early_data)
        assert not early_signals.breakout.signal, "Should not signal before breakout"

        # Full data (should signal)
        full_signals = self.signal_service.detect_all_signals(enhanced_data)
        assert full_signals.breakout.signal, "Should signal after breakout"

    def test_signal_strength_accuracy(self, data_builder):
        """Test that signal strength accurately reflects breakout magnitude"""
        # Test different breakout strengths
        test_cases = [
            (111.0, 0.009),  # ~1% breakout (weak)
            (115.0, 0.045),  # ~4.5% breakout (strong)
            (120.0, 0.091),  # ~9% breakout (very strong)
        ]

        for breakout_price, expected_strength in test_cases:
            data = (
                data_builder("TEST", 100.0)
                .with_basic_data(60)
                .with_resistance_at(110.0, 30, 55)
                .with_breakout_on_day(56, breakout_price, 2.5)
                .build()
            )

            enhanced_data = self.technical_service.calculate_all_indicators(data)
            signals = self.signal_service.detect_all_signals(enhanced_data)

            if signals.breakout.signal:
                actual_strength = signals.breakout.strength
                # Allow 1% tolerance for calculation differences
                assert abs(actual_strength - expected_strength) < 0.01, (
                    f"Strength calculation incorrect for {breakout_price}: "
                    f"expected ~{expected_strength:.3f}, got {actual_strength:.3f}"
                )

    def test_market_condition_detection(self, mock_gateway):
        """Test market condition detection accuracy"""
        service = StockScreenerService(self.config, mock_gateway)

        # Test different market scenarios
        test_scenarios = [
            # Bullish market (many signals)
            (["TEST_RESISTANCE", "TEST_MA", "TEST_VOLUME"], "bullish"),
            # Neutral market (few signals)
            (["TEST_NONE", "TEST_FALSE"], "bearish"),
            # Mixed market
            (["TEST_RESISTANCE", "TEST_NONE", "TEST_VOLUME", "TEST_FALSE"], "neutral"),
        ]

        for symbols, expected_condition_type in test_scenarios:
            analysis = service.analyze_market_conditions(symbols)

            # Verify condition makes sense
            signal_pct = analysis["signal_percentage"]
            condition = analysis["condition"]

            if expected_condition_type == "bullish":
                assert signal_pct >= 30 or condition in [
                    "bullish",
                    "very_bullish",
                ], f"Expected bullish market but got {condition} with {signal_pct}% signals"
            elif expected_condition_type == "bearish":
                assert signal_pct <= 20 or condition in [
                    "bearish",
                    "neutral",
                ], f"Expected bearish/neutral market but got {condition} with {signal_pct}% signals"

    def test_entry_point_risk_assessment(self, data_builder):
        """Test entry point quality assessment"""
        # Create high-quality entry point
        good_entry_data = (
            data_builder("TEST", 100.0)
            .with_basic_data(60)
            .with_resistance_at(110.0, 30, 55)
            .with_breakout_on_day(56, 113.0, 4.0)  # Strong breakout with high volume
            .build()
        )

        enhanced_data = self.technical_service.calculate_all_indicators(good_entry_data)
        signals = self.signal_service.detect_all_signals(enhanced_data)
        quality = self.signal_service.analyze_signal_quality(signals, enhanced_data)

        # Should be high-quality entry point
        assert (
            quality["confidence"] > 0.6
        ), "High-quality entry should have good confidence"
        assert quality["quality"] in [
            "good",
            "excellent",
        ], f"Expected good/excellent quality, got {quality['quality']}"

        # Create poor-quality entry point
        poor_entry_data = data_builder("TEST", 100.0).with_basic_data(60).build()

        # Weak breakout with low volume and high volatility
        poor_entry_data.iloc[55, poor_entry_data.columns.get_loc("Close")] = (
            101.0  # Minimal breakout
        )
        poor_entry_data.iloc[55, poor_entry_data.columns.get_loc("Volume")] = int(
            poor_entry_data.iloc[55]["Volume"] * 0.8  # Low volume
        )

        enhanced_poor_data = self.technical_service.calculate_all_indicators(
            poor_entry_data
        )
        poor_signals = self.signal_service.detect_all_signals(enhanced_poor_data)

        # Should have low quality if any signal is detected
        if poor_signals.has_any_signal:
            poor_quality = self.signal_service.analyze_signal_quality(
                poor_signals, enhanced_poor_data
            )
            assert (
                poor_quality["confidence"] < 0.5
            ), "Poor entry should have low confidence"

    def test_pattern_recognition_accuracy(self, data_builder):
        """Test accurate recognition of different breakout patterns"""
        # Test various breakout patterns
        patterns = {
            "horizontal_resistance": {
                "setup": lambda d: d.with_resistance_at(
                    110.0, 30, 55
                ).with_breakout_on_day(56, 113.0, 2.5),
                "expected_type": "Resistance Breakout",
            },
            "ascending_triangle": {
                "setup": lambda d: self._create_ascending_triangle(d),
                "expected_type": "Resistance Breakout",
            },
            "ma_crossover": {
                "setup": lambda d: self._create_ma_crossover(d),
                "expected_type": "MA Breakout",
            },
        }

        for pattern_name, pattern_config in patterns.items():
            data = pattern_config["setup"](
                data_builder("TEST", 100.0).with_basic_data(60)
            ).build()
            enhanced_data = self.technical_service.calculate_all_indicators(data)
            signals = self.signal_service.detect_all_signals(enhanced_data)

            if signals.breakout.signal:
                assert (
                    signals.breakout.signal_type.value
                    == pattern_config["expected_type"]
                ), f"Pattern {pattern_name} should detect {pattern_config['expected_type']}"

    def _create_ascending_triangle(self, builder):
        """Create ascending triangle pattern"""
        data = builder.build()

        # Ascending lows, horizontal highs
        resistance = 110.0
        for i in range(30, 56):
            # Ascending support line
            support_price = 100.0 + (i - 30) * 0.2
            data.iloc[i, data.columns.get_loc("Low")] = support_price
            data.iloc[i, data.columns.get_loc("High")] = resistance
            data.iloc[i, data.columns.get_loc("Close")] = support_price + 2.0

        # Breakout
        data.iloc[56, data.columns.get_loc("Close")] = resistance + 2.0
        data.iloc[56, data.columns.get_loc("Volume")] = int(
            data.iloc[56]["Volume"] * 3.0
        )

        return builder

    def _create_ma_crossover(self, builder):
        """Create moving average crossover pattern"""
        data = builder.build()

        # Create scenario where price crosses above SMA after consolidation
        for i in range(40):
            data.iloc[i, data.columns.get_loc("Close")] = 95.0 - i * 0.1  # Downtrend

        for i in range(40, 55):
            data.iloc[i, data.columns.get_loc("Close")] = 91.0 + np.random.uniform(
                -0.5, 0.5
            )  # Consolidation

        # Clear upward breakout
        for i in range(55, 60):
            data.iloc[i, data.columns.get_loc("Close")] = 92.0 + (i - 55) * 0.5
            if i == 56:
                data.iloc[i, data.columns.get_loc("Volume")] = int(
                    data.iloc[i]["Volume"] * 2.0
                )

        return builder

    def test_volume_pattern_analysis(self, data_builder):
        """Test volume pattern analysis for signal confirmation"""
        # Test different volume patterns
        volume_patterns = [
            ("spike", 4.0, True),  # Clear spike - should detect
            ("gradual", 1.8, False),  # Gradual increase - should not detect
            ("declining", 0.5, False),  # Declining volume - should not detect
        ]

        for pattern_name, volume_multiplier, should_detect in volume_patterns:
            data = (
                data_builder("TEST", 100.0)
                .with_basic_data(60)
                .with_volume_spike_on_day(55, volume_multiplier)
                .build()
            )

            enhanced_data = self.technical_service.calculate_all_indicators(data)
            signals = self.signal_service.detect_all_signals(enhanced_data)

            if should_detect:
                assert (
                    signals.volume.signal
                ), f"Should detect {pattern_name} volume pattern"
                assert (
                    signals.volume.volume_ratio >= 2.0
                ), "Volume ratio should meet threshold"
            else:
                assert (
                    not signals.volume.signal
                ), f"Should not detect {pattern_name} volume pattern"
