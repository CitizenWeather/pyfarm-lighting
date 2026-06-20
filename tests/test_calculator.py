"""Tests for pyfarm-lighting LightingCalculator."""

import math
from datetime import time

import pytest

from pyfarm.lighting.calculator import LightingCalculator
from pyfarm.lighting.models import DimmingCurve, FixtureSpec, LightingSetpoint


class TestDLIToRuntimeHours:
    """Test LightingCalculator.dli_to_runtime_hours()."""

    def test_basic_calculation(self):
        fixture = FixtureSpec(fixture_id="400W", wattage_per_m2=400, ppf_per_watt=2.5)
        hours = LightingCalculator.dli_to_runtime_hours(8.0, fixture)
        assert hours > 0
        assert hours <= 24.0

    def test_dli_scaling(self):
        fixture = FixtureSpec(fixture_id="400W", wattage_per_m2=400, ppf_per_watt=2.5)
        hours_8 = LightingCalculator.dli_to_runtime_hours(8.0, fixture)
        hours_16 = LightingCalculator.dli_to_runtime_hours(16.0, fixture)
        assert hours_16 > hours_8

    def test_fixture_wattage_effect(self):
        fixture_400 = FixtureSpec(fixture_id="400W", wattage_per_m2=400, ppf_per_watt=2.5)
        fixture_600 = FixtureSpec(fixture_id="600W", wattage_per_m2=600, ppf_per_watt=2.5)

        hours_400 = LightingCalculator.dli_to_runtime_hours(12.0, fixture_400)
        hours_600 = LightingCalculator.dli_to_runtime_hours(12.0, fixture_600)

        assert hours_600 < hours_400  # Higher wattage needs less time

    def test_ppf_per_watt_effect(self):
        fixture_low = FixtureSpec(fixture_id="low", wattage_per_m2=400, ppf_per_watt=2.0)
        fixture_high = FixtureSpec(fixture_id="high", wattage_per_m2=400, ppf_per_watt=3.0)

        hours_low = LightingCalculator.dli_to_runtime_hours(12.0, fixture_low)
        hours_high = LightingCalculator.dli_to_runtime_hours(12.0, fixture_high)

        assert hours_high < hours_low  # Higher efficiency needs less time

    def test_intensity_percentage(self):
        fixture = FixtureSpec(fixture_id="400W", wattage_per_m2=400, ppf_per_watt=2.5)

        hours_100 = LightingCalculator.dli_to_runtime_hours(12.0, fixture, intensity_pct=100)
        hours_50 = LightingCalculator.dli_to_runtime_hours(12.0, fixture, intensity_pct=50)

        assert hours_50 > hours_100  # Lower intensity needs more time

    def test_zero_dli_target(self):
        fixture = FixtureSpec(fixture_id="400W", wattage_per_m2=400, ppf_per_watt=2.5)
        hours = LightingCalculator.dli_to_runtime_hours(0.0, fixture)
        assert hours == 0.0

    def test_24_hour_max(self):
        fixture = FixtureSpec(fixture_id="low-power", wattage_per_m2=10, ppf_per_watt=1.0)
        hours = LightingCalculator.dli_to_runtime_hours(100.0, fixture)  # Impossible high DLI
        assert hours == 24.0  # Capped at 24 hours

    def test_zero_wattage_returns_zero(self):
        fixture = FixtureSpec(fixture_id="broken", wattage_per_m2=0.0, ppf_per_watt=2.5)
        hours = LightingCalculator.dli_to_runtime_hours(12.0, fixture)
        assert hours == 0.0

    def test_zero_ppf_returns_zero(self):
        fixture = FixtureSpec(fixture_id="broken", wattage_per_m2=400, ppf_per_watt=0.0)
        hours = LightingCalculator.dli_to_runtime_hours(12.0, fixture)
        assert hours == 0.0


