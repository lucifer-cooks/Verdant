"""Convenience query functions for the VERDANT ecology and vegetation condition system."""

from __future__ import annotations

from typing import Any, Dict, Optional

from verdant.ecology.system import VerdantEcologySystem
from verdant.ecology.vegetation_state import VerdantVegetationState


def _resolve_system(world=None, climate_system=None, water_system=None, world_state=None, clock=None, seed=None) -> VerdantEcologySystem:
    system = VerdantEcologySystem(
        world_state=world_state,
        climate_system=climate_system,
        water_system=water_system,
        clock=clock,
        seed=seed,
    )
    if world is not None:
        system.bind_world(world)
    return system


def get_vegetation_state(x: int, y: int, z: int, world=None, climate_system=None,
                         water_system=None, world_state=None, clock=None, seed=None) -> VerdantVegetationState:
    system = _resolve_system(world, climate_system, water_system, world_state, clock, seed)
    return system.get_vegetation_state(x, y, z)


def get_growth_potential(x: int, y: int, z: int, world=None, climate_system=None,
                         water_system=None, world_state=None, clock=None, seed=None) -> float:
    system = _resolve_system(world, climate_system, water_system, world_state, clock, seed)
    return system.get_growth_potential(x, y, z)


def get_vegetation_health(x: int, y: int, z: int, world=None, climate_system=None,
                          water_system=None, world_state=None, clock=None, seed=None) -> float:
    system = _resolve_system(world, climate_system, water_system, world_state, clock, seed)
    return system.get_vegetation_health(x, y, z)


def get_environmental_stress(x: int, y: int, z: int, world=None, climate_system=None,
                             water_system=None, world_state=None, clock=None, seed=None) -> float:
    system = _resolve_system(world, climate_system, water_system, world_state, clock, seed)
    return system.get_environmental_stress(x, y, z)


def get_fertility(x: int, y: int, z: int, world=None, climate_system=None,
                  water_system=None, world_state=None, clock=None, seed=None) -> float:
    system = _resolve_system(world, climate_system, water_system, world_state, clock, seed)
    return system.get_fertility(x, y, z)


def get_season_modifier(x: Optional[int] = None, y: Optional[int] = None, z: Optional[int] = None,
                        world=None, climate_system=None, water_system=None, world_state=None, clock=None, seed=None) -> float:
    system = _resolve_system(world, climate_system, water_system, world_state, clock, seed)
    return system.get_season_modifier(x, y, z)


def get_current_season(world_state=None, clock=None) -> str:
    system = _resolve_system(world_state=world_state, clock=clock)
    return system.get_current_season()


def get_season_progress(world_state=None, clock=None) -> float:
    system = _resolve_system(world_state=world_state, clock=clock)
    return system.get_season_progress()


def is_growth_favorable(x: int, y: int, z: int, world=None, climate_system=None,
                        water_system=None, world_state=None, clock=None, seed=None) -> bool:
    system = _resolve_system(world, climate_system, water_system, world_state, clock, seed)
    return system.is_growth_favorable(x, y, z)
