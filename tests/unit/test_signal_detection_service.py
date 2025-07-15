"""
Unit tests for SignalDetectionService
"""

import pytest
import pandas as pd
import numpy as np
from services.signal_detection_service import SignalDetectionService
from services.technical_analysis_service import TechnicalAnalysisService
from models.signals import BreakoutSignal, VolumeSignal, SignalType
from tests.utils.fixtures import (
    sample_stock_data, data_builder, test_scenarios, 
    assert_signal_detected, assert_no_signals, assert_signal_strength, assert_volume_ratio
)


class TestSignalDetectionService:
    """Test cases for SignalDetectionService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = SignalDetectionService(
            volume_spike_threshold=2.0,
            breakout_threshold=0.02
        )
        self.technical_service = TechnicalAnalysisService()
    
    def test_resistance_breakout_detection(self, test_scenarios):
        """Test detection of resistance breakout patterns"""
        # Use the resistance breakout scenario
        data = test_scenarios['resistance_breakout']
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        
        signals = self.service.detect_all_signals(enhanced_data)
        
        # Should detect breakout signal
        assert signals.breakout.signal, "Should detect resistance breakout"
        assert signals.breakout.signal_type == SignalType.RESISTANCE_BREAKOUT, \
            "Should identify as resistance breakout"
        assert signals.breakout.strength > 0, "Breakout strength should be positive"
        
        # Should also detect volume spike (3x volume was set)
        assert signals.volume.signal, "Should detect volume spike with breakout"
        assert signals.volume.volume_ratio >= 2.0, "Volume ratio should meet threshold"
    
    def test_ma_breakout_detection(self, test_scenarios):
        """Test detection of moving average breakout patterns"""
        data = test_scenarios['ma_breakout']
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        
        signals = self.service.detect_all_signals(enhanced_data)
        
        # Should detect MA breakout
        assert signals.breakout.signal, "Should detect MA breakout"
        assert signals.breakout.signal_type == SignalType.MA_BREAKOUT, \
            "Should identify as MA breakout"
        assert signals.breakout.strength > 0, "Breakout strength should be positive"
    
    def test_volume_spike_only_detection(self, test_scenarios):
        """Test detection of volume spike without breakout"""
        data = test_scenarios['volume_spike']
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        
        signals = self.service.detect_all_signals(enhanced_data)
        
        # Should detect volume spike but not breakout
        assert signals.volume.signal, "Should detect volume spike"
        assert signals.volume.volume_ratio >= 2.0, "Volume ratio should meet threshold"
        assert not signals.breakout.signal, "Should not detect breakout"
    
    def test_no_signal_detection(self, test_scenarios):
        """Test that no signals are detected in normal trading"""
        data = test_scenarios['no_signal']
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        
        signals = self.service.detect_all_signals(enhanced_data)
        
        # Should not detect any signals
        assert not signals.breakout.signal, "Should not detect breakout"
        assert not signals.volume.signal, "Should not detect volume spike"
        assert not signals.has_any_signal, "Should not have any signals"
    
    def test_false_breakout_rejection(self, test_scenarios):
        """Test that false breakouts are not detected as signals"""
        data = test_scenarios['false_breakout']
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        
        signals = self.service.detect_all_signals(enhanced_data)
        
        # Should not detect breakout (low volume, closed below resistance)
        assert not signals.breakout.signal, "Should not detect false breakout"
    
    def test_strict_thresholds(self, test_scenarios):
        """Test signal detection with stricter thresholds"""
        strict_service = SignalDetectionService(
            volume_spike_threshold=5.0,  # Very high threshold
            breakout_threshold=0.10      # 10% breakout threshold
        )
        
        data = test_scenarios['resistance_breakout']
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        
        signals = strict_service.detect_all_signals(enhanced_data)
        
        # With strict thresholds, may not detect signals
        # Volume spike was 3x, so should not meet 5x threshold
        assert not signals.volume.signal, "Should not detect volume spike with strict threshold"
    
    def test_custom_breakout_scenario(self, data_builder):
        """Test with custom breakout scenario"""
        # Create specific breakout pattern
        data = (data_builder("TEST", 100.0)
                .with_basic_data(60)
                .with_resistance_at(110.0, 30, 50)
                .with_breakout_on_day(55, 112.0, 2.5)
                .build())
        
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        signals = self.service.detect_all_signals(enhanced_data)
        
        # Should detect resistance breakout
        assert signals.breakout.signal, "Should detect custom resistance breakout"
        assert signals.volume.signal, "Should detect volume spike"
        
        # Check strength calculation
        resistance = enhanced_data['Resistance'].iloc[-1]
        expected_strength = (112.0 - resistance) / resistance
        actual_strength = signals.breakout.strength
        assert abs(actual_strength - expected_strength) < 0.01, \
            f"Breakout strength calculation incorrect: expected {expected_strength}, got {actual_strength}"
    
    def test_breakout_signal_creation(self):
        """Test breakout signal creation methods"""
        # Test no signal
        no_signal = BreakoutSignal.no_signal()
        assert not no_signal.signal
        assert no_signal.signal_type is None
        assert no_signal.strength == 0.0
        
        # Test resistance breakout
        resistance_signal = BreakoutSignal.resistance_breakout(0.05)
        assert resistance_signal.signal
        assert resistance_signal.signal_type == SignalType.RESISTANCE_BREAKOUT
        assert resistance_signal.strength == 0.05
        
        # Test MA breakout
        ma_signal = BreakoutSignal.ma_breakout(0.03)
        assert ma_signal.signal
        assert ma_signal.signal_type == SignalType.MA_BREAKOUT
        assert ma_signal.strength == 0.03
    
    def test_volume_signal_creation(self):
        """Test volume signal creation methods"""
        # Test no signal
        no_signal = VolumeSignal.no_signal(1.5)
        assert not no_signal.signal
        assert no_signal.volume_ratio == 1.5
        
        # Test volume spike
        spike_signal = VolumeSignal.volume_spike(3.0)
        assert spike_signal.signal
        assert spike_signal.volume_ratio == 3.0
    
    def test_insufficient_data_handling(self, data_builder):
        """Test handling of insufficient data"""
        # Create data with only 10 days (insufficient for analysis)
        data = data_builder("TEST", 100.0).with_basic_data(10).build()
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        
        signals = self.service.detect_all_signals(enhanced_data)
        
        # Should not detect signals with insufficient data
        assert not signals.breakout.signal, "Should not detect breakout with insufficient data"
        assert not signals.volume.signal, "Should not detect volume spike with insufficient data"
    
    def test_edge_case_volume_calculations(self, data_builder):
        """Test edge cases in volume calculations"""
        data = data_builder("TEST", 100.0).with_basic_data(30).build()
        
        # Set zero average volume (edge case)
        data['Volume'] = [0] * len(data)
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        
        signals = self.service.detect_all_signals(enhanced_data)
        
        # Should handle zero volume gracefully
        assert not signals.volume.signal, "Should not detect volume spike with zero volume"
        assert signals.volume.volume_ratio == 0, "Volume ratio should be 0"
    
    def test_breakout_confirmation_requirements(self, data_builder):
        """Test that breakouts require proper confirmation"""
        data = data_builder("TEST", 100.0).with_basic_data(60).build()
        
        # Create scenario where price breaks resistance but volume is low
        resistance_level = 110.0
        
        # Set resistance
        for i in range(30, 50):
            data.iloc[i, data.columns.get_loc('High')] = resistance_level
        
        # Day 55: Price breaks but volume is too low
        breakout_day = 55
        data.iloc[breakout_day, data.columns.get_loc('Close')] = resistance_level + 2
        data.iloc[breakout_day, data.columns.get_loc('High')] = resistance_level + 3
        data.iloc[breakout_day, data.columns.get_loc('Volume')] = int(
            data.iloc[breakout_day]['Volume'] * 0.5  # Low volume
        )
        
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        signals = self.service.detect_all_signals(enhanced_data)
        
        # Should not detect breakout without volume confirmation
        assert not signals.breakout.signal, "Should not detect breakout without volume confirmation"
    
    def test_ma_breakout_trend_requirement(self, data_builder):
        """Test that MA breakouts require uptrend confirmation"""
        data = data_builder("TEST", 100.0).with_basic_data(60).build()
        
        # Create scenario where price breaks SMA but trend is not confirmed
        for i in range(len(data)):
            # Set SMA_20 > SMA_50 initially, then reverse for trend test
            if i < 50:
                data.iloc[i, data.columns.get_loc('Close')] = 90.0  # Below both MAs
            else:
                data.iloc[i, data.columns.get_loc('Close')] = 95.0  # Above SMA_20 but downtrend
        
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        
        # Manually create scenario where SMA_20 < SMA_50 (downtrend)
        enhanced_data.loc[enhanced_data.index[-1], 'SMA_20'] = 90.0
        enhanced_data.loc[enhanced_data.index[-1], 'SMA_50'] = 95.0
        enhanced_data.loc[enhanced_data.index[-2], 'SMA_20'] = 89.0
        
        signals = self.service.detect_all_signals(enhanced_data)
        
        # Should not detect MA breakout without uptrend confirmation
        assert not signals.breakout.signal, "Should not detect MA breakout in downtrend"
    
    def test_signal_quality_analysis(self, test_scenarios):
        """Test signal quality analysis functionality"""
        data = test_scenarios['resistance_breakout']
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        signals = self.service.detect_all_signals(enhanced_data)
        
        quality = self.service.analyze_signal_quality(signals, enhanced_data)
        
        # Should return quality analysis
        assert 'quality' in quality
        assert 'confidence' in quality
        assert 'factors' in quality
        assert 'score' in quality
        
        # Quality should be reasonable for good breakout
        assert quality['confidence'] > 0.0, "Confidence should be positive"
        assert quality['quality'] in ['poor', 'fair', 'good', 'excellent'], \
            f"Invalid quality level: {quality['quality']}"
    
    def test_multiple_signal_detection(self, data_builder):
        """Test detection of multiple signals in same data"""
        data = (data_builder("TEST", 100.0)
                .with_basic_data(60)
                .with_resistance_at(110.0, 30, 50)
                .with_breakout_on_day(55, 112.0, 3.0)  # Both breakout and volume spike
                .build())
        
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        signals = self.service.detect_all_signals(enhanced_data)
        
        # Should detect both signals
        assert signals.breakout.signal, "Should detect breakout signal"
        assert signals.volume.signal, "Should detect volume signal"
        assert signals.has_any_signal, "Should have signals"
        assert signals.signal_count == 2, "Should count 2 signals"
    
    def test_performance_signal_detection(self, performance_timer):
        """Test signal detection performance"""
        from tests.utils.test_data_generator import StockDataGenerator
        
        # Generate large dataset
        generator = StockDataGenerator("TEST", 100.0)
        large_data = generator.generate_basic_data(1000)
        enhanced_data = self.technical_service.calculate_all_indicators(large_data)
        
        performance_timer.start()
        signals = self.service.detect_all_signals(enhanced_data)
        performance_timer.stop()
        
        # Should complete quickly
        assert performance_timer.elapsed < 0.1, \
            f"Signal detection took too long: {performance_timer.elapsed} seconds"
        
        # Should return valid signals
        assert hasattr(signals, 'breakout')
        assert hasattr(signals, 'volume')
    
    def test_signal_strength_calculations(self, data_builder):
        """Test accurate signal strength calculations"""
        data = data_builder("TEST", 100.0).with_basic_data(60).build()
        
        # Create precise breakout scenario
        resistance = 110.0
        breakout_price = 113.0  # 2.73% above resistance
        
        data.iloc[55, data.columns.get_loc('Close')] = breakout_price
        data.iloc[55, data.columns.get_loc('High')] = breakout_price + 1
        data.iloc[55, data.columns.get_loc('Volume')] = int(data.iloc[55]['Volume'] * 2.0)
        
        # Set resistance level
        for i in range(30, 55):
            data.iloc[i, data.columns.get_loc('High')] = resistance
        
        enhanced_data = self.technical_service.calculate_all_indicators(data)
        signals = self.service.detect_all_signals(enhanced_data)
        
        if signals.breakout.signal:
            expected_strength = (breakout_price - resistance) / resistance
            actual_strength = signals.breakout.strength
            
            # Allow small tolerance for floating point calculations
            assert abs(actual_strength - expected_strength) < 0.001, \
                f"Signal strength calculation error: expected {expected_strength}, got {actual_strength}"
    
    def test_error_handling_in_detection(self):
        """Test error handling in signal detection"""
        # Test with empty data
        empty_data = pd.DataFrame()
        signals = self.service.detect_all_signals(empty_data)
        
        # Should return no signals without crashing
        assert not signals.breakout.signal
        assert not signals.volume.signal
        
        # Test with malformed data
        bad_data = pd.DataFrame({'Close': [100], 'Volume': [1000]})
        signals = self.service.detect_all_signals(bad_data)
        
        # Should handle gracefully
        assert not signals.breakout.signal
        assert not signals.volume.signal 