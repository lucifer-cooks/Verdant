"""Future world-layer modules for VERDANT.

This package is reserved for biome, climate, vegetation, water, resource,
weather, and world-event systems. The legacy foundation remains authoritative
for the base world implementation.
"""

from .state import VerdantWorldState
from .clock import VerdantSimulationClock
from .queries import VerdantWorldQueryBoundary
from .persistence import VerdantStatePersistence
from .outworld import VerdantOutworldGenerator, OutworldGeographySample, get_world_seed, set_world_seed

__all__ = [
    'VerdantWorldState',
    'VerdantSimulationClock',
    'VerdantWorldQueryBoundary',
    'VerdantStatePersistence',
    'VerdantOutworldGenerator',
    'OutworldGeographySample',
    'get_world_seed',
    'set_world_seed',
]
