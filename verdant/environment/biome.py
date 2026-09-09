"""Biome definitions and deterministic resolution for VERDANT."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class VerdantBiomeDefinition:
    """Environmental definition for a VERDANT biome.

    These are not terrain types; they describe the environmental envelope a
    location is expected to occupy. Future systems can extend this as needed.
    """

    name: str
    temperature_range: tuple
    humidity_range: tuple
    rainfall_range: tuple
    vegetation_potential: float = 0.0
    water_availability: float = 0.0
    fertility: float = 0.0
    description: str = ""
    tags: tuple = field(default_factory=tuple)

    def matches(self, environment) -> bool:
        return (
            self.temperature_range[0] <= environment.temperature <= self.temperature_range[1]
            and self.humidity_range[0] <= environment.humidity <= self.humidity_range[1]
            and self.rainfall_range[0] <= environment.rainfall <= self.rainfall_range[1]
        )


class VerdantBiomeResolver:
    """Deterministic biome classification based on environmental values."""

    BIOMES: Dict[str, VerdantBiomeDefinition] = {
        'ocean': VerdantBiomeDefinition(
            name='Ocean',
            temperature_range=(-1.0, 22.0),
            humidity_range=(0.0, 1.0),
            rainfall_range=(0.0, 0.9),
            vegetation_potential=0.05,
            water_availability=1.0,
            fertility=0.15,
            description='Coastal and submerged environment with stable water abundance.',
            tags=('water', 'marine', 'low_land'),
        ),
        'plains': VerdantBiomeDefinition(
            name='Plains',
            temperature_range=(8.0, 28.0),
            humidity_range=(0.2, 0.75),
            rainfall_range=(0.2, 0.8),
            vegetation_potential=0.7,
            water_availability=0.7,
            fertility=0.75,
            description='Balanced temperate lowlands with broad vegetation potential.',
            tags=('temperate', 'grassland', 'fertile'),
        ),
        'forest': VerdantBiomeDefinition(
            name='Forest',
            temperature_range=(6.0, 24.0),
            humidity_range=(0.5, 0.95),
            rainfall_range=(0.45, 1.0),
            vegetation_potential=0.95,
            water_availability=0.9,
            fertility=0.85,
            description='Moist, productive woodland environment.',
            tags=('humid', 'woodland', 'lush'),
        ),
        'desert': VerdantBiomeDefinition(
            name='Desert',
            temperature_range=(20.0, 45.0),
            humidity_range=(0.0, 0.25),
            rainfall_range=(0.0, 0.2),
            vegetation_potential=0.1,
            water_availability=0.1,
            fertility=0.2,
            description='Dry, warm environment with poor vegetation and low water.',
            tags=('arid', 'hot', 'dry'),
        ),
        'mountains': VerdantBiomeDefinition(
            name='Mountains',
            temperature_range=(-10.0, 18.0),
            humidity_range=(0.1, 0.8),
            rainfall_range=(0.1, 0.9),
            vegetation_potential=0.35,
            water_availability=0.55,
            fertility=0.25,
            description='Elevated terrain with cooler temperatures and sparse productivity.',
            tags=('elevated', 'cold', 'rocky'),
        ),
        'snow': VerdantBiomeDefinition(
            name='Snow/Tundra',
            temperature_range=(-30.0, 5.0),
            humidity_range=(0.1, 0.8),
            rainfall_range=(0.0, 0.6),
            vegetation_potential=0.15,
            water_availability=0.4,
            fertility=0.18,
            description='Cold environment with low productivity and limited plant growth.',
            tags=('cold', 'tundra', 'frozen'),
        ),
        'swamp': VerdantBiomeDefinition(
            name='Swamp',
            temperature_range=(8.0, 26.0),
            humidity_range=(0.7, 1.0),
            rainfall_range=(0.6, 1.0),
            vegetation_potential=0.8,
            water_availability=1.0,
            fertility=0.7,
            description='Wet, dense environment with high water and rich organic potential.',
            tags=('wet', 'marsh', 'waterlogged'),
        ),
    }

    def __init__(self):
        self.biome_index = {biome.name: biome for biome in self.BIOMES.values()}
        self.biome_lookup = {key.lower(): biome for key, biome in self.BIOMES.items()}

    def resolve(self, environment) -> VerdantBiomeDefinition:
        temperature = float(getattr(environment, 'temperature', 20.0))
        humidity = float(getattr(environment, 'humidity', 0.5))
        rainfall = float(getattr(environment, 'rainfall', 0.5))
        water_proximity = float(getattr(environment, 'water_proximity', 0.0))

        if temperature >= 28.0 and humidity <= 0.6 and rainfall <= 0.8 and water_proximity < 0.7:
            return self.biome_index['Desert']
        if temperature <= 22.0 and rainfall >= 0.2 and water_proximity >= 0.55:
            return self.biome_index['Forest']
        if humidity >= 0.55 and rainfall >= 0.4 and water_proximity >= 0.6:
            return self.biome_index['Swamp']
        if temperature <= 8.0 and humidity <= 0.8:
            return self.biome_index['Snow/Tundra']

        matches = [biome for biome in self.biome_index.values() if biome.matches(environment)]
        if not matches:
            return self.biome_index['Plains']
        return max(matches, key=lambda biome: (biome.vegetation_potential, biome.fertility, biome.water_availability))

    def list(self) -> Iterable[str]:
        return tuple(self.biome_index.keys())

    @classmethod
    def from_environment(cls, environment):
        return cls().resolve(environment)
