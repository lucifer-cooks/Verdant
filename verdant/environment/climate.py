"""Deterministic climate system for VERDANT."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from verdant.environment.biome import VerdantBiomeResolver
from verdant.environment.seed import VerdantWorldSeed
from verdant.simulation.system import VerdantSystem


@dataclass(frozen=True)
class VerdantEnvironmentSample:
    """Lightweight environmental sample for local VERDANT calculations."""

    x: int
    y: int
    z: int
    temperature: float
    humidity: float
    rainfall: float
    soil_moisture: float
    elevation: float
    sunlight: float
    water_proximity: float
    wind_strength: float
    fertility: float
    biome_name: str
    season: str


class VerdantClimateSystem(VerdantSystem):
    """Simple deterministic climate model for M3.

    The algorithm is intentionally lightweight: a seeded sample is combined with
    elevation, season, and a modest deterministic noise term. It does not replace
    legacy terrain generation or block storage.
    """

    def __init__(self, world_state=None, *, name='verdant_climate', seed: Optional[int] = None):
        super().__init__(name=name)
        self.world_state = world_state
        self.seed = int(seed if seed is not None else (world_state.metadata.get('seed', 0) if world_state else 0))
        self.noise = VerdantWorldSeed(self.seed)
        self.biome_resolver = VerdantBiomeResolver()
        self.water_system = None
        self._resolving_water = False

    def initialize(self, context=None):
        if self.world_state is not None:
            self.seed = int(self.world_state.metadata.get('seed', self.seed))
            self.noise = VerdantWorldSeed(self.seed)
        self.initialized = True
        return self

    def _seasonal_modifier(self, season: str):
        modifiers = {
            'spring': {'temperature': 0.0, 'rainfall': 0.10},
            'summer': {'temperature': 0.35, 'rainfall': 0.15},
            'autumn': {'temperature': -0.10, 'rainfall': 0.05},
            'winter': {'temperature': -0.35, 'rainfall': -0.10},
        }
        return modifiers.get(season, {'temperature': 0.0, 'rainfall': 0.0})

    def _elevation_influence(self, elevation: float):
        return -0.008 * elevation

    def _temperature(self, x: int, y: int, z: int, elevation: float, season: str):
        base = 18.0 + self.noise.noise(x, y, z) * 18.0
        season_mod = self._seasonal_modifier(season)['temperature']
        return max(-30.0, min(45.0, base + season_mod + self._elevation_influence(elevation)))

    def _humidity(self, x: int, y: int, z: int, temperature: float, elevation: float):
        signal = self.noise.noise(x + 7, y + 3, z + 1)
        return max(0.0, min(1.0, 0.55 + signal * 0.35 + (18.0 - temperature) * 0.008 + (30.0 - abs(elevation)) * 0.002))

    def _rainfall(self, x: int, y: int, z: int, humidity: float, season: str):
        season_mod = self._seasonal_modifier(season)['rainfall']
        signal = self.noise.noise(x + 13, y + 7, z + 19)
        return max(0.0, min(1.0, humidity * 0.85 + signal * 0.2 + season_mod))

    def _soil_moisture(self, rainfall: float, humidity: float):
        return max(0.0, min(1.0, (rainfall + humidity) / 2.0))

    def _water_proximity(self, x: int, y: int, z: int, elevation: float):
        signal = self.noise.noise(x + 25, y + 11, z + 18)
        return max(0.0, min(1.0, 0.5 + signal * 0.25 + max(0.0, 25.0 - elevation) * 0.02))

    def _wind_strength(self, x: int, y: int, z: int):
        signal = self.noise.noise(x + 91, y + 44, z + 6)
        return max(0.0, min(1.0, 0.5 + signal * 0.5))

    def _fertility(self, humidity: float, rainfall: float, temperature: float):
        return max(0.0, min(1.0, 0.5 * humidity + 0.4 * rainfall + (1.0 if 8.0 <= temperature <= 28.0 else 0.0) - 0.2))

    def _resolve_water_system(self):
        if self.water_system is not None:
            return self.water_system
        if self.world_state is not None and getattr(self.world_state, 'world', None) is not None:
            from verdant.water.system import VerdantWaterSystem
            self.water_system = VerdantWaterSystem(world_state=self.world_state, climate_system=self)
            self.water_system.bind_world(self.world_state.world)
            self.world_state.water_system = self.water_system
            return self.water_system
        return None

    def get_environment(self, x: int, y: int, z: int):
        season = self.world_state.current_season if self.world_state is not None else 'spring'
        elevation = self.get_elevation(x, y, z)
        temperature = self._temperature(x, y, z, elevation, season)
        humidity = self._humidity(x, y, z, temperature, elevation)
        rainfall = self._rainfall(x, y, z, humidity, season)
        soil_moisture = self._soil_moisture(rainfall, humidity)
        sunlight = max(0.0, min(1.0, 0.55 + self.noise.noise(x + 19, y + 71, z + 23) * 0.35))
        water_proximity = self._water_proximity(x, y, z, elevation)
        wind_strength = self._wind_strength(x, y, z)
        fertility = self._fertility(humidity, rainfall, temperature)

        if not self._resolving_water:
            water_system = self._resolve_water_system()
            if water_system is not None:
                self._resolving_water = True
                try:
                    soil_moisture = water_system.get_soil_moisture(x, y, z)
                    water_proximity = water_system.get_water_proximity(x, y, z)
                finally:
                    self._resolving_water = False

        sample = type('TempEnv', (), {
            'temperature': temperature,
            'humidity': humidity,
            'rainfall': rainfall,
            'soil_moisture': soil_moisture,
            'elevation': elevation,
            'sunlight': sunlight,
            'water_proximity': water_proximity,
            'wind_strength': wind_strength,
            'fertility': fertility,
        })()

        biome = self.biome_resolver.resolve(sample)
        return VerdantEnvironmentSample(
            x=x,
            y=y,
            z=z,
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            soil_moisture=soil_moisture,
            elevation=elevation,
            sunlight=sunlight,
            water_proximity=water_proximity,
            wind_strength=wind_strength,
            fertility=fertility,
            biome_name=biome.name,
            season=season,
        )

    def get_temperature(self, x: int, y: int, z: int):
        return self.get_environment(x, y, z).temperature

    def get_humidity(self, x: int, y: int, z: int):
        return self.get_environment(x, y, z).humidity

    def get_rainfall(self, x: int, y: int, z: int):
        return self.get_environment(x, y, z).rainfall

    def get_elevation(self, x: int, y: int, z: int):
        if self.world_state is not None and getattr(self.world_state, 'world', None) is not None:
            try:
                return float(self.world_state.world.getGroundLevel())
            except Exception:
                pass
        return abs(self.noise.noise(x, y, z)) * 40.0 + (y / 3.0)

    def set_world_state(self, state):
        self.world_state = state
        if state is not None:
            self.seed = int(getattr(state, 'metadata', {}).get('seed', self.seed))
        self.noise = VerdantWorldSeed(self.seed)
        return self

    def snapshot(self):
        return {
            'seed': self.seed,
            'initialized': self.initialized,
            'world_state': getattr(self.world_state, 'current_season', 'spring'),
        }
