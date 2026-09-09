"""Lightweight creature ecological state model for VERDANT M7."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class VerdantCreatureState:
    """Normalized ecological condition state for an entity or creature species."""

    species: str
    entity_id: Optional[int] = None
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    habitat_score: float = 0.0
    temperature_score: float = 0.0
    moisture_score: float = 0.0
    food_score: float = 0.0
    water_score: float = 0.0
    shelter_score: float = 0.0
    safety_score: float = 0.0
    population_pressure: float = 0.0
    stress: float = 0.0
    activity: str = 'active'
    movement_bias: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    behavior_context: str = 'idle'

    def as_dict(self) -> Dict[str, Any]:
        return {
            'species': self.species,
            'entity_id': self.entity_id,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'habitat_score': self.habitat_score,
            'temperature_score': self.temperature_score,
            'moisture_score': self.moisture_score,
            'food_score': self.food_score,
            'water_score': self.water_score,
            'shelter_score': self.shelter_score,
            'safety_score': self.safety_score,
            'population_pressure': self.population_pressure,
            'stress': self.stress,
            'activity': self.activity,
            'movement_bias': list(self.movement_bias),
            'behavior_context': self.behavior_context,
        }
