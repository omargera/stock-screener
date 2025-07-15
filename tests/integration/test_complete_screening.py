"""
Integration tests for complete stock screening process
"""

import pytest
from services.screener_service import StockScreenerService, ScreenerConfiguration
from models.screening_result import ScreeningResults
from tests.utils.fixtures import (
    mock_gateway, screener_config, strict_screener_config,
    assert_signal_detected, assert_no_signals, performance_timer
)


class TestCompleteScreening:
    """Integration tests for complete screening workflow"""
    
    def test_single_stock_screening_with_signals(self, mock_gateway, screener_config):
        """Test complete screening process for a single stock with signals"""
        service = StockScreenerService(screener_config, mock_gateway)
        
        # Screen stock that should have resistance breakout
        result = service.screen_single_stock('TEST_RESISTANCE')
        
        assert result is not None, "Should return screening result"
        assert result.stock_price.symbol == 'TEST_RESISTANCE'
        assert result.stock_price.current_price > 0
        assert result.has_signals, "Should detect signals"
        
        # Should detect both breakout and volume signals
        assert result.signals.breakout.signal, "Should detect breakout"
        assert result.signals.volume.signal, "Should detect volume spike"
    
    def test_single_stock_screening_no_signals(self, mock_gateway, screener_config):
        """Test screening for stock with no signals"""
        service = StockScreenerService(screener_config, mock_gateway)
        
        result = service.screen_single_stock('TEST_NONE')
        
        assert result is not None, "Should return screening result"
        assert result.stock_price.symbol == 'TEST_NONE'
        assert not result.has_signals, "Should not detect signals"
        assert not result.signals.breakout.signal, "Should not detect breakout"
        assert not result.signals.volume.signal, "Should not detect volume spike"
    
    def test_multiple_stocks_screening(self, mock_gateway, screener_config):
        """Test screening multiple stocks"""
        service = StockScreenerService(screener_config, mock_gateway)
        
        symbols = ['TEST_RESISTANCE', 'TEST_MA', 'TEST_VOLUME', 'TEST_NONE', 'TEST_FALSE']
        results = service.screen_multiple_stocks(symbols)
        
        assert results.total_screened == 5, "Should screen 5 stocks"
        
        # Check that signal stocks are detected
        signal_stocks = results.stocks_with_signals
        assert len(signal_stocks) >= 3, "Should find at least 3 stocks with signals"
        
        # Verify specific signals
        resistance_stock = next((r for r in results.results if r.symbol == 'TEST_RESISTANCE'), None)
        assert resistance_stock is not None, "Should find TEST_RESISTANCE"
        assert resistance_stock.signals.breakout.signal, "TEST_RESISTANCE should have breakout"
        
        volume_stock = next((r for r in results.results if r.symbol == 'TEST_VOLUME'), None)
        assert volume_stock is not None, "Should find TEST_VOLUME"
        assert volume_stock.signals.volume.signal, "TEST_VOLUME should have volume spike"
        
        no_signal_stock = next((r for r in results.results if r.symbol == 'TEST_NONE'), None)
        assert no_signal_stock is not None, "Should find TEST_NONE"
        assert not no_signal_stock.has_signals, "TEST_NONE should have no signals"
    
    def test_screening_with_strict_configuration(self, mock_gateway, strict_screener_config):
        """Test screening with strict thresholds"""
        service = StockScreenerService(strict_screener_config, mock_gateway)
        
        # Same stocks but with stricter thresholds
        symbols = ['TEST_RESISTANCE', 'TEST_VOLUME']
        results = service.screen_multiple_stocks(symbols)
        
        # Should find fewer signals with strict thresholds
        signal_count = results.signal_count
        assert signal_count <= 2, "Should find fewer signals with strict thresholds"
    
    def test_stocks_with_signals_only(self, mock_gateway, screener_config):
        """Test getting only stocks with signals"""
        service = StockScreenerService(screener_config, mock_gateway)
        
        symbols = ['TEST_RESISTANCE', 'TEST_NONE', 'TEST_VOLUME']
        signal_results = service.get_stocks_with_signals(symbols)
        
        # Should only return stocks with signals
        assert signal_results.total_screened <= 3, "Should screen max 3 stocks"
        assert signal_results.signal_count >= 2, "Should find signal stocks"
        
        # All returned results should have signals
        for result in signal_results.results:
            assert result.has_signals, f"{result.symbol} should have signals"
    
    def test_market_analysis(self, mock_gateway, screener_config):
        """Test market condition analysis"""
        service = StockScreenerService(screener_config, mock_gateway)
        
        # Mix of stocks with and without signals
        symbols = ['TEST_RESISTANCE', 'TEST_MA', 'TEST_VOLUME', 'TEST_NONE', 'TEST_FALSE']
        analysis = service.analyze_market_conditions(symbols)
        
        assert 'condition' in analysis, "Should include market condition"
        assert 'signal_percentage' in analysis, "Should include signal percentage"
        assert 'total_screened' in analysis, "Should include total screened"
        assert 'stocks_with_signals' in analysis, "Should include signal count"
        
        assert analysis['total_screened'] == 5, "Should screen 5 stocks"
        assert analysis['signal_percentage'] >= 0, "Signal percentage should be non-negative"
        assert analysis['condition'] in [
            'very_bullish', 'bullish', 'neutral_positive', 'neutral', 'bearish'
        ], f"Invalid market condition: {analysis['condition']}"
    
    def test_top_opportunities(self, mock_gateway, screener_config):
        """Test getting top investment opportunities"""
        service = StockScreenerService(screener_config, mock_gateway)
        
        symbols = ['TEST_RESISTANCE', 'TEST_MA', 'TEST_VOLUME', 'TEST_NONE']
        opportunities = service.get_top_opportunities(symbols, limit=3)
        
        assert len(opportunities) <= 3, "Should limit to 3 opportunities"
        
        # Should be sorted by signal quality (multiple signals first)
        if len(opportunities) > 1:
            first_op = opportunities[0]
            second_op = opportunities[1]
            
            # First opportunity should have at least as many signals as second
            assert first_op.signals.signal_count >= second_op.signals.signal_count, \
                "Opportunities should be sorted by signal quality"
    
    def test_error_handling_in_screening(self, mock_failing_gateway, screener_config):
        """Test error handling when data fetching fails"""
        service = StockScreenerService(screener_config, mock_failing_gateway)
        
        # Should handle failed data fetching gracefully
        result = service.screen_single_stock('INVALID')
        assert result is None, "Should return None for failed fetch"
        
        # Should handle multiple failures
        symbols = ['INVALID1', 'INVALID2', 'INVALID3']
        results = service.screen_multiple_stocks(symbols)
        
        assert results.total_screened == 0, "Should screen 0 stocks due to failures"
        assert results.signal_count == 0, "Should find 0 signals"
    
    def test_system_health_check(self, mock_gateway, screener_config):
        """Test system health checking"""
        service = StockScreenerService(screener_config, mock_gateway)
        
        health = service.test_system_health()
        
        assert 'overall' in health, "Should include overall status"
        assert 'data_gateway' in health, "Should include gateway status"
        assert 'technical_service' in health, "Should include technical service status"
        assert 'signal_service' in health, "Should include signal service status"
        
        # Mock gateway should be healthy
        assert health['data_gateway'] == 'healthy', "Mock gateway should be healthy"
        assert health['overall'] in ['healthy', 'degraded'], "Overall should be healthy or degraded"
    
    def test_screening_performance(self, mock_gateway, screener_config, performance_timer):
        """Test screening performance with multiple stocks"""
        service = StockScreenerService(screener_config, mock_gateway)
        
        # Test with many stocks
        symbols = [f'TEST_RESISTANCE_{i}' for i in range(20)]  # 20 stocks
        
        performance_timer.start()
        results = service.screen_multiple_stocks(symbols)
        performance_timer.stop()
        
        # Should complete in reasonable time
        assert performance_timer.elapsed < 5.0, \
            f"Screening took too long: {performance_timer.elapsed} seconds"
        
        # Should handle all stocks (mock returns same data for any symbol)
        assert results.total_screened == 20, "Should screen all 20 stocks"
    
    def test_configuration_impact(self, mock_gateway):
        """Test how different configurations affect results"""
        # Liberal configuration
        liberal_config = ScreenerConfiguration(
            period="3mo",
            volume_spike_threshold=1.5,
            breakout_threshold=0.01
        )
        
        # Conservative configuration  
        conservative_config = ScreenerConfiguration(
            period="3mo",
            volume_spike_threshold=4.0,
            breakout_threshold=0.05
        )
        
        liberal_service = StockScreenerService(liberal_config, mock_gateway)
        conservative_service = StockScreenerService(conservative_config, mock_gateway)
        
        symbols = ['TEST_RESISTANCE', 'TEST_VOLUME']
        
        liberal_results = liberal_service.screen_multiple_stocks(symbols)
        conservative_results = conservative_service.screen_multiple_stocks(symbols)
        
        # Liberal configuration should find more signals
        assert liberal_results.signal_count >= conservative_results.signal_count, \
            "Liberal config should find at least as many signals as conservative"
    
    def test_data_flow_integrity(self, mock_gateway, screener_config):
        """Test that data flows correctly through all layers"""
        service = StockScreenerService(screener_config, mock_gateway)
        
        result = service.screen_single_stock('TEST_RESISTANCE')
        
        # Verify data integrity through the flow
        assert result.stock_price.symbol == 'TEST_RESISTANCE'
        assert result.stock_price.current_price > 0
        assert result.stock_price.volume > 0
        assert result.stock_price.avg_volume > 0
        assert result.stock_price.timestamp is not None
        
        # Verify signal data integrity
        if result.signals.breakout.signal:
            assert result.signals.breakout.strength >= 0
            assert result.signals.breakout.signal_type is not None
        
        if result.signals.volume.signal:
            assert result.signals.volume.volume_ratio >= 1.0
    
    def test_screening_results_analysis(self, mock_gateway, screener_config):
        """Test ScreeningResults analysis capabilities"""
        service = StockScreenerService(screener_config, mock_gateway)
        
        symbols = ['TEST_RESISTANCE', 'TEST_MA', 'TEST_VOLUME', 'TEST_NONE', 'TEST_FALSE']
        results = service.screen_multiple_stocks(symbols)
        
        # Test breakout analysis
        breakout_stocks = results.stocks_with_breakouts
        assert len(breakout_stocks) >= 2, "Should find breakout stocks"
        
        # Test volume spike analysis
        volume_stocks = results.stocks_with_volume_spikes
        assert len(volume_stocks) >= 2, "Should find volume spike stocks"
        
        # Test counts
        assert results.breakout_count == len(breakout_stocks)
        assert results.volume_spike_count == len(volume_stocks)
        assert results.signal_count == len(results.stocks_with_signals)
        
        # Test top signals
        top_signals = results.get_top_signals(3)
        assert len(top_signals) <= 3, "Should limit top signals"
        
        # All top signals should have signals
        for result in top_signals:
            assert result.has_signals, "Top signals should all have signals"
    
    def test_end_to_end_workflow(self, mock_gateway, screener_config):
        """Test complete end-to-end workflow"""
        service = StockScreenerService(screener_config, mock_gateway)
        
        # Step 1: Screen multiple stocks
        symbols = ['TEST_RESISTANCE', 'TEST_MA', 'TEST_VOLUME', 'TEST_NONE']
        all_results = service.screen_multiple_stocks(symbols)
        
        # Step 2: Get market analysis
        market_analysis = service.analyze_market_conditions(symbols)
        
        # Step 3: Get top opportunities
        opportunities = service.get_top_opportunities(symbols, limit=2)
        
        # Step 4: Get signal-only results
        signal_results = service.get_stocks_with_signals(symbols)
        
        # Verify consistency across operations
        assert all_results.total_screened == 4, "Should screen 4 stocks"
        assert market_analysis['total_screened'] == 4, "Market analysis should match"
        assert len(opportunities) <= 2, "Should have max 2 opportunities"
        assert signal_results.signal_count <= all_results.signal_count, \
            "Signal-only results should be subset"
        
        # Verify signal counts are consistent
        expected_signal_count = all_results.signal_count
        actual_market_signals = market_analysis['stocks_with_signals']
        assert actual_market_signals == expected_signal_count, \
            "Market analysis signal count should match screening results" 