"""Small debug/status surface for VERDANT development.

This does not add a UI; it exposes simple information for log inspection and test
verification.
"""

from __future__ import annotations


class VerdantDebugInfo:
    """Simple status object for simulation debugging and inspection."""

    def __init__(self, world_state=None, simulation_clock=None, simulation_manager=None, climate_system=None, query_boundary=None):
        self.world_state = world_state
        self.simulation_clock = simulation_clock
        self.simulation_manager = simulation_manager
        self.climate_system = climate_system
        self.query_boundary = query_boundary

    def snapshot(self):
        state = self.world_state
        clock = self.simulation_clock
        manager = self.simulation_manager

        return {
            'version': 'VERDANT 0.1.0',
            'world_age': (state.world_age_ticks if state else 0),
            'simulation_tick': (clock.elapsed_ticks if clock else 0),
            'season': (state.current_season if state else 'spring'),
            'registered_systems': (
                [getattr(system, 'name', system.__class__.__name__) for system in manager.systems]
                if manager else []
            ),
        }

    def environment_snapshot(self, x: int, y: int, z: int):
        if self.query_boundary is not None:
            env = self.query_boundary.get_environment(x, y, z)
            return {
                'position': {'x': x, 'y': y, 'z': z},
                'temperature': env['temperature'],
                'humidity': env['humidity'],
                'rainfall': env['rainfall'],
                'elevation': env['elevation'],
                'biome': env['biome'],
                'season': env['season'],
            }
        if self.climate_system is not None:
            env = self.climate_system.get_environment(x, y, z)
            return {
                'position': {'x': x, 'y': y, 'z': z},
                'temperature': env.temperature,
                'humidity': env.humidity,
                'rainfall': env.rainfall,
                'elevation': env.elevation,
                'biome': env.biome_name,
                'season': env.season,
            }
        return {
            'position': {'x': x, 'y': y, 'z': z},
            'temperature': 0.0,
            'humidity': 0.0,
            'rainfall': 0.0,
            'elevation': 0.0,
            'biome': 'Unknown',
            'season': 'spring',
        }
