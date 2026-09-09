"""Ecology and living vegetation condition layer for VERDANT M6."""

from .vegetation_state import VerdantVegetationState
from .system import VerdantEcologySystem
from .queries import (
    get_vegetation_state,
    get_growth_potential,
    get_vegetation_health,
    get_environmental_stress,
    get_fertility,
    get_season_modifier,
    get_current_season,
    get_season_progress,
    is_growth_favorable,
)

__all__ = [
    'VerdantVegetationState',
    'VerdantEcologySystem',
    'get_vegetation_state',
    'get_growth_potential',
    'get_vegetation_health',
    'get_environmental_stress',
    'get_fertility',
    'get_season_modifier',
    'get_current_season',
    'get_season_progress',
    'is_growth_favorable',
]
