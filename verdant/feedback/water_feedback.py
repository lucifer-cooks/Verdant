"""Deterministic water and drought feedback model for VERDANT M9."""

from __future__ import annotations

from typing import Any, Dict, Optional


class VerdantWaterFeedback:
    """Evaluates ecological water stress and drought pressure.

    Connects rainfall, soil moisture, and ecosystem demand without modifying
    authoritative Minecraft Indev fluid mechanics or water blocks.
    """

    def __init__(self, seed: Optional[int] = None):
        self.seed = int(seed) if seed is not None else 0

    def _clamp(self, val: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, float(val)))

    def calculate_water_stress(self, soil_moisture: float, rainfall: float,
                               temperature: float, ecosystem_demand: float) -> float:
        """Calculates localized hydrological stress."""
        # Evaporative demand increases with heat
        evaporative_demand = max(0.0, (temperature - 15.0) / 25.0)
        # Supply vs demand deficit
        supply = 0.60 * soil_moisture + 0.40 * rainfall
        demand = 0.50 * evaporative_demand + 0.50 * ecosystem_demand

        if supply >= demand:
            stress = max(0.0, (1.0 - supply) * 0.25)
        else:
            deficit = demand - supply
            stress = min(1.0, 0.25 + deficit * 1.25)

        return self._clamp(stress)

    def calculate_drought_pressure(self, water_stress: float, soil_moisture: float,
                                   rainfall: float, season: str = 'summer') -> float:
        """Calculates macro drought pressure."""
        season_mod = 1.15 if season == 'summer' else (0.85 if season in ('spring', 'winter') else 1.0)
        arid_deficit = (1.0 - soil_moisture) * 0.60 + (1.0 - rainfall) * 0.40
        pressure = (0.55 * water_stress + 0.45 * arid_deficit) * season_mod
        return self._clamp(pressure)
