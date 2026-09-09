"""Lightweight vegetation condition state representation for VERDANT M6."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class VerdantVegetationState:
    """Normalized environmental condition state for local vegetation."""

    x: int
    y: int
    z: int
    growth_potential: float = 0.0
    moisture: float = 0.0
    temperature_suitability: float = 0.0
    sunlight: float = 0.0
    fertility: float = 0.0
    stress: float = 0.0
    health: float = 0.0
    season: str = 'spring'
    season_progress: float = 0.0
    biome_name: str = 'Plains'
    events: Tuple[str, ...] = ()

    def as_dict(self) -> Dict[str, Any]:
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'growth_potential': self.growth_potential,
            'moisture': self.moisture,
            'temperature_suitability': self.temperature_suitability,
            'sunlight': self.sunlight,
            'fertility': self.fertility,
            'stress': self.stress,
            'health': self.health,
            'season': self.season,
            'season_progress': self.season_progress,
            'biome_name': self.biome_name,
            'events': list(self.events),
        }
