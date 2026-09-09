"""Convenience read-only query APIs for the VERDANT ecosystem and population dynamics layer."""

from __future__ import annotations

from typing import Any, Dict, Optional

from verdant.ecosystem.population import VerdantPopulationSample
from verdant.ecosystem.system import VerdantEcosystemSystem


def _resolve_system(world=None, world_state=None, climate_system=None, water_system=None,
                    ecology_system=None, creature_system=None, clock=None,
                    seed=None) -> VerdantEcosystemSystem:
    system = VerdantEcosystemSystem(
        world_state=world_state,
        climate_system=climate_system,
        water_system=water_system,
        ecology_system=ecology_system,
        creature_system=creature_system,
        clock=clock,
        seed=seed,
    )
    if world is not None:
        system.bind_world(world)
    return system


def get_population_state(x: float, y: float, z: float, radius: float = 16.0,
                         species: str = 'herbivore', world=None, world_state=None,
                         climate_system=None, water_system=None, ecology_system=None,
                         creature_system=None, clock=None, seed=None) -> VerdantPopulationSample:
    system = _resolve_system(world, world_state, climate_system, water_system, ecology_system, creature_system, clock, seed)
    return system.evaluate_population_sample(x, y, z, radius=radius, species=species, world=world)


def get_population_pressure(x: float, y: float, z: float, radius: float = 16.0,
                            species: str = 'herbivore', world=None, world_state=None,
                            climate_system=None, water_system=None, ecology_system=None,
                            creature_system=None, clock=None, seed=None) -> float:
    sample = get_population_state(x, y, z, radius=radius, species=species, world=world,
                                  world_state=world_state, climate_system=climate_system,
                                  water_system=water_system, ecology_system=ecology_system,
                                  creature_system=creature_system, clock=clock, seed=seed)
    return sample.population_pressure


def get_resource_pressure(x: float, y: float, z: float, radius: float = 16.0,
                          species: str = 'herbivore', world=None, world_state=None,
                          climate_system=None, water_system=None, ecology_system=None,
                          creature_system=None, clock=None, seed=None) -> float:
    sample = get_population_state(x, y, z, radius=radius, species=species, world=world,
                                  world_state=world_state, climate_system=climate_system,
                                  water_system=water_system, ecology_system=ecology_system,
                                  creature_system=creature_system, clock=clock, seed=seed)
    return sample.resource_pressure


def get_food_availability(x: float, y: float, z: float, radius: float = 16.0,
                          species: str = 'herbivore', world=None, world_state=None,
                          climate_system=None, water_system=None, ecology_system=None,
                          creature_system=None, clock=None, seed=None) -> float:
    sample = get_population_state(x, y, z, radius=radius, species=species, world=world,
                                  world_state=world_state, climate_system=climate_system,
                                  water_system=water_system, ecology_system=ecology_system,
                                  creature_system=creature_system, clock=clock, seed=seed)
    return sample.food_availability


def get_water_availability(x: float, y: float, z: float, radius: float = 16.0,
                           world=None, world_state=None, climate_system=None,
                           water_system=None, ecology_system=None, creature_system=None,
                           clock=None, seed=None) -> float:
    sample = get_population_state(x, y, z, radius=radius, species='herbivore', world=world,
                                  world_state=world_state, climate_system=climate_system,
                                  water_system=water_system, ecology_system=ecology_system,
                                  creature_system=creature_system, clock=clock, seed=seed)
    return sample.water_availability


def get_shelter_availability(x: float, y: float, z: float, radius: float = 16.0,
                             species: str = 'herbivore', world=None, world_state=None,
                             climate_system=None, water_system=None, ecology_system=None,
                             creature_system=None, clock=None, seed=None) -> float:
    sample = get_population_state(x, y, z, radius=radius, species=species, world=world,
                                  world_state=world_state, climate_system=climate_system,
                                  water_system=water_system, ecology_system=ecology_system,
                                  creature_system=creature_system, clock=clock, seed=seed)
    return sample.shelter_availability


def get_sustainability(x: float, y: float, z: float, radius: float = 16.0,
                       species: str = 'herbivore', world=None, world_state=None,
                       climate_system=None, water_system=None, ecology_system=None,
                       creature_system=None, clock=None, seed=None) -> float:
    sample = get_population_state(x, y, z, radius=radius, species=species, world=world,
                                  world_state=world_state, climate_system=climate_system,
                                  water_system=water_system, ecology_system=ecology_system,
                                  creature_system=creature_system, clock=clock, seed=seed)
    return sample.sustainability


def get_population_trend(x: float, y: float, z: float, radius: float = 16.0,
                         species: str = 'herbivore', world=None, world_state=None,
                         climate_system=None, water_system=None, ecology_system=None,
                         creature_system=None, clock=None, seed=None) -> str:
    sample = get_population_state(x, y, z, radius=radius, species=species, world=world,
                                  world_state=world_state, climate_system=climate_system,
                                  water_system=water_system, ecology_system=ecology_system,
                                  creature_system=creature_system, clock=clock, seed=seed)
    return sample.trend


def get_recovery_tendency(x: float, y: float, z: float, radius: float = 16.0,
                          species: str = 'herbivore', world=None, world_state=None,
                          climate_system=None, water_system=None, ecology_system=None,
                          creature_system=None, clock=None, seed=None) -> float:
    sample = get_population_state(x, y, z, radius=radius, species=species, world=world,
                                  world_state=world_state, climate_system=climate_system,
                                  water_system=water_system, ecology_system=ecology_system,
                                  creature_system=creature_system, clock=clock, seed=seed)
    return sample.recovery_tendency


def get_expansion_tendency(x: float, y: float, z: float, radius: float = 16.0,
                           species: str = 'herbivore', world=None, world_state=None,
                           climate_system=None, water_system=None, ecology_system=None,
                           creature_system=None, clock=None, seed=None) -> float:
    sample = get_population_state(x, y, z, radius=radius, species=species, world=world,
                                  world_state=world_state, climate_system=climate_system,
                                  water_system=water_system, ecology_system=ecology_system,
                                  creature_system=creature_system, clock=clock, seed=seed)
    return sample.expansion_tendency
