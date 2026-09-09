"""Lightweight bounded spatial population sample dataclass for VERDANT M8."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class VerdantPopulationSample:
    """Represents a bounded local population and ecological dynamics observation.

    Does not create duplicate entities or secondary entity registries.
    Encapsulates macro-ecological metrics within a localized spatial sphere (r <= 16.0).
    """

    species: str
    center_x: float
    center_y: float
    center_z: float
    radius: float
    count: int
    density: float
    habitat_quality: float
    food_availability: float
    water_availability: float
    shelter_availability: float
    population_pressure: float
    resource_pressure: float
    ecological_stress: float
    sustainability: float
    recovery_tendency: float
    expansion_tendency: float
    trend: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            'species': self.species,
            'center_x': self.center_x,
            'center_y': self.center_y,
            'center_z': self.center_z,
            'radius': self.radius,
            'count': self.count,
            'density': self.density,
            'habitat_quality': self.habitat_quality,
            'food_availability': self.food_availability,
            'water_availability': self.water_availability,
            'shelter_availability': self.shelter_availability,
            'population_pressure': self.population_pressure,
            'resource_pressure': self.resource_pressure,
            'ecological_stress': self.ecological_stress,
            'sustainability': self.sustainability,
            'recovery_tendency': self.recovery_tendency,
            'expansion_tendency': self.expansion_tendency,
            'trend': self.trend,
        }
