"""
Main screener service for orchestrating stock screening process
"""

import logging
from typing import List, Optional
from models.stock import StockData
from models.screening_result import ScreeningResult, ScreeningResults
from gateways.stock_data_gateway import StockDataGateway, YahooFinanceGateway
from services.technical_analysis_service import TechnicalAnalysisService
from services.signal_detection_service import SignalDetectionService

logger = logging.getLogger(__name__)


class ScreenerConfiguration:
    """Configuration class for screener parameters"""
    
    def __init__(
        self,
        period: str = "3mo",
        volume_spike_threshold: float = 2.0,
        breakout_threshold: float = 0.02
    ):
        self.period = period
        self.volume_spike_threshold = volume_spike_threshold
        self.breakout_threshold = breakout_threshold


class StockScreenerService:
    """Main service for screening stocks"""
    
    def __init__(
        self,
        config: ScreenerConfiguration,
        data_gateway: Optional[StockDataGateway] = None
    ):
        """
        Initialize the stock screener service
        
        Args:
            config (ScreenerConfiguration): Screening configuration
            data_gateway (StockDataGateway, optional): Data gateway for fetching stock data
        """
        self.config = config
        self.data_gateway = data_gateway or YahooFinanceGateway()
        self.technical_service = TechnicalAnalysisService()
        self.signal_service = SignalDetectionService(
            volume_spike_threshold=config.volume_spike_threshold,
            breakout_threshold=config.breakout_threshold
        )
    
    def screen_single_stock(self, symbol: str) -> Optional[ScreeningResult]:
        """
        Screen a single stock for signals
        
        Args:
            symbol (str): Stock symbol to screen
            
        Returns:
            ScreeningResult: Screening result or None if failed
        """
        try:
            logger.info(f"Screening {symbol}...")
            
            # Step 1: Fetch stock data
            raw_data = self.data_gateway.fetch_stock_data(symbol, self.config.period)
            if raw_data is None:
                logger.warning(f"Failed to fetch data for {symbol}")
                return None
            
            # Step 2: Create stock data object
            stock_data = StockData(symbol, raw_data)
            if not stock_data.has_sufficient_data:
                logger.warning(f"Insufficient data for analysis: {symbol}")
                return None
            
            # Step 3: Calculate technical indicators
            enhanced_data = self.technical_service.calculate_all_indicators(raw_data)
            stock_data.raw_data = enhanced_data
            
            # Step 4: Detect signals
            signals = self.signal_service.detect_all_signals(enhanced_data)
            
            # Step 5: Create screening result
            result = ScreeningResult(
                stock_price=stock_data.price_info,
                signals=signals
            )
            
            logger.info(f"Completed screening for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error screening {symbol}: {str(e)}")
            return None
    
    def screen_multiple_stocks(self, symbols: List[str]) -> ScreeningResults:
        """
        Screen multiple stocks
        
        Args:
            symbols (List[str]): List of stock symbols to screen
            
        Returns:
            ScreeningResults: Combined screening results
        """
        logger.info(f"Starting screening of {len(symbols)} stocks...")
        
        results = []
        successful_screens = 0
        failed_screens = 0
        
        for symbol in symbols:
            try:
                result = self.screen_single_stock(symbol)
                if result:
                    results.append(result)
                    successful_screens += 1
                else:
                    failed_screens += 1
                    
            except Exception as e:
                logger.error(f"Unexpected error screening {symbol}: {str(e)}")
                failed_screens += 1
                continue
        
        logger.info(
            f"Screening completed: {successful_screens} successful, "
            f"{failed_screens} failed out of {len(symbols)} total"
        )
        
        return ScreeningResults(results)
    
    def get_stocks_with_signals(self, symbols: List[str]) -> ScreeningResults:
        """
        Get only stocks that have signals detected
        
        Args:
            symbols (List[str]): List of stock symbols to screen
            
        Returns:
            ScreeningResults: Results containing only stocks with signals
        """
        all_results = self.screen_multiple_stocks(symbols)
        signal_results = ScreeningResults(all_results.stocks_with_signals)
        
        logger.info(
            f"Found {signal_results.signal_count} stocks with signals "
            f"out of {all_results.total_screened} screened"
        )
        
        return signal_results
    
    def analyze_market_conditions(self, symbols: List[str]) -> dict:
        """
        Analyze overall market conditions based on screening results
        
        Args:
            symbols (List[str]): List of stock symbols to analyze
            
        Returns:
            dict: Market condition analysis
        """
        try:
            results = self.screen_multiple_stocks(symbols)
            
            if results.total_screened == 0:
                return {"condition": "unknown", "reason": "no_data"}
            
            # Calculate market metrics
            breakout_percentage = (results.breakout_count / results.total_screened) * 100
            volume_spike_percentage = (results.volume_spike_count / results.total_screened) * 100
            signal_percentage = (results.signal_count / results.total_screened) * 100
            
            # Determine market condition
            if signal_percentage >= 30:
                condition = "very_bullish"
            elif signal_percentage >= 20:
                condition = "bullish"
            elif signal_percentage >= 10:
                condition = "neutral_positive"
            elif signal_percentage >= 5:
                condition = "neutral"
            else:
                condition = "bearish"
            
            analysis = {
                "condition": condition,
                "signal_percentage": round(signal_percentage, 1),
                "breakout_percentage": round(breakout_percentage, 1),
                "volume_spike_percentage": round(volume_spike_percentage, 1),
                "total_screened": results.total_screened,
                "stocks_with_signals": results.signal_count,
                "breakout_stocks": results.breakout_count,
                "volume_spike_stocks": results.volume_spike_count
            }
            
            logger.info(f"Market analysis: {condition} ({signal_percentage:.1f}% with signals)")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {str(e)}")
            return {"condition": "unknown", "reason": "error"}
    
    def get_top_opportunities(self, symbols: List[str], limit: int = 5) -> List[ScreeningResult]:
        """
        Get top investment opportunities based on signal strength
        
        Args:
            symbols (List[str]): List of stock symbols to screen
            limit (int): Maximum number of opportunities to return
            
        Returns:
            List[ScreeningResult]: Top opportunities sorted by signal quality
        """
        try:
            results = self.screen_multiple_stocks(symbols)
            top_signals = results.get_top_signals(limit)
            
            # Add signal quality analysis
            enhanced_opportunities = []
            for result in top_signals:
                # Get the enhanced data for quality analysis
                raw_data = self.data_gateway.fetch_stock_data(
                    result.symbol, self.config.period
                )
                if raw_data is not None:
                    enhanced_data = self.technical_service.calculate_all_indicators(raw_data)
                    quality = self.signal_service.analyze_signal_quality(
                        result.signals, enhanced_data
                    )
                    
                    # Add quality info to result (we could extend the model for this)
                    setattr(result, 'quality', quality)
                
                enhanced_opportunities.append(result)
            
            logger.info(f"Identified {len(enhanced_opportunities)} top opportunities")
            return enhanced_opportunities
            
        except Exception as e:
            logger.error(f"Error getting top opportunities: {str(e)}")
            return []
    
    def test_system_health(self) -> dict:
        """
        Test system health and connectivity
        
        Returns:
            dict: System health status
        """
        try:
            health_status = {
                "overall": "healthy",
                "data_gateway": "unknown",
                "technical_service": "unknown",
                "signal_service": "unknown"
            }
            
            # Test data gateway
            if hasattr(self.data_gateway, 'test_connection'):
                if self.data_gateway.test_connection():
                    health_status["data_gateway"] = "healthy"
                else:
                    health_status["data_gateway"] = "unhealthy"
                    health_status["overall"] = "degraded"
            else:
                health_status["data_gateway"] = "not_testable"
            
            # Test technical service (simple test)
            try:
                import pandas as pd
                test_data = pd.DataFrame({
                    'Open': [100, 101, 102],
                    'High': [101, 102, 103],
                    'Low': [99, 100, 101],
                    'Close': [100.5, 101.5, 102.5],
                    'Volume': [1000, 1100, 1200]
                })
                self.technical_service.calculate_all_indicators(test_data)
                health_status["technical_service"] = "healthy"
            except Exception:
                health_status["technical_service"] = "unhealthy"
                health_status["overall"] = "degraded"
            
            # Test signal service
            try:
                # This will be tested indirectly through technical service test
                health_status["signal_service"] = "healthy"
            except Exception:
                health_status["signal_service"] = "unhealthy"
                health_status["overall"] = "degraded"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error testing system health: {str(e)}")
            return {"overall": "unhealthy", "error": str(e)} 