"""
Signal models for representing trading signals
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SignalType(Enum):
    """Types of signals that can be detected"""

    RESISTANCE_BREAKOUT = "Resistance Breakout"
    MA_BREAKOUT = "MA Breakout"
    VOLUME_SPIKE = "Volume Spike"


@dataclass
class BreakoutSignal:
    """Represents a breakout signal"""

    signal: bool
    signal_type: Optional[SignalType]
    strength: float

    @classmethod
    def no_signal(cls) -> "BreakoutSignal":
        """Create a no-signal instance"""
        return cls(signal=False, signal_type=None, strength=0.0)

    @classmethod
    def resistance_breakout(cls, strength: float) -> "BreakoutSignal":
        """Create a resistance breakout signal"""
        return cls(
            signal=True, signal_type=SignalType.RESISTANCE_BREAKOUT, strength=strength
        )

    @classmethod
    def ma_breakout(cls, strength: float) -> "BreakoutSignal":
        """Create a moving average breakout signal"""
        return cls(signal=True, signal_type=SignalType.MA_BREAKOUT, strength=strength)


@dataclass
class VolumeSignal:
    """Represents a volume spike signal"""

    signal: bool
    volume_ratio: float

    @classmethod
    def no_signal(cls, volume_ratio: float = 0.0) -> "VolumeSignal":
        """Create a no-signal instance"""
        return cls(signal=False, volume_ratio=volume_ratio)

    @classmethod
    def volume_spike(cls, volume_ratio: float) -> "VolumeSignal":
        """Create a volume spike signal"""
        return cls(signal=True, volume_ratio=volume_ratio)


@dataclass
class CombinedSignals:
    """Container for all signals detected for a stock"""

    breakout: BreakoutSignal
    volume: VolumeSignal

    @property
    def has_any_signal(self) -> bool:
        """Check if any signal is detected"""
        return self.breakout.signal or self.volume.signal

    @property
    def signal_count(self) -> int:
        """Count of active signals"""
        count = 0
        if self.breakout.signal:
            count += 1
        if self.volume.signal:
            count += 1
        return count
