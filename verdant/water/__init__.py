"""Water and moisture environmental foundation for VERDANT."""

from .moisture import VerdantMoistureState
from .system import VerdantWaterSystem
from .queries import (
    get_soil_moisture,
    get_surface_water_presence,
    get_water_proximity,
    get_water_influence,
    is_near_water,
    get_moisture_state,
)

__all__ = [
    'VerdantMoistureState',
    'VerdantWaterSystem',
    'get_soil_moisture',
    'get_surface_water_presence',
    'get_water_proximity',
    'get_water_influence',
    'is_near_water',
    'get_moisture_state',
]
