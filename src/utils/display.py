"""
Display utilities for formatting and presenting screening results
"""

from datetime import datetime

from models.screening_result import ScreeningResult, ScreeningResults


class ResultsDisplayService:
    """Service for displaying screening results in a formatted way"""

    def __init__(self):
        self.header_separator = "=" * 80
        self.section_separator = "-" * 80

    def display_screening_results(self, results: ScreeningResults) -> None:
        """
        Display complete screening results

        Args:
            results (ScreeningResults): Screening results to display
        """
        print("\n" + self.header_separator)
        print(" STOCK SCREENING RESULTS")
        print(self.header_separator)

        # Display stocks with signals
        signal_stocks = results.stocks_with_signals

        if signal_stocks:
            print(f"\n🚨 STOCKS WITH SIGNALS ({len(signal_stocks)} found):")
            print(self.section_separator)

            for result in signal_stocks:
                self._display_single_result(result)
        else:
            print("\n⚠️  No stocks with signals found in current screening.")

        # Display summary
        self._display_summary(results)
        print(self.header_separator)

    def display_top_opportunities(self, opportunities: list[ScreeningResult], limit: int = 5) -> None:
        """
        Display top investment opportunities

        Args:
            opportunities (List[ScreeningResult]): Top opportunities to display
            limit (int): Maximum number to display
        """
        print("\n" + self.header_separator)
        print(f" TOP {min(limit, len(opportunities))} INVESTMENT OPPORTUNITIES")
        print(self.header_separator)

        if opportunities:
            for i, result in enumerate(opportunities[:limit], 1):
                print(f"\n🏆 #{i} - {result.symbol}")
                self._display_single_result(result, show_quality=True)
        else:
            print("\n⚠️  No opportunities found.")

        print(self.header_separator)

    def display_market_analysis(self, analysis: dict) -> None:
        """
        Display market condition analysis

        Args:
            analysis (dict): Market analysis data
        """
        print("\n" + self.header_separator)
        print(" MARKET CONDITION ANALYSIS")
        print(self.header_separator)

        condition = analysis.get('condition', 'unknown')
        signal_pct = analysis.get('signal_percentage', 0)

        # Choose emoji based on condition
        condition_emoji = {
            'very_bullish': '🚀',
            'bullish': '📈',
            'neutral_positive': '➡️',
            'neutral': '😐',
            'bearish': '📉',
            'unknown': '❓'
        }.get(condition, '❓')

        print(f"\n{condition_emoji} Overall Market Condition: {condition.upper().replace('_', ' ')}")
        print(f"📊 Signal Percentage: {signal_pct}%")
        print(f"📈 Breakout Stocks: {analysis.get('breakout_stocks', 0)}")
        print(f"📊 Volume Spike Stocks: {analysis.get('volume_spike_stocks', 0)}")
        print(f"🎯 Total Screened: {analysis.get('total_screened', 0)}")

        print(self.header_separator)

    def _display_single_result(self, result: ScreeningResult, show_quality: bool = False) -> None:
        """
        Display a single screening result

        Args:
            result (ScreeningResult): Result to display
            show_quality (bool): Whether to show quality information
        """
        stock = result.stock_price
        signals = result.signals

        print(f"\n📈 {stock.symbol}")
        print(f"   Price: ${stock.current_price} ({stock.price_change_pct:+.2f}%)")
        print(f"   Volume: {stock.volume:,} (Avg: {stock.avg_volume:,})")

        # Display breakout signals
        if signals.breakout.signal:
            signal_type = signals.breakout.signal_type.value if signals.breakout.signal_type else "Unknown"
            strength_pct = signals.breakout.strength * 100
            print(f"   🔥 BREAKOUT: {signal_type} (Strength: {strength_pct:.2f}%)")

        # Display volume signals
        if signals.volume.signal:
            volume_ratio = signals.volume.volume_ratio
            print(f"   📊 VOLUME SPIKE: {volume_ratio:.1f}x average")

        # Display quality information if available
        if show_quality and hasattr(result, 'quality'):
            quality_info = result.quality
            quality_level = quality_info.get('quality', 'unknown')
            confidence = quality_info.get('confidence', 0)
            print(f"   ⭐ Quality: {quality_level.upper()} (Confidence: {confidence:.0%})")

    def _display_summary(self, results: ScreeningResults) -> None:
        """
        Display summary statistics

        Args:
            results (ScreeningResults): Results to summarize
        """
        print("\n📊 SUMMARY:")
        print(f"   Total stocks screened: {results.total_screened}")
        print(f"   Stocks with breakout signals: {results.breakout_count}")
        print(f"   Stocks with volume spikes: {results.volume_spike_count}")
        print(f"   Total stocks with signals: {results.signal_count}")
        print(f"   Screening completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def display_system_health(self, health_status: dict) -> None:
        """
        Display system health status

        Args:
            health_status (dict): System health information
        """
        print("\n" + self.header_separator)
        print(" SYSTEM HEALTH STATUS")
        print(self.header_separator)

        overall = health_status.get('overall', 'unknown')

        # Choose emoji based on overall health
        health_emoji = {
            'healthy': '✅',
            'degraded': '⚠️',
            'unhealthy': '❌',
            'unknown': '❓'
        }.get(overall, '❓')

        print(f"\n{health_emoji} Overall Status: {overall.upper()}")

        # Display component status
        components = {
            'data_gateway': 'Data Gateway',
            'technical_service': 'Technical Analysis',
            'signal_service': 'Signal Detection'
        }

        for key, name in components.items():
            status = health_status.get(key, 'unknown')
            status_emoji = {
                'healthy': '✅',
                'unhealthy': '❌',
                'not_testable': '⚪',
                'unknown': '❓'
            }.get(status, '❓')

            print(f"   {status_emoji} {name}: {status}")

        if 'error' in health_status:
            print(f"\n❌ Error: {health_status['error']}")

        print(self.header_separator)

    def display_welcome_message(self) -> None:
        """Display welcome message and startup information"""
        print("🔍 Starting Stock Screener...")
        print("═" * 50)
        print("🎯 Features:")
        print("   • Breakout pattern detection")
        print("   • Volume spike identification")
        print("   • Technical indicator analysis")
        print("   • Real-time market data")
        print("═" * 50)

    def display_screening_progress(self, current: int, total: int, symbol: str) -> None:
        """
        Display screening progress

        Args:
            current (int): Current position
            total (int): Total number of stocks
            symbol (str): Current symbol being processed
        """
        percentage = (current / total) * 100
        progress_bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))

        print(f"\r📊 Progress: [{progress_bar}] {percentage:.1f}% - Screening {symbol}...", end="", flush=True)

        if current == total:
            print()  # New line after completion

    def display_error_message(self, message: str, error_type: str = "ERROR") -> None:
        """
        Display formatted error message

        Args:
            message (str): Error message
            error_type (str): Type of error
        """
        error_emoji = {
            'ERROR': '❌',
            'WARNING': '⚠️',
            'INFO': 'ℹ️'
        }.get(error_type, '❌')

        print(f"\n{error_emoji} {error_type}: {message}")

    def display_quick_stats(self, results: ScreeningResults) -> None:
        """
        Display quick statistics in a compact format

        Args:
            results (ScreeningResults): Results to display stats for
        """
        if results.signal_count > 0:
            print(f"🚨 Quick Alert: {results.signal_count} signals detected!")
            for result in results.stocks_with_signals[:3]:  # Show top 3
                signals_text = []
                if result.signals.breakout.signal:
                    signals_text.append("📈 Breakout")
                if result.signals.volume.signal:
                    signals_text.append("📊 Volume")

                print(f"   • {result.symbol}: {', '.join(signals_text)}")

            if results.signal_count > 3:
                print(f"   ... and {results.signal_count - 3} more")
        else:
            print("😔 No signals detected in current screening.")
