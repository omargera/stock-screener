"""
Stock data gateway for fetching data from external APIs
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class StockDataGateway(ABC):
    """Abstract base class for stock data gateways"""

    @abstractmethod
    def fetch_stock_data(self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """Fetch stock data for a symbol"""
        pass


class YahooFinanceGateway(StockDataGateway):
    """Gateway for fetching stock data from Yahoo Finance"""

    def __init__(self):
        self.session = None

    def fetch_stock_data(
        self, symbol: str, period: str = "3mo"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch stock data from Yahoo Finance

        Args:
            symbol (str): Stock symbol (e.g., 'AAPL')
            period (str): Time period (1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            pd.DataFrame: Stock data with OHLCV information, or None if failed
        """
        try:
            logger.info(f"Fetching data for {symbol} with period {period}")

            # Create ticker object
            ticker = yf.Ticker(symbol)

            # Fetch historical data
            data = ticker.history(period=period)

            # Validate data
            if data.empty:
                logger.warning(f"No data found for symbol: {symbol}")
                return None

            # Check for required columns
            required_columns = ["Open", "High", "Low", "Close", "Volume"]
            missing_columns = [
                col for col in required_columns if col not in data.columns
            ]

            if missing_columns:
                logger.error(
                    f"Missing required columns for {symbol}: {missing_columns}"
                )
                return None

            # Validate data quality
            if self._validate_data_quality(data, symbol):
                logger.info(
                    f"Successfully fetched {len(data)} rows of data for {symbol}"
                )
                return data
            else:
                logger.warning(f"Data quality validation failed for {symbol}")
                return None

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def _validate_data_quality(self, data: pd.DataFrame, symbol: str) -> bool:
        """
        Validate the quality of fetched data

        Args:
            data (pd.DataFrame): Stock data to validate
            symbol (str): Stock symbol for logging

        Returns:
            bool: True if data passes quality checks
        """
        try:
            # Check for minimum data points
            if len(data) < 20:
                logger.warning(f"Insufficient data points for {symbol}: {len(data)}")
                return False

            # Check for null values in critical columns
            critical_columns = ["Close", "Volume"]
            for col in critical_columns:
                null_count = data[col].isnull().sum()
                if null_count > 0:
                    logger.warning(
                        f"Found {null_count} null values in {col} for {symbol}"
                    )
                    # Allow some null values but not too many
                    if null_count > len(data) * 0.1:  # More than 10% null
                        return False

            # Check for reasonable price ranges
            close_prices = data["Close"].dropna()
            if len(close_prices) > 0:
                min_price = close_prices.min()
                max_price = close_prices.max()

                # Basic sanity checks
                if min_price <= 0:
                    logger.warning(
                        f"Invalid price data for {symbol}: min price {min_price}"
                    )
                    return False

                if max_price / min_price > 100:  # Price changed more than 100x
                    logger.warning(
                        f"Suspicious price range for {symbol}: {min_price} to {max_price}"
                    )
                    # This might be valid for some stocks, so just warn but don't fail

            # Check for reasonable volume
            volumes = data["Volume"].dropna()
            if len(volumes) > 0 and volumes.sum() == 0:
                logger.warning(f"No volume data for {symbol}")
                # Some stocks might have no volume, so don't fail

            return True

        except Exception as e:
            logger.error(f"Error validating data for {symbol}: {str(e)}")
            return False

    def get_stock_info(self, symbol: str) -> Optional[dict]:
        """
        Get additional stock information

        Args:
            symbol (str): Stock symbol

        Returns:
            dict: Stock information or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if info:
                # Extract relevant information
                return {
                    "shortName": info.get("shortName", symbol),
                    "longName": info.get("longName", ""),
                    "sector": info.get("sector", ""),
                    "industry": info.get("industry", ""),
                    "marketCap": info.get("marketCap", 0),
                    "currency": info.get("currency", "USD"),
                }

            return None

        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {str(e)}")
            return None

    def test_connection(self) -> bool:
        """
        Test connection to Yahoo Finance

        Returns:
            bool: True if connection is working
        """
        try:
            # Try to fetch data for a well-known stock
            test_data = self.fetch_stock_data("AAPL", "5d")
            return test_data is not None and not test_data.empty
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
