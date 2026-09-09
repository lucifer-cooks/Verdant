"""VERDANT extension layer for the original Indev 20100223 foundation.

This package intentionally stays separate from the original Minecraft codebase.
It provides a minimal no-op integration boundary for future features that expand
or replace systems in the legacy foundation without rewriting the working game.
"""

from .config import VERDANT_CONFIG
from .version import __version__, __build__, __release_name__
from .hooks import VerdantHooks
from .world.state import VerdantWorldState
from .world.clock import VerdantSimulationClock
from .world.queries import VerdantWorldQueryBoundary
from .world.persistence import VerdantStatePersistence
from .simulation.system import VerdantSystem
from .simulation.manager import VerdantSimulationManager
from .environment import VerdantBiomeDefinition, VerdantBiomeResolver, VerdantClimateSystem, VerdantWorldSeed

__all__ = [
    'VerdantHooks',
    'VerdantWorldState',
    'VerdantSimulationClock',
    'VerdantWorldQueryBoundary',
    'VerdantStatePersistence',
    'VerdantSystem',
    'VerdantSimulationManager',
    'VerdantBiomeDefinition',
    'VerdantBiomeResolver',
    'VerdantClimateSystem',
    'VerdantWorldSeed',
    'VERDANT_CONFIG',
    '__version__',
    '__build__',
    '__release_name__',
]
