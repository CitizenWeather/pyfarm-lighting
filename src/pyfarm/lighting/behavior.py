"""Lighting behavior for control loop integration."""

from __future__ import annotations

from typing import Optional

from pyfarm.crops.registry import CultivarRegistry
from pyfarm.lighting.calculator import LightingCalculator
from pyfarm.lighting.models import FixtureSpec, LightingSetpoint


class LightingBehavior:
    """Compute lighting setpoints based on cultivar and environment."""

    def __init__(
        self,
        registry: CultivarRegistry,
        default_fixture: Optional[FixtureSpec] = None,
    ):
        """Initialize lighting behavior.

        Args:
            registry: Cultivar registry for defaults
            default_fixture: Default LED fixture (400W/m², 2.5 μmol/J)
        """
        self.registry = registry
        self.default_fixture = default_fixture or FixtureSpec(
            fixture_id="default-led",
            wattage_per_m2=400.0,
            ppf_per_watt=2.5,
        )
        self.calculator = LightingCalculator()

    async def compute_setpoint(
        self,
        cultivar_id: str,
        current_stage_index: int,
        override_dli: Optional[float] = None,
        fixture: Optional[FixtureSpec] = None,
    ) -> LightingSetpoint:
        """Compute lighting setpoint for current stage.

        Args:
            cultivar_id: Cultivar ID
            current_stage_index: Index in phenophase list
            override_dli: Override DLI (use if provided)
            fixture: Override fixture spec

        Returns:
            Lighting setpoint with DLI and photoperiod
        """
        cultivar = await self.registry.get_cultivar(cultivar_id)
        if not cultivar:
            raise ValueError(f"Cultivar {cultivar_id} not found")

        fixture = fixture or self.default_fixture

        # Get current stage
        if current_stage_index >= len(cultivar.phenophases):
            raise ValueError(f"Stage index {current_stage_index} out of range")

        stage = cultivar.phenophases[current_stage_index]

        # Determine DLI
        if override_dli is not None:
            dli = override_dli
        elif stage.light_dli is not None:
            dli = stage.light_dli
        elif cultivar.optimal_light_dli is not None:
            dli = cultivar.optimal_light_dli
        else:
            dli = 8.0  # Default fallback

        # Compute runtime
        runtime_hours = self.calculator.dli_to_runtime_hours(dli, fixture)

        return LightingSetpoint(
            photoperiod_hours=runtime_hours,
            dli_mol_per_m2_per_day=dli,
        )

    async def validate_setpoint(self, setpoint: LightingSetpoint) -> bool:
        """Validate a lighting setpoint.

        Args:
            setpoint: Setpoint to validate

        Returns:
            True if valid
        """
        # Photoperiod must be 0-24h
        if not 0 <= setpoint.photoperiod_hours <= 24:
            return False

        # DLI must be 0-100
        if not 0 <= setpoint.dli_mol_per_m2_per_day <= 100:
            return False

        return True
