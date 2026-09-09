"""VERDANT environmental foundation for M3.

This package contains the deterministic, read-only environmental model used by
future biome, climate, vegetation, and ecosystem systems.
"""

from .biome import VerdantBiomeDefinition, VerdantBiomeResolver
from .climate import VerdantClimateSystem
from .seed import VerdantWorldSeed

__all__ = [
    'VerdantBiomeDefinition',
    'VerdantBiomeResolver',
    'VerdantClimateSystem',
    'VerdantWorldSeed',
]
