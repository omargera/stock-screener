"""
Signal detection service for identifying trading signals
"""

import logging

import pandas as pd

from models.signals import BreakoutSignal, CombinedSignals, VolumeSignal

logger = logging.getLogger(__name__)


class SignalDetectionService:
    """Service for detecting various trading signals"""

    def __init__(
        self, volume_spike_threshold: float = 2.0, breakout_threshold: float = 0.02
    ):
        """
        Initialize signal detection service

        Args:
            volume_spike_threshold (float): Multiplier for average volume to detect spikes
            breakout_threshold (float): Percentage threshold for breakout detection
        """
        self.volume_spike_threshold = volume_spike_threshold
        self.breakout_threshold = breakout_threshold

    def detect_all_signals(self, data: pd.DataFrame) -> CombinedSignals:
        """
        Detect all signals for the given stock data

        Args:
            data (pd.DataFrame): Stock data with technical indicators

        Returns:
            CombinedSignals: Combined signal results
        """
        try:
            logger.debug("Detecting all signals")

            # Detect breakout signals
            breakout_signal = self.detect_breakout_signals(data)

            # Detect volume signals
            volume_signal = self.detect_volume_signals(data)

            return CombinedSignals(breakout=breakout_signal, volume=volume_signal)

        except Exception as e:
            logger.error(f"Error detecting signals: {str(e)}")
            # Return no signals in case of error
            return CombinedSignals(
                breakout=BreakoutSignal.no_signal(), volume=VolumeSignal.no_signal()
            )

    def detect_breakout_signals(self, data: pd.DataFrame) -> BreakoutSignal:
        """
        Detect breakout patterns

        Args:
            data (pd.DataFrame): Stock data with technical indicators

        Returns:
            BreakoutSignal: Breakout signal information
        """
        try:
            if len(data) < 21:  # Need enough data for calculations
                logger.debug("Insufficient data for breakout detection")
                return BreakoutSignal.no_signal()

            latest = data.iloc[-1]
            previous = data.iloc[-2]

            # Check for resistance breakout (using full data context)
            resistance_breakout, resistance_strength = (
                self._check_resistance_breakout_with_data(data)
            )

            if resistance_breakout:
                logger.info(
                    f"Resistance breakout detected with strength: {resistance_strength:.2%}"
                )
                return BreakoutSignal.resistance_breakout(resistance_strength)

            # Check for moving average breakout
            ma_breakout, ma_strength = self._check_ma_breakout(latest, previous)

            if ma_breakout:
                logger.info(f"MA breakout detected with strength: {ma_strength:.2%}")
                return BreakoutSignal.ma_breakout(ma_strength)

            return BreakoutSignal.no_signal()

        except Exception as e:
            logger.error(f"Error detecting breakout signals: {str(e)}")
            return BreakoutSignal.no_signal()

    def detect_volume_signals(self, data: pd.DataFrame) -> VolumeSignal:
        """
        Detect volume spikes

        Args:
            data (pd.DataFrame): Stock data with volume information

        Returns:
            VolumeSignal: Volume spike signal information
        """
        try:
            if len(data) < 21:  # Need enough data for calculations
                logger.debug("Insufficient data for volume spike detection")
                return VolumeSignal.no_signal()

            # Look for volume spikes in recent days (last 5 days)
            max_volume_ratio = 0.0
            spike_detected = False

            lookback_days = min(5, len(data))

            for i in range(1, lookback_days + 1):
                day_data = data.iloc[-i]

                # Calculate volume ratio for this day
                if day_data["Volume_MA_20"] > 0:
                    volume_ratio = day_data["Volume"] / day_data["Volume_MA_20"]
                else:
                    volume_ratio = 0

                max_volume_ratio = max(max_volume_ratio, volume_ratio)

                # Check for volume spike
                if volume_ratio >= self.volume_spike_threshold:
                    spike_detected = True
                    logger.info(
                        f"Volume spike detected on recent day: {volume_ratio:.1f}x average"
                    )

            if spike_detected:
                return VolumeSignal.volume_spike(max_volume_ratio)

            # If no spike detected, return current day ratio for reference
            latest = data.iloc[-1]
            current_ratio = (
                latest["Volume"] / latest["Volume_MA_20"]
                if latest["Volume_MA_20"] > 0
                else 0
            )

            return VolumeSignal.no_signal(current_ratio)

        except Exception as e:
            logger.error(f"Error detecting volume signals: {str(e)}")
            return VolumeSignal.no_signal()

    def _check_resistance_breakout(
        self, latest: pd.Series, previous: pd.Series
    ) -> tuple[bool, float]:
        """
        Check for resistance breakout pattern

        Args:
            latest (pd.Series): Latest data point
            previous (pd.Series): Previous data point

        Returns:
            Tuple[bool, float]: (is_breakout, strength)
        """
        try:
            # Conditions for resistance breakout:
            # 1. Current price breaks above resistance with threshold
            # 2. Previous price was below resistance
            # 3. Volume confirmation (>1.2x average)

            resistance_threshold = latest["Resistance"] * (1 - self.breakout_threshold)

            price_breakout = (
                latest["Close"] > resistance_threshold
                and previous["Close"] <= previous["Resistance"]
            )

            volume_confirmation = latest["Volume"] > latest["Volume_MA_20"] * 1.2

            if price_breakout and volume_confirmation:
                # Calculate breakout strength
                strength = (latest["Close"] - latest["Resistance"]) / latest[
                    "Resistance"
                ]
                return True, max(0, strength)  # Ensure non-negative strength

            return False, 0.0

        except Exception as e:
            logger.error(f"Error checking resistance breakout: {str(e)}")
            return False, 0.0

    def _check_resistance_breakout_with_data(
        self, data: pd.DataFrame
    ) -> tuple[bool, float]:
        """
        Check for resistance breakout pattern with full data context

        Args:
            data (pd.DataFrame): Full stock data with indicators

        Returns:
            Tuple[bool, float]: (is_breakout, strength)
        """
        try:
            if len(data) < 2:
                return False, 0.0

            latest = data.iloc[-1]

            # Check if current price is above resistance threshold
            resistance_threshold = latest["Resistance"] * (1 - self.breakout_threshold)
            current_above_resistance = latest["Close"] > resistance_threshold

            if not current_above_resistance:
                return False, 0.0

            # Look for recent volume confirmation (within last 5 days)
            volume_confirmation = False
            lookback_days = min(5, len(data))

            for i in range(1, lookback_days + 1):
                day_data = data.iloc[-i]
                if day_data["Volume"] > day_data["Volume_MA_20"] * 1.2:
                    volume_confirmation = True
                    break

            # Check that price recently broke above resistance
            recent_breakout = False
            for i in range(1, min(5, len(data))):
                current_day = data.iloc[-i]
                if i < len(data) - 1:
                    prev_day = data.iloc[-i - 1]
                    if (
                        current_day["Close"]
                        > current_day["Resistance"] * (1 - self.breakout_threshold)
                        and prev_day["Close"] <= prev_day["Resistance"]
                    ):
                        recent_breakout = True
                        break

            if recent_breakout and volume_confirmation:
                # Calculate breakout strength
                strength = (latest["Close"] - latest["Resistance"]) / latest[
                    "Resistance"
                ]
                return True, max(0, strength)  # Ensure non-negative strength

            return False, 0.0

        except Exception as e:
            logger.error(f"Error checking resistance breakout with data: {str(e)}")
            return False, 0.0

    def _check_ma_breakout(
        self, latest: pd.Series, previous: pd.Series
    ) -> tuple[bool, float]:
        """
        Check for moving average breakout pattern

        Args:
            latest (pd.Series): Latest data point
            previous (pd.Series): Previous data point

        Returns:
            Tuple[bool, float]: (is_breakout, strength)
        """
        try:
            # Conditions for MA breakout:
            # 1. Current price breaks above SMA 20
            # 2. Previous price was below SMA 20
            # 3. SMA 20 > SMA 50 (uptrend confirmation)

            price_above_sma = latest["Close"] > latest["SMA_20"]
            previous_below_sma = previous["Close"] <= previous["SMA_20"]
            uptrend_confirmation = latest["SMA_20"] > latest["SMA_50"]

            if price_above_sma and previous_below_sma and uptrend_confirmation:
                # Calculate breakout strength
                strength = (latest["Close"] - latest["SMA_20"]) / latest["SMA_20"]
                return True, max(0, strength)  # Ensure non-negative strength

            return False, 0.0

        except Exception as e:
            logger.error(f"Error checking MA breakout: {str(e)}")
            return False, 0.0

    def analyze_signal_quality(
        self, signals: CombinedSignals, data: pd.DataFrame
    ) -> dict:
        """
        Analyze the quality and reliability of detected signals

        Args:
            signals (CombinedSignals): Detected signals
            data (pd.DataFrame): Stock data with indicators

        Returns:
            dict: Signal quality analysis
        """
        try:
            if len(data) == 0:
                return {"quality": "unknown", "confidence": 0.0}

            latest = data.iloc[-1]
            quality_score = 0.0
            factors = []

            # Volume confirmation
            if latest["Volume"] > latest["Volume_MA_20"] * 1.5:
                quality_score += 0.3
                factors.append("strong_volume")
            elif latest["Volume"] > latest["Volume_MA_20"]:
                quality_score += 0.15
                factors.append("good_volume")

            # Trend confirmation
            if latest["SMA_20"] > latest["SMA_50"]:
                quality_score += 0.2
                factors.append("uptrend")

            # Volatility check (not too volatile)
            avg_price = latest["SMA_20"]
            if (
                avg_price > 0 and latest["Price_Volatility"] / avg_price < 0.05
            ):  # Less than 5% volatility
                quality_score += 0.2
                factors.append("low_volatility")

            # Signal strength
            if (
                signals.breakout.signal and signals.breakout.strength > 0.03
            ):  # >3% breakout
                quality_score += 0.3
                factors.append("strong_breakout")

            # Determine quality level
            if quality_score >= 0.8:
                quality = "excellent"
            elif quality_score >= 0.6:
                quality = "good"
            elif quality_score >= 0.4:
                quality = "fair"
            else:
                quality = "poor"

            return {
                "quality": quality,
                "confidence": quality_score,
                "factors": factors,
                "score": quality_score,
            }

        except Exception as e:
            logger.error(f"Error analyzing signal quality: {str(e)}")
            return {"quality": "unknown", "confidence": 0.0}
