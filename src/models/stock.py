"""
Stock data model for representing stock information
"""

from dataclasses import dataclass
from typing import Optional
import pandas as pd
from datetime import datetime


@dataclass
class StockPrice:
    """Represents current stock price information"""
    symbol: str
    current_price: float
    price_change_pct: float
    volume: int
    avg_volume: int
    timestamp: str

    @classmethod
    def from_data(cls, symbol: str, data: pd.DataFrame) -> 'StockPrice':
        """Create StockPrice from pandas DataFrame"""
        latest = data.iloc[-1]
        return cls(
            symbol=symbol,
            current_price=round(latest['Close'], 2),
            price_change_pct=round(latest['Price_Change_Pct'] * 100, 2),
            volume=int(latest['Volume']),
            avg_volume=int(latest['Volume_MA_20']),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )


@dataclass
class TechnicalIndicators:
    """Technical indicators calculated for stock analysis"""
    sma_20: float
    sma_50: float
    volume_ma_20: float
    price_volatility: float
    resistance: float
    support: float
    
    @classmethod
    def from_data(cls, data: pd.DataFrame) -> 'TechnicalIndicators':
        """Create TechnicalIndicators from pandas DataFrame"""
        latest = data.iloc[-1]
        return cls(
            sma_20=latest['SMA_20'],
            sma_50=latest['SMA_50'],
            volume_ma_20=latest['Volume_MA_20'],
            price_volatility=latest['Price_Volatility'],
            resistance=latest['Resistance'],
            support=latest['Support']
        )


class StockData:
    """Container for stock data and calculated indicators"""
    
    def __init__(self, symbol: str, raw_data: pd.DataFrame):
        self.symbol = symbol
        self.raw_data = raw_data
        self._price_info: Optional[StockPrice] = None
        self._technical_indicators: Optional[TechnicalIndicators] = None
    
    @property
    def price_info(self) -> StockPrice:
        """Get current price information"""
        if self._price_info is None:
            self._price_info = StockPrice.from_data(self.symbol, self.raw_data)
        return self._price_info
    
    @property
    def technical_indicators(self) -> TechnicalIndicators:
        """Get technical indicators"""
        if self._technical_indicators is None:
            self._technical_indicators = TechnicalIndicators.from_data(self.raw_data)
        return self._technical_indicators
    
    @property
    def has_sufficient_data(self) -> bool:
        """Check if there's enough data for analysis"""
        return len(self.raw_data) >= 21
    
    def get_latest_data(self) -> pd.Series:
        """Get the latest row of data"""
        return self.raw_data.iloc[-1]
    
    def get_previous_data(self) -> pd.Series:
        """Get the previous row of data"""
        return self.raw_data.iloc[-2] if len(self.raw_data) > 1 else self.raw_data.iloc[-1] 