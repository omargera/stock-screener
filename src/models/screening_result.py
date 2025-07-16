"""
Screening result model for representing complete stock analysis results
"""

from dataclasses import dataclass

from .signals import CombinedSignals
from .stock import StockPrice


@dataclass
class ScreeningResult:
    """Complete screening result for a single stock"""
    stock_price: StockPrice
    signals: CombinedSignals

    @property
    def symbol(self) -> str:
        """Get stock symbol"""
        return self.stock_price.symbol

    @property
    def has_signals(self) -> bool:
        """Check if stock has any signals"""
        return self.signals.has_any_signal


class ScreeningResults:
    """Container for multiple screening results with analysis capabilities"""

    def __init__(self, results: list[ScreeningResult]):
        self.results = results

    @property
    def total_screened(self) -> int:
        """Total number of stocks screened"""
        return len(self.results)

    @property
    def stocks_with_signals(self) -> list[ScreeningResult]:
        """Get stocks that have any signals"""
        return [result for result in self.results if result.has_signals]

    @property
    def stocks_with_breakouts(self) -> list[ScreeningResult]:
        """Get stocks with breakout signals"""
        return [result for result in self.results if result.signals.breakout.signal]

    @property
    def stocks_with_volume_spikes(self) -> list[ScreeningResult]:
        """Get stocks with volume spike signals"""
        return [result for result in self.results if result.signals.volume.signal]

    @property
    def breakout_count(self) -> int:
        """Count of stocks with breakout signals"""
        return len(self.stocks_with_breakouts)

    @property
    def volume_spike_count(self) -> int:
        """Count of stocks with volume spikes"""
        return len(self.stocks_with_volume_spikes)

    @property
    def signal_count(self) -> int:
        """Count of stocks with any signals"""
        return len(self.stocks_with_signals)

    def add_result(self, result: ScreeningResult) -> None:
        """Add a screening result"""
        self.results.append(result)

    def get_top_signals(self, limit: int = 10) -> list[ScreeningResult]:
        """Get top signals sorted by signal strength and volume"""
        signal_stocks = self.stocks_with_signals

        # Sort by signal count first, then by breakout strength
        return sorted(
            signal_stocks,
            key=lambda x: (
                x.signals.signal_count,
                x.signals.breakout.strength if x.signals.breakout.signal else 0,
                x.signals.volume.volume_ratio if x.signals.volume.signal else 0
            ),
            reverse=True
        )[:limit]
