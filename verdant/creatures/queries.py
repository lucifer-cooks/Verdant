"""Convenience query functions for the VERDANT creature and ecosystem layer."""

from __future__ import annotations

from typing import Any, Dict, Optional

from verdant.creatures.creature_state import VerdantCreatureState
from verdant.creatures.system import VerdantCreatureSystem


def _resolve_system(world=None, world_state=None, climate_system=None, water_system=None,
                    ecology_system=None, clock=None, seed=None) -> VerdantCreatureSystem:
    system = VerdantCreatureSystem(
        world_state=world_state,
        climate_system=climate_system,
        water_system=water_system,
        ecology_system=ecology_system,
        clock=clock,
        seed=seed,
    )
    if world is not None:
        system.bind_world(world)
    return system


def get_creature_state(entity_or_species: Any, x: Optional[float] = None,
                       y: Optional[float] = None, z: Optional[float] = None,
                       world=None, world_state=None, climate_system=None,
                       water_system=None, ecology_system=None, clock=None,
                       seed=None) -> VerdantCreatureState:
    system = _resolve_system(world, world_state, climate_system, water_system, ecology_system, clock, seed)
    return system.get_creature_state(entity_or_species, x, y, z, world=world)


def get_habitat_score(entity_or_species: Any, x: Optional[float] = None,
                      y: Optional[float] = None, z: Optional[float] = None,
                      world=None, world_state=None, climate_system=None,
                      water_system=None, ecology_system=None, clock=None,
                      seed=None) -> float:
    system = _resolve_system(world, world_state, climate_system, water_system, ecology_system, clock, seed)
    return system.get_habitat_score(entity_or_species, x, y, z, world=world)


def get_food_suitability(entity_or_species: Any, x: Optional[float] = None,
                         y: Optional[float] = None, z: Optional[float] = None,
                         world=None, world_state=None, climate_system=None,
                         water_system=None, ecology_system=None, clock=None,
                         seed=None) -> float:
    system = _resolve_system(world, world_state, climate_system, water_system, ecology_system, clock, seed)
    return system.get_food_suitability(entity_or_species, x, y, z, world=world)


def get_water_access(entity_or_species: Any, x: Optional[float] = None,
                     y: Optional[float] = None, z: Optional[float] = None,
                     world=None, world_state=None, climate_system=None,
                     water_system=None, ecology_system=None, clock=None,
                     seed=None) -> float:
    system = _resolve_system(world, world_state, climate_system, water_system, ecology_system, clock, seed)
    return system.get_water_access(entity_or_species, x, y, z, world=world)


def get_shelter_score(entity_or_species: Any, x: Optional[float] = None,
                      y: Optional[float] = None, z: Optional[float] = None,
                      world=None, world_state=None, climate_system=None,
                      water_system=None, ecology_system=None, clock=None,
                      seed=None) -> float:
    system = _resolve_system(world, world_state, climate_system, water_system, ecology_system, clock, seed)
    return system.get_shelter_score(entity_or_species, x, y, z, world=world)


def get_population_pressure(x: float, y: float, z: float, radius: float = 16.0,
                            world=None, world_state=None, climate_system=None,
                            water_system=None, ecology_system=None, clock=None,
                            seed=None) -> float:
    system = _resolve_system(world, world_state, climate_system, water_system, ecology_system, clock, seed)
    return system.get_population_pressure(x, y, z, radius=radius, world=world)


def get_activity_tendency(entity_or_species: Any, x: Optional[float] = None,
                          y: Optional[float] = None, z: Optional[float] = None,
                          world=None, world_state=None, climate_system=None,
                          water_system=None, ecology_system=None, clock=None,
                          seed=None) -> str:
    system = _resolve_system(world, world_state, climate_system, water_system, ecology_system, clock, seed)
    return system.get_activity_tendency(entity_or_species, x, y, z, world=world)


def get_behavior_context(entity_or_species: Any, x: Optional[float] = None,
                         y: Optional[float] = None, z: Optional[float] = None,
                         world=None, world_state=None, climate_system=None,
                         water_system=None, ecology_system=None, clock=None,
                         seed=None) -> str:
    system = _resolve_system(world, world_state, climate_system, water_system, ecology_system, clock, seed)
    return system.get_behavior_context(entity_or_species, x, y, z, world=world)
