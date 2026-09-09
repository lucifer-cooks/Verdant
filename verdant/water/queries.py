"""Convenience query functions for the VERDANT moisture system."""

from __future__ import annotations

from typing import Any, Dict

from verdant.water.system import VerdantWaterSystem


def get_soil_moisture(x: int, y: int, z: int, world=None, climate_system=None, world_state=None):
    system = VerdantWaterSystem(world_state=world_state, climate_system=climate_system)
    if world is not None:
        system.bind_world(world)
    return system.get_soil_moisture(x, y, z)


def get_surface_water_presence(x: int, y: int, z: int, world=None, climate_system=None, world_state=None):
    system = VerdantWaterSystem(world_state=world_state, climate_system=climate_system)
    if world is not None:
        system.bind_world(world)
    return system.get_surface_water_presence(x, y, z)


def get_water_proximity(x: int, y: int, z: int, world=None, climate_system=None, world_state=None):
    system = VerdantWaterSystem(world_state=world_state, climate_system=climate_system)
    if world is not None:
        system.bind_world(world)
    return system.get_water_proximity(x, y, z)


def get_water_influence(x: int, y: int, z: int, world=None, climate_system=None, world_state=None):
    system = VerdantWaterSystem(world_state=world_state, climate_system=climate_system)
    if world is not None:
        system.bind_world(world)
    return system.get_water_influence(x, y, z)


def is_near_water(x: int, y: int, z: int, world=None, climate_system=None, world_state=None):
    system = VerdantWaterSystem(world_state=world_state, climate_system=climate_system)
    if world is not None:
        system.bind_world(world)
    return system.is_near_water(x, y, z)


def get_moisture_state(x: int, y: int, z: int, world=None, climate_system=None, world_state=None) -> Dict[str, Any]:
    system = VerdantWaterSystem(world_state=world_state, climate_system=climate_system)
    if world is not None:
        system.bind_world(world)
    return system.get_moisture_state(x, y, z).as_dict()
