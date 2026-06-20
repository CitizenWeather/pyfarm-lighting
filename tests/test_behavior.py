"""Tests for lighting behavior."""

import pytest

from pyfarm.crops import MemoryRegistry
from pyfarm.lighting import FixtureSpec, LightingBehavior


@pytest.mark.asyncio
async def test_lighting_setpoint_computation():
    registry = MemoryRegistry()
    behavior = LightingBehavior(registry)

    # Get setpoint for oyster mushroom fruiting stage
    setpoint = await behavior.compute_setpoint("oyster-grey-strain-a", current_stage_index=2)
    assert setpoint.dli_mol_per_m2_per_day == 8.0
    assert setpoint.photoperiod_hours > 0


@pytest.mark.asyncio
async def test_override_dli():
    registry = MemoryRegistry()
    behavior = LightingBehavior(registry)

    # Override DLI
    setpoint = await behavior.compute_setpoint(
        "oyster-grey-strain-a",
        current_stage_index=2,
        override_dli=12.0,
    )
    assert setpoint.dli_mol_per_m2_per_day == 12.0


@pytest.mark.asyncio
async def test_custom_fixture():
    registry = MemoryRegistry()
    behavior = LightingBehavior(registry)

    # Use higher-power fixture
    high_power = FixtureSpec(fixture_id="high-power", wattage_per_m2=800.0)
    setpoint = await behavior.compute_setpoint(
        "oyster-grey-strain-a",
        current_stage_index=2,
        fixture=high_power,
    )
    # Higher wattage should give shorter runtime for same DLI
    assert setpoint.photoperiod_hours > 0
    assert setpoint.photoperiod_hours <= 24


@pytest.mark.asyncio
async def test_microgreen_dli():
    registry = MemoryRegistry()
    behavior = LightingBehavior(registry)

    # Microgreens use growth stage DLI
    setpoint = await behavior.compute_setpoint("radish-microgreen", current_stage_index=1)
    assert setpoint.dli_mol_per_m2_per_day == 12.0


@pytest.mark.asyncio
async def test_validate_setpoint():
    registry = MemoryRegistry()
    behavior = LightingBehavior(registry)

    # Valid setpoint
    setpoint = await behavior.compute_setpoint("oyster-grey-strain-a", current_stage_index=2)
    assert await behavior.validate_setpoint(setpoint)

    # Invalid photoperiod
    setpoint.photoperiod_hours = 25
    assert not await behavior.validate_setpoint(setpoint)

    # Invalid DLI
    setpoint.photoperiod_hours = 12
    setpoint.dli_mol_per_m2_per_day = 150
    assert not await behavior.validate_setpoint(setpoint)


@pytest.mark.asyncio
async def test_missing_cultivar():
    registry = MemoryRegistry()
    behavior = LightingBehavior(registry)

    with pytest.raises(ValueError):
        await behavior.compute_setpoint("nonexistent", current_stage_index=0)
