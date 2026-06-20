"""Data models for lighting."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DimmingCurve(str, Enum):
    """Dimming curve type."""
    FLAT = "flat"
    LINEAR = "linear"
    SINUSOIDAL = "sinusoidal"


@dataclass
class LightingSetpoint:
    """Lighting control setpoint."""
    photoperiod_hours: float = 16.0
    dli_mol_per_m2_per_day: float = 12.0
    onset_time: str = "06:00"
    offset_time: str = "22:00"
    dimming_curve: DimmingCurve = DimmingCurve.FLAT
    max_intensity_pct: float = 100.0

    def __post_init__(self):
        if not 0 <= self.photoperiod_hours <= 24:
            raise ValueError("photoperiod_hours must be between 0 and 24")
        if not 0 <= self.dli_mol_per_m2_per_day <= 100:
            raise ValueError("dli_mol_per_m2_per_day must be between 0 and 100")
        if not 0 <= self.max_intensity_pct <= 100:
            raise ValueError("max_intensity_pct must be between 0 and 100")


@dataclass
class FixtureSpec:
    """LED fixture specification."""
    fixture_id: str = ""
    wattage_per_m2: float = 400.0
    ppf_per_watt: float = 2.5
    spectrum_k: Optional[int] = None

    def __post_init__(self):
        if not self.fixture_id:
            raise ValueError("fixture_id is required")
        if self.wattage_per_m2 <= 0:
            raise ValueError("wattage_per_m2 must be positive")
        if self.ppf_per_watt <= 0:
            raise ValueError("ppf_per_watt must be positive")
