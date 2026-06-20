"""DLI and photoperiod calculations."""

from __future__ import annotations

from datetime import datetime, time

from pyfarm.lighting.models import DimmingCurve, FixtureSpec, LightingSetpoint


class LightingCalculator:
    """Calculates lighting parameters based on DLI and fixtures."""

    @staticmethod
    def dli_to_runtime_hours(
        dli_target: float,
        fixture: FixtureSpec,
        intensity_pct: float = 100.0,
    ) -> float:
        """Calculate runtime hours needed to achieve target DLI.

        Args:
            dli_target: Target DLI in mol/m²/day
            fixture: LED fixture specification
            intensity_pct: Intensity as percentage (0-100)

        Returns:
            Runtime hours needed
        """
        if fixture.ppf_per_watt <= 0 or fixture.wattage_per_m2 <= 0:
            return 0.0

        # PPF = watts/m² * ppf/watt * intensity%
        ppf = (fixture.wattage_per_m2 * fixture.ppf_per_watt * intensity_pct) / 100.0

        # Moles = PPF * time_hours / 3600
        # DLI = Moles (for 1 m²)
        # time = DLI * 3600 / PPF
        if ppf <= 0:
            return 0.0

        hours = (dli_target * 3600.0) / ppf
        return min(hours, 24.0)

    @staticmethod
    def photoperiod_hours_to_schedule(
        photoperiod: float,
        onset: str = "06:00",
        offset: str = "22:00",
    ) -> tuple[time, time]:
        """Convert photoperiod duration to on/off times.

        Args:
            photoperiod: Hours of light per day
            onset: Desired light start time (HH:MM)
            offset: Desired light end time (HH:MM)

        Returns:
            Tuple of (start_time, end_time) as time objects
        """
        onset_parts = onset.split(":")
        offset_parts = offset.split(":")

        start = time(int(onset_parts[0]), int(onset_parts[1]))
        end = time(int(offset_parts[0]), int(offset_parts[1]))

        return start, end

    @staticmethod
    def apply_dimming_curve(
        intensity: float,
        curve_type: DimmingCurve,
        progress: float,
    ) -> float:
        """Apply dimming curve to intensity.

        Args:
            intensity: Base intensity (0-100)
            curve_type: Type of dimming curve
            progress: Progress through photoperiod (0-1)

        Returns:
            Adjusted intensity (0-100)
        """
        if curve_type == DimmingCurve.FLAT:
            return intensity

        if curve_type == DimmingCurve.LINEAR:
            # Linear ramp up and down
            if progress < 0.5:
                return intensity * (progress * 2)
            else:
                return intensity * ((1 - progress) * 2)

        if curve_type == DimmingCurve.SINUSOIDAL:
            # Smooth sinusoidal curve
            import math

            return intensity * math.sin(progress * math.pi)

        return intensity
