"""Deterministic normalized ecological signals model for VERDANT M9."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class VerdantEcologicalSignals:
    """Encapsulates normalized ecological feedback signals for a bounded region.

    All signals are normalized in [0.0, 1.0] and derived deterministically from
    climate (M3), moisture (M5), vegetation (M6), creatures (M7), and population dynamics (M8).
    """

    x: float
    y: float
    z: float
    radius: float
    grazing_pressure: float
    vegetation_stress: float
    vegetation_recovery: float
    habitat_pressure: float
    resource_pressure: float
    water_stress: float
    drought_pressure: float
    population_pressure: float
    ecological_health: float
    ecosystem_stability: float
    adaptive_response: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'radius': self.radius,
            'grazing_pressure': self.grazing_pressure,
            'vegetation_stress': self.vegetation_stress,
            'vegetation_recovery': self.vegetation_recovery,
            'habitat_pressure': self.habitat_pressure,
            'resource_pressure': self.resource_pressure,
            'water_stress': self.water_stress,
            'drought_pressure': self.drought_pressure,
            'population_pressure': self.population_pressure,
            'ecological_health': self.ecological_health,
            'ecosystem_stability': self.ecosystem_stability,
            'adaptive_response': self.adaptive_response,
        }

    def explain(self) -> str:
        """Returns a multi-line diagnostic representation of the ecological state."""
        lines = [
            f"Ecosystem at ({self.x:.1f}, {self.y:.1f}, {self.z:.1f}) [r={self.radius:.1f}]:",
            f"  adaptive_response  : {self.adaptive_response}",
            f"  ecological_health  : {self.ecological_health:.2f}",
            f"  ecosystem_stability: {self.ecosystem_stability:.2f}",
            "Factors:",
            f"  grazing_pressure   : {self.grazing_pressure:.2f}",
            f"  vegetation_stress  : {self.vegetation_stress:.2f}",
            f"  vegetation_recovery: {self.vegetation_recovery:.2f}",
            f"  habitat_pressure   : {self.habitat_pressure:.2f}",
            f"  resource_pressure  : {self.resource_pressure:.2f}",
            f"  water_stress       : {self.water_stress:.2f}",
            f"  drought_pressure   : {self.drought_pressure:.2f}",
            f"  population_pressure: {self.population_pressure:.2f}",
        ]
        return "\n".join(lines)
