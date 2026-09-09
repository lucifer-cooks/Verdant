"""VERDANT world state for future simulation systems.

This class represents environmental state owned by VERDANT rather than the legacy
Minecraft engine. It intentionally references the current world instead of copying
all block data or maintaining a second world model.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class VerdantWorldState:
    """Persistent environmental state for VERDANT systems."""

    SEASONS = ('spring', 'summer', 'autumn', 'winter')
    CLIMATES = ('temperate', 'arid', 'temperate_rainy', 'cold')
    WEATHER = ('clear', 'rain', 'storm', 'snow', 'overcast')

    def __init__(self, world=None, *,
                 simulation_version: int = 1,
                 world_age_ticks: int = 0,
                 current_season: str = 'spring',
                 climate: str = 'temperate',
                 weather: str = 'clear'):
        self.world = world
        self.simulation_version = simulation_version
        self.world_age_ticks = world_age_ticks
        self.elapsed_simulation_ticks = 0
        self.current_season = current_season
        self.climate = climate
        self.weather = weather
        self.environment_events: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}

    def bind_world(self, world):
        self.world = world
        return self

    def update_world_time(self, legacy_time: int = 0):
        self.elapsed_simulation_ticks = max(0, int(legacy_time))
        self.world_age_ticks = max(0, int(legacy_time))
        return self.world_age_ticks

    def set_season(self, season: str):
        if season in self.SEASONS:
            self.current_season = season
        return self.current_season

    def set_climate(self, climate: str):
        if climate in self.CLIMATES:
            self.climate = climate
        return self.climate

    def set_weather(self, weather: str):
        if weather in self.WEATHER:
            self.weather = weather
        return self.weather

    def add_event(self, event_type: str, payload: Optional[Dict[str, Any]] = None):
        event = {'type': event_type, 'payload': payload or {}}
        self.environment_events.append(event)
        return event

    def get_environment_at(self, x: int, y: int, z: int):
        """Lightweight VERDANT environmental data for a location.

        This intentionally does not duplicate the legacy world. It provides a
        stable snapshot of environmental state that future systems can extend.
        """
        if self.world is None:
            return {
                'x': x, 'y': y, 'z': z,
                'season': self.current_season,
                'climate': self.climate,
                'weather': self.weather,
                'world_time': self.world_age_ticks,
                'block_id': 0,
                'exposed_to_sky': False,
            }

        try:
            block_id = int(self.world.getBlockId(x, y, z))
        except Exception:
            block_id = 0

        try:
            exposed = bool(y >= self.world.getGroundLevel())
        except Exception:
            exposed = False

        return {
            'x': x, 'y': y, 'z': z,
            'season': self.current_season,
            'climate': self.climate,
            'weather': self.weather,
            'world_time': self.world_age_ticks,
            'block_id': block_id,
            'exposed_to_sky': exposed,
        }

    def to_dict(self):
        return {
            'simulation_version': self.simulation_version,
            'world_age_ticks': self.world_age_ticks,
            'elapsed_simulation_ticks': self.elapsed_simulation_ticks,
            'current_season': self.current_season,
            'climate': self.climate,
            'weather': self.weather,
            'environment_events': list(self.environment_events),
            'metadata': dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            simulation_version=int(data.get('simulation_version', 1)),
            world_age_ticks=int(data.get('world_age_ticks', 0)),
            current_season=data.get('current_season', 'spring'),
            climate=data.get('climate', 'temperate'),
            weather=data.get('weather', 'clear'),
        )
        obj.elapsed_simulation_ticks = int(data.get('elapsed_simulation_ticks', 0))
        obj.environment_events = list(data.get('environment_events', []))
        obj.metadata = dict(data.get('metadata', {}))
        return obj
