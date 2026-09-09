"""Deterministic habitat feedback model for VERDANT M9."""

from __future__ import annotations

from typing import Any, Dict, Optional


class VerdantHabitatFeedback:
    """Evaluates the influence of macro-ecological pressure on creature habitat suitability.

    When resources are depleted or populations are severely overcrowded, habitat pressure
    rises and effective ecological suitability declines without mutating legacy Indev AI.
    """

    def __init__(self, seed: Optional[int] = None):
        self.seed = int(seed) if seed is not None else 0

    def _clamp(self, val: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, float(val)))

    def calculate_habitat_pressure(self, base_habitat_quality: float, population_pressure: float,
                                   resource_pressure: float) -> float:
        """Calculates normalized habitat pressure from deficit and crowding."""
        deficit = 1.0 - self._clamp(base_habitat_quality)
        pressure = 0.40 * deficit + 0.35 * population_pressure + 0.25 * resource_pressure
        return self._clamp(pressure)

    def modulate_habitat_score(self, base_habitat_score: float, habitat_pressure: float,
                               ecosystem_health: float) -> float:
        """Modulates ecological habitat suitability in response to systemic health."""
        base = self._clamp(base_habitat_score)
        # Habitat degradation reduces suitability under severe pressure
        degradation = habitat_pressure * 0.35 * (1.0 - ecosystem_health * 0.50)
        modulated = base - degradation
        # Minor bonus in exceptionally healthy, thriving ecosystems
        if ecosystem_health >= 0.75 and habitat_pressure <= 0.25:
            modulated += (ecosystem_health - 0.75) * 0.20
        return self._clamp(modulated)
