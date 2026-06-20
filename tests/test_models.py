"""Tests for lighting models."""

import pytest

from pyfarm.lighting.models import DimmingCurve, FixtureSpec, LightingSetpoint


def test_lighting_setpoint_creation():
    setpoint = LightingSetpoint(
        photoperiod_hours=16.0,
        dli_mol_per_m2_per_day=12.0,
    )
    assert setpoint.photoperiod_hours == 16.0
    assert setpoint.dli_mol_per_m2_per_day == 12.0


def test_lighting_setpoint_invalid_photoperiod():
    with pytest.raises(ValueError):
        LightingSetpoint(photoperiod_hours=25.0)


def test_lighting_setpoint_invalid_dli():
    with pytest.raises(ValueError):
        LightingSetpoint(dli_mol_per_m2_per_day=150.0)


def test_fixture_spec_creation():
    fixture = FixtureSpec(fixture_id="led-1", wattage_per_m2=400.0)
    assert fixture.fixture_id == "led-1"
    assert fixture.wattage_per_m2 == 400.0


def test_fixture_spec_invalid():
    with pytest.raises(ValueError):
        FixtureSpec(fixture_id="", wattage_per_m2=400.0)
