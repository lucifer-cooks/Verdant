"""Safe VERDANT query boundary for legacy world access.

This layer does not copy world state or scan the full map every tick. It exposes a
small, explicit set of localized queries for future VERDANT systems.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class VerdantWorldQueryBoundary:
    """Read-only access boundary for localized legacy world queries."""

    def __init__(self, world=None, climate_system=None):
        self.world = world
        self.climate_system = climate_system

    def bind_world(self, world):
        self.world = world
        return self

    def bind_climate_system(self, climate_system):
        self.climate_system = climate_system
        return self

    def get_world_time(self):
        if self.world is None:
            return 0
        try:
            return int(self.world.worldTime)
        except Exception:
            return 0

    def get_block_id(self, x: int, y: int, z: int):
        if self.world is None:
            return 0
        try:
            return int(self.world.getBlockId(int(x), int(y), int(z)))
        except Exception:
            return 0

    def is_exposed_to_sky(self, x: int, y: int, z: int):
        if self.world is None:
            return False
        try:
            local_block = self.get_block_id(x, y, z)
            return local_block == 0 and y >= int(self.world.getGroundLevel())
        except Exception:
            return False

    def get_local_height(self, x: int, z: int):
        if self.world is None:
            return 0
        try:
            return int(self.world.getGroundLevel())
        except Exception:
            return 0

    def get_elevation(self, x: int, y: int, z: int):
        if self.world is not None:
            try:
                return float(self.world.getGroundLevel())
            except Exception:
                pass
        if self.climate_system is not None:
            try:
                return float(self.climate_system.get_elevation(x, y, z))
            except Exception:
                pass
        return float(abs(x) + abs(z) + abs(y)) * 0.1

    def get_environment(self, x: int, y: int, z: int):
        if self.climate_system is not None:
            if self.world is not None and getattr(self.climate_system, 'world_state', None) is not None:
                self.climate_system.world_state.world = self.world
            env = self.climate_system.get_environment(x, y, z)
            return {
                'x': x,
                'y': y,
                'z': z,
                'temperature': env.temperature,
                'humidity': env.humidity,
                'rainfall': env.rainfall,
                'soil_moisture': env.soil_moisture,
                'elevation': env.elevation,
                'sunlight': env.sunlight,
                'water_proximity': env.water_proximity,
                'wind_strength': env.wind_strength,
                'fertility': env.fertility,
                'biome': env.biome_name,
                'season': env.season,
            }
        return {
            'x': x,
            'y': y,
            'z': z,
            'temperature': 0.0,
            'humidity': 0.0,
            'rainfall': 0.0,
            'soil_moisture': 0.0,
            'elevation': self.get_elevation(x, y, z),
            'sunlight': 0.0,
            'water_proximity': 0.0,
            'wind_strength': 0.0,
            'fertility': 0.0,
            'biome': 'Unknown',
            'season': 'spring',
        }

    def get_temperature(self, x: int, y: int, z: int):
        return self.get_environment(x, y, z)['temperature']

    def get_humidity(self, x: int, y: int, z: int):
        return self.get_environment(x, y, z)['humidity']

    def get_rainfall(self, x: int, y: int, z: int):
        return self.get_environment(x, y, z)['rainfall']

    def get_biome(self, x: int, y: int, z: int):
        biome_name = self.get_environment(x, y, z)['biome']
        return biome_name

    def get_nearby_entity_count(self, x: int, y: int, z: int, radius: float = 16.0):
        if self.world is None or not hasattr(self.world, 'entityMap'):
            return 0

        try:
            entity_map = self.world.entityMap
            if entity_map is None:
                return 0
            return len(entity_map.all)
        except Exception:
            return 0

    def snapshot(self, x: int, y: int, z: int):
        return {
            'world_time': self.get_world_time(),
            'block_id': self.get_block_id(x, y, z),
            'exposed_to_sky': self.is_exposed_to_sky(x, y, z),
            'local_height': self.get_local_height(x, z),
            'nearby_entities': self.get_nearby_entity_count(x, y, z),
            'environment': self.get_environment(x, y, z),
        }
