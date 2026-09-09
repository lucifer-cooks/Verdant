"""VERDANT vegetation layer for M4.

The existing Indev vegetation and rendering systems remain authoritative. This
layer decides which vegetation is appropriate for a biome and environment and
then delegates actual placement/growth to the working legacy mechanisms.
"""

from .rules import VerdantVegetationRuleSet
from .system import VerdantVegetationSystem

__all__ = [
    'VerdantVegetationRuleSet',
    'VerdantVegetationSystem',
]
