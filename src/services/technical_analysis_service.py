"""
Technical analysis service for calculating technical indicators
"""

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """Service for calculating technical indicators"""

    def __init__(self):
        pass

    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for the given data

        Args:
            data (pd.DataFrame): Raw OHLCV stock data

        Returns:
            pd.DataFrame: Data with additional technical indicators
        """
        try:
            logger.debug("Calculating technical indicators")

            # Make a copy to avoid modifying original data
            enhanced_data = data.copy()

            # Calculate moving averages
            enhanced_data = self._calculate_moving_averages(enhanced_data)

            # Calculate volume indicators
            enhanced_data = self._calculate_volume_indicators(enhanced_data)

            # Calculate volatility measures
            enhanced_data = self._calculate_volatility(enhanced_data)

            # Calculate support and resistance levels
            enhanced_data = self._calculate_support_resistance(enhanced_data)

            # Calculate price change percentages
            enhanced_data = self._calculate_price_changes(enhanced_data)

            logger.debug("Technical indicators calculated successfully")
            return enhanced_data

        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            raise

    def _calculate_moving_averages(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate simple moving averages"""
        try:
            # Simple Moving Averages
            data["SMA_20"] = data["Close"].rolling(window=20).mean()
            data["SMA_50"] = data["Close"].rolling(window=50).mean()

            # Exponential Moving Averages (optional for future use)
            data["EMA_12"] = data["Close"].ewm(span=12).mean()
            data["EMA_26"] = data["Close"].ewm(span=26).mean()

            return data
        except Exception as e:
            logger.error(f"Error calculating moving averages: {str(e)}")
            raise

    def _calculate_volume_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume-based indicators"""
        try:
            # Volume moving average
            data["Volume_MA_20"] = data["Volume"].rolling(window=20).mean()

            # Volume Rate of Change
            data["Volume_ROC"] = data["Volume"].pct_change()

            # On-Balance Volume (OBV)
            data["OBV"] = self._calculate_obv(data)

            return data
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {str(e)}")
            raise

    def _calculate_volatility(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate volatility measures"""
        try:
            # Price volatility (standard deviation)
            data["Price_Volatility"] = data["Close"].rolling(window=20).std()

            # Average True Range (ATR)
            data["ATR"] = self._calculate_atr(data)

            return data
        except Exception as e:
            logger.error(f"Error calculating volatility: {str(e)}")
            raise

    def _calculate_support_resistance(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate support and resistance levels"""
        try:
            # Rolling maximum (resistance) and minimum (support)
            data["Resistance"] = data["High"].rolling(window=20).max()
            data["Support"] = data["Low"].rolling(window=20).min()

            # Pivot points (optional for future use)
            data["Pivot"] = (data["High"] + data["Low"] + data["Close"]) / 3

            return data
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {str(e)}")
            raise

    def _calculate_price_changes(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate price change percentages and ratios"""
        try:
            # Daily price change percentage
            data["Price_Change_Pct"] = data["Close"].pct_change()

            # Price change from SMA
            data["Price_vs_SMA20"] = (data["Close"] - data["SMA_20"]) / data["SMA_20"]
            data["Price_vs_SMA50"] = (data["Close"] - data["SMA_50"]) / data["SMA_50"]

            return data
        except Exception as e:
            logger.error(f"Error calculating price changes: {str(e)}")
            raise

    def _calculate_obv(self, data: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume"""
        try:
            obv = np.zeros(len(data))

            for i in range(1, len(data)):
                if data["Close"].iloc[i] > data["Close"].iloc[i - 1]:
                    obv[i] = obv[i - 1] + data["Volume"].iloc[i]
                elif data["Close"].iloc[i] < data["Close"].iloc[i - 1]:
                    obv[i] = obv[i - 1] - data["Volume"].iloc[i]
                else:
                    obv[i] = obv[i - 1]

            return pd.Series(obv, index=data.index)
        except Exception as e:
            logger.error(f"Error calculating OBV: {str(e)}")
            return pd.Series(np.zeros(len(data)), index=data.index)

    def _calculate_atr(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        try:
            # True Range calculation
            high_low = data["High"] - data["Low"]
            high_close_prev = np.abs(data["High"] - data["Close"].shift(1))
            low_close_prev = np.abs(data["Low"] - data["Close"].shift(1))

            true_range = np.maximum(
                high_low, np.maximum(high_close_prev, low_close_prev)
            )

            # Average True Range
            atr = pd.Series(true_range).rolling(window=window).mean()
            atr.index = data.index

            return atr
        except Exception as e:
            logger.error(f"Error calculating ATR: {str(e)}")
            return pd.Series(np.zeros(len(data)), index=data.index)

    def get_latest_indicators(self, data: pd.DataFrame) -> dict[str, Any]:
        """
        Get latest values of all indicators

        Args:
            data (pd.DataFrame): Data with calculated indicators

        Returns:
            Dict[str, Any]: Dictionary of latest indicator values
        """
        try:
            if len(data) == 0:
                return {}

            latest = data.iloc[-1]

            indicators = {
                "sma_20": latest.get("SMA_20", 0),
                "sma_50": latest.get("SMA_50", 0),
                "volume_ma_20": latest.get("Volume_MA_20", 0),
                "price_volatility": latest.get("Price_Volatility", 0),
                "resistance": latest.get("Resistance", 0),
                "support": latest.get("Support", 0),
                "atr": latest.get("ATR", 0),
                "obv": latest.get("OBV", 0),
                "price_change_pct": latest.get("Price_Change_Pct", 0),
                "price_vs_sma20": latest.get("Price_vs_SMA20", 0),
                "price_vs_sma50": latest.get("Price_vs_SMA50", 0),
            }

            return indicators

        except Exception as e:
            logger.error(f"Error getting latest indicators: {str(e)}")
            return {}
