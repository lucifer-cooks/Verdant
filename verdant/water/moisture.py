"""Lightweight moisture state representation for VERDANT."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VerdantMoistureState:
    """Normalized environmental moisture sample for a local world coordinate."""

    x: int
    y: int
    z: int
    soil_moisture: float = 0.0
    surface_water_presence: float = 0.0
    water_proximity: float = 0.0
    water_influence: float = 0.0
    evaporation_potential: float = 0.0
    water_accessibility: float = 0.0
    nearby_water: bool = False
    biome_name: str = 'Plains'
    rainfall: float = 0.0
    humidity: float = 0.0
    temperature: float = 0.0
    elevation: float = 0.0

    def as_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'soil_moisture': self.soil_moisture,
            'surface_water_presence': self.surface_water_presence,
            'water_proximity': self.water_proximity,
            'water_influence': self.water_influence,
            'evaporation_potential': self.evaporation_potential,
            'water_accessibility': self.water_accessibility,
            'nearby_water': self.nearby_water,
            'biome_name': self.biome_name,
            'rainfall': self.rainfall,
            'humidity': self.humidity,
            'temperature': self.temperature,
            'elevation': self.elevation,
        }
