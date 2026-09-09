"""Deterministic vegetation feedback and grazing pressure model for VERDANT M9."""

from __future__ import annotations

from typing import Any, Dict, Optional


class VerdantVegetationFeedback:
    """Evaluates the bidirectional relationship between herbivores and living vegetation.

    Translates herbivore population density and feeding demand into grazing pressure,
    elevated vegetation stress, and modulated recovery potential.
    """

    def __init__(self, seed: Optional[int] = None):
        self.seed = int(seed) if seed is not None else 0

    def _clamp(self, val: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, float(val)))

    def evaluate_grazing_pressure(self, herbivore_count: int, carrying_capacity: int = 8) -> float:
        """Calculates normalized grazing pressure from observed herbivore counts."""
        if herbivore_count <= 0:
            return 0.0
        cap = max(1, carrying_capacity)
        density = herbivore_count / cap
        if density <= 0.25:
            return density * 0.40
        elif density <= 0.75:
            return 0.10 + (density - 0.25) * 0.90
        else:
            return min(1.0, 0.55 + (density - 0.75) * 1.50)

    def calculate_vegetation_stress_feedback(self, base_stress: float, grazing_pressure: float,
                                             moisture: float) -> float:
        """Calculates total modulated vegetation stress under grazing and climate."""
        # Low soil moisture exacerbates the impact of herbivore grazing
        drought_multiplier = 1.0 + max(0.0, (0.40 - moisture) * 1.25)
        grazing_impact = grazing_pressure * 0.40 * drought_multiplier
        total_stress = base_stress + grazing_impact
        return self._clamp(total_stress)

    def calculate_vegetation_recovery_feedback(self, growth_potential: float, vegetation_health: float,
                                               fertility: float, grazing_pressure: float,
                                               vegetation_stress: float) -> float:
        """Calculates ecological vegetation regrowth capacity."""
        # Strong fertility and growth potential drive recovery
        base_recovery = 0.40 * growth_potential + 0.35 * vegetation_health + 0.25 * fertility
        # Heavy grazing pressure and severe stress suppress recovery
        suppression = 0.50 * grazing_pressure + 0.50 * vegetation_stress
        recovery = base_recovery * max(0.10, 1.0 - 0.85 * suppression)
        return self._clamp(recovery)
