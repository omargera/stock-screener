"""
Test data generator for creating sample stock data scenarios
"""

from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd


class StockDataGenerator:
    """Generator for creating sample stock data for testing"""

    def __init__(self, symbol: str = "TEST", base_price: float = 100.0):
        self.symbol = symbol
        self.base_price = base_price

    def generate_basic_data(
        self, days: int = 60, start_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Generate basic OHLCV data with realistic patterns

        Args:
            days (int): Number of days of data
            start_date (datetime, optional): Start date for data

        Returns:
            pd.DataFrame: Basic stock data
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=days)

        dates = pd.date_range(start=start_date, periods=days, freq="D")

        # Generate realistic price movement
        np.random.seed(42)  # For reproducible tests
        daily_returns = np.random.normal(0.001, 0.02, days)  # 0.1% mean, 2% volatility

        prices = [self.base_price]
        for i in range(1, days):
            price = prices[-1] * (1 + daily_returns[i])
            prices.append(max(price, 1.0))  # Ensure price doesn't go below $1

        # Generate OHLC from close prices
        data = []
        for i, (_date, close) in enumerate(zip(dates, prices)):
            # Add some intraday volatility
            volatility = close * 0.02  # 2% intraday range
            high = close + np.random.uniform(0, volatility)
            low = close - np.random.uniform(0, volatility)
            open_price = close + np.random.uniform(-volatility / 2, volatility / 2)

            # Ensure OHLC relationships are valid
            high = max(high, open_price, close)
            low = min(low, open_price, close)

            # Generate volume (higher volume on larger price moves)
            base_volume = 1000000
            volume_multiplier = 1 + abs(daily_returns[i]) * 10
            volume = int(base_volume * volume_multiplier * np.random.uniform(0.5, 1.5))

            data.append(
                {
                    "Open": round(open_price, 2),
                    "High": round(high, 2),
                    "Low": round(low, 2),
                    "Close": round(close, 2),
                    "Volume": volume,
                }
            )

        df = pd.DataFrame(data, index=dates)
        return df

    def generate_resistance_breakout_scenario(self) -> pd.DataFrame:
        """
        Generate data with a clear resistance breakout pattern

        Returns:
            pd.DataFrame: Data showing resistance breakout
        """
        data = self.generate_basic_data(60)

        # Create resistance level around day 40-50
        resistance_level = self.base_price * 1.10

        # Days 30-50: Price approaches but doesn't break resistance
        for i in range(30, 50):
            data.iloc[i, data.columns.get_loc("High")] = min(
                data.iloc[i]["High"], resistance_level - 0.50
            )
            data.iloc[i, data.columns.get_loc("Close")] = min(
                data.iloc[i]["Close"], resistance_level - 1.00
            )

        # Day 55: Breakout with high volume
        breakout_day = 55
        data.iloc[breakout_day, data.columns.get_loc("High")] = resistance_level + 2.00
        data.iloc[breakout_day, data.columns.get_loc("Close")] = resistance_level + 1.50
        data.iloc[breakout_day, data.columns.get_loc("Volume")] = int(
            data.iloc[breakout_day]["Volume"] * 3.0  # 3x volume spike
        )

        # Days after breakout: Maintain higher levels
        for i in range(breakout_day + 1, len(data)):
            # Ensure price stays above resistance level
            data.iloc[i, data.columns.get_loc("Close")] = (
                resistance_level + 1.0 + (i - breakout_day) * 0.5
            )
            data.iloc[i, data.columns.get_loc("High")] = data.iloc[i]["Close"] + 1.0
            data.iloc[i, data.columns.get_loc("Low")] = max(
                data.iloc[i]["Low"], resistance_level
            )

        return data

    def generate_ma_breakout_scenario(self) -> pd.DataFrame:
        """
        Generate data with moving average breakout pattern

        Returns:
            pd.DataFrame: Data showing MA breakout
        """
        data = self.generate_basic_data(60)

        # Create a more controlled pattern for MA breakout
        # Days 0-40: Higher prices to establish higher SMA_50
        for i in range(40):
            price = self.base_price * (1.02 - i * 0.005)  # Gradual decline from higher level
            data.iloc[i, data.columns.get_loc("Close")] = price
            data.iloc[i, data.columns.get_loc("High")] = price * 1.01
            data.iloc[i, data.columns.get_loc("Low")] = price * 0.99
            data.iloc[i, data.columns.get_loc("Open")] = price

        # Days 40-58: Lower consolidation to create SMA_20 < SMA_50 but recent recovery
        consolidation_price = self.base_price * 0.87
        for i in range(40, 58):
            # Gradual recovery but still below what will become SMA_20
            recovery_factor = (i - 40) / 18 * 0.08  # Gradual 8% recovery over 18 days
            price = consolidation_price + recovery_factor * self.base_price
            data.iloc[i, data.columns.get_loc("Close")] = price
            data.iloc[i, data.columns.get_loc("High")] = price * 1.01
            data.iloc[i, data.columns.get_loc("Low")] = price * 0.99
            data.iloc[i, data.columns.get_loc("Open")] = price

        # Day 58: Make sure this is clearly below SMA_20
        pre_breakout_price = self.base_price * 0.87  # Lower to ensure below SMA_20
        data.iloc[58, data.columns.get_loc("Close")] = pre_breakout_price
        data.iloc[58, data.columns.get_loc("High")] = pre_breakout_price * 1.01
        data.iloc[58, data.columns.get_loc("Low")] = pre_breakout_price * 0.99
        data.iloc[58, data.columns.get_loc("Open")] = pre_breakout_price

        # Day 59 (last day): Clear MA breakout with volume
        breakout_price = self.base_price * 0.98  # Above SMA_20 but reasonable
        data.iloc[59, data.columns.get_loc("Close")] = breakout_price
        data.iloc[59, data.columns.get_loc("High")] = breakout_price * 1.02
        data.iloc[59, data.columns.get_loc("Low")] = breakout_price * 0.98
        data.iloc[59, data.columns.get_loc("Volume")] = int(
            data.iloc[59]["Volume"] * 2.5
        )

        return data

    def generate_volume_spike_scenario(self) -> pd.DataFrame:
        """
        Generate data with volume spike but no breakout

        Returns:
            pd.DataFrame: Data showing volume spike
        """
        data = self.generate_basic_data(60)

        # Day 55: Volume spike without significant price change
        spike_day = 55
        data.iloc[spike_day, data.columns.get_loc("Volume")] = int(
            data.iloc[spike_day]["Volume"] * 4.0  # 4x volume spike
        )

        # Keep price relatively stable
        avg_price = data.iloc[50:55]["Close"].mean()
        data.iloc[spike_day, data.columns.get_loc("Close")] = (
            avg_price * 1.005
        )  # Minimal price change

        return data

    def generate_no_signal_scenario(self) -> pd.DataFrame:
        """
        Generate data with no signals (normal trading)

        Returns:
            pd.DataFrame: Data with no significant signals
        """
        data = self.generate_basic_data(60)

        # Ensure no volume spikes or breakouts
        # Normalize volume to avoid spikes - very tight range
        avg_volume = data["Volume"].mean()
        data["Volume"] = [
            int(avg_volume * np.random.uniform(0.8, 1.2)) for _ in range(len(data))
        ]

        # Keep price completely flat to prevent any breakouts
        # No trend, no variation - just flat trading
        flat_price = self.base_price * 0.99  # Fixed price slightly below base
        
        for i in range(len(data)):
            # Completely flat with minimal noise
            noise = np.random.uniform(-0.01, 0.01)  # Only 1% noise
            price = flat_price * (1 + noise)
            
            data.iloc[i, data.columns.get_loc("Close")] = price
            data.iloc[i, data.columns.get_loc("High")] = price * 1.002  # Tiny high
            data.iloc[i, data.columns.get_loc("Low")] = price * 0.998   # Tiny low
            data.iloc[i, data.columns.get_loc("Open")] = price

        return data

    def generate_false_breakout_scenario(self) -> pd.DataFrame:
        """
        Generate data with false breakout (should not trigger signal)

        Returns:
            pd.DataFrame: Data showing false breakout
        """
        data = self.generate_basic_data(60)

        resistance_level = self.base_price * 1.10

        # Create resistance level
        for i in range(30, 50):
            data.iloc[i, data.columns.get_loc("High")] = min(
                data.iloc[i]["High"], resistance_level
            )

        # Day 55: Brief breakout but low volume
        breakout_day = 55
        data.iloc[breakout_day, data.columns.get_loc("High")] = resistance_level + 1.00
        data.iloc[breakout_day, data.columns.get_loc("Close")] = (
            resistance_level - 0.50
        )  # Close back below
        data.iloc[breakout_day, data.columns.get_loc("Volume")] = int(
            data.iloc[breakout_day]["Volume"] * 0.8  # Lower volume
        )

        return data


def generate_test_scenarios() -> dict[str, pd.DataFrame]:
    """
    Generate all test scenarios

    Returns:
        Dict[str, pd.DataFrame]: Dictionary of test scenarios
    """
    generator = StockDataGenerator()

    scenarios = {
        "resistance_breakout": generator.generate_resistance_breakout_scenario(),
        "ma_breakout": generator.generate_ma_breakout_scenario(),
        "volume_spike": generator.generate_volume_spike_scenario(),
        "no_signal": generator.generate_no_signal_scenario(),
        "false_breakout": generator.generate_false_breakout_scenario(),
    }

    return scenarios


def save_test_scenarios(output_dir: str = "tests/data") -> None:
    """
    Save test scenarios to CSV files

    Args:
        output_dir (str): Directory to save test data
    """
    import os

    os.makedirs(output_dir, exist_ok=True)

    scenarios = generate_test_scenarios()

    for name, data in scenarios.items():
        filepath = os.path.join(output_dir, f"{name}.csv")
        data.to_csv(filepath)
        print(f"Saved {name} scenario to {filepath}")


if __name__ == "__main__":
    # Generate and save test scenarios
    save_test_scenarios()