class TestPhotoperiodHoursToSchedule:
    """Test LightingCalculator.photoperiod_hours_to_schedule()."""

    def test_default_schedule(self):
        start, end = LightingCalculator.photoperiod_hours_to_schedule(16.0)
        assert start == time(6, 0)
        assert end == time(22, 0)

    def test_custom_onset(self):
        start, end = LightingCalculator.photoperiod_hours_to_schedule(
            16.0,
            onset="05:00",
            offset="21:00"
        )
        assert start == time(5, 0)
        assert end == time(21, 0)

    def test_various_photoperiods(self):
        for photoperiod in [8, 12, 16, 20, 24]:
            start, end = LightingCalculator.photoperiod_hours_to_schedule(photoperiod)
            assert isinstance(start, time)
            assert isinstance(end, time)

    def test_midnight_schedule(self):
        start, end = LightingCalculator.photoperiod_hours_to_schedule(
            12.0,
            onset="00:00",
            offset="12:00"
        )
        assert start == time(0, 0)
        assert end == time(12, 0)


class TestApplyDimmingCurve:
    """Test LightingCalculator.apply_dimming_curve()."""

    def test_flat_curve(self):
        for progress in [0.0, 0.25, 0.5, 0.75, 1.0]:
            intensity = LightingCalculator.apply_dimming_curve(
                100.0,
                DimmingCurve.FLAT,
                progress
            )
            assert intensity == 100.0

    def test_linear_curve_ramp_up(self):
        # First half: ramp up from 0 to 100
        for progress in [0.0, 0.25]:
            intensity = LightingCalculator.apply_dimming_curve(
                100.0,
                DimmingCurve.LINEAR,
                progress
            )
            assert 0 <= intensity <= 100.0

    def test_linear_curve_ramp_down(self):
        # Second half: ramp down from 100 to 0
        for progress in [0.75, 1.0]:
            intensity = LightingCalculator.apply_dimming_curve(
                100.0,
                DimmingCurve.LINEAR,
                progress
            )
            assert 0 <= intensity <= 100.0

    def test_linear_curve_peak(self):
        intensity = LightingCalculator.apply_dimming_curve(
            100.0,
            DimmingCurve.LINEAR,
            0.5
        )
        assert intensity == 100.0

    def test_sinusoidal_curve(self):
        # Peak at 0.5
        peak = LightingCalculator.apply_dimming_curve(
            100.0,
            DimmingCurve.SINUSOIDAL,
            0.5
        )
        assert peak == pytest.approx(100.0, abs=0.1)

        # Near zero at start/end
        start = LightingCalculator.apply_dimming_curve(
            100.0,
            DimmingCurve.SINUSOIDAL,
            0.0
        )
        end = LightingCalculator.apply_dimming_curve(
            100.0,
            DimmingCurve.SINUSOIDAL,
            1.0
        )
        assert start == pytest.approx(0.0, abs=0.1)
        assert end == pytest.approx(0.0, abs=0.1)

    def test_sinusoidal_curve_smooth(self):
        intensities = []
        for progress in [i / 10.0 for i in range(11)]:
            intensity = LightingCalculator.apply_dimming_curve(
                100.0,
                DimmingCurve.SINUSOIDAL,
                progress
            )
            intensities.append(intensity)

        # Should be smooth curve (monotonic increase then decrease)
        # Increase phase
        for i in range(5):
            assert intensities[i] <= intensities[i + 1]

    def test_scaled_intensity(self):
        intensity_50 = LightingCalculator.apply_dimming_curve(
            50.0,
            DimmingCurve.FLAT,
            0.5
        )
        assert intensity_50 == 50.0

    def test_intensity_percentage_scaling(self):
        intensity_100 = LightingCalculator.apply_dimming_curve(
            100.0,
            DimmingCurve.LINEAR,
            0.5
        )
        intensity_50 = LightingCalculator.apply_dimming_curve(
            50.0,
            DimmingCurve.LINEAR,
            0.5
        )
        assert intensity_50 == pytest.approx(intensity_100 / 2)
