"""Public convenience query functions for the VERDANT ecological feedback layer."""

from __future__ import annotations

from typing import Any, Dict, Optional

from verdant.feedback.signals import VerdantEcologicalSignals
from verdant.feedback.system import VerdantFeedbackSystem


def _resolve_system(world=None, world_state=None, climate_system=None, water_system=None,
                    ecology_system=None, creature_system=None, ecosystem_system=None,
                    clock=None, seed=None) -> VerdantFeedbackSystem:
    system = VerdantFeedbackSystem(
        world_state=world_state,
        climate_system=climate_system,
        water_system=water_system,
        ecology_system=ecology_system,
        creature_system=creature_system,
        ecosystem_system=ecosystem_system,
        clock=clock,
        seed=seed,
    )
    if world is not None:
        system.bind_world(world)
    return system


def get_ecosystem_state(x: float, y: float, z: float, radius: float = 16.0,
                        world=None, world_state=None, climate_system=None,
                        water_system=None, ecology_system=None, creature_system=None,
                        ecosystem_system=None, clock=None, seed=None) -> VerdantEcologicalSignals:
    system = _resolve_system(world, world_state, climate_system, water_system, ecology_system, creature_system, ecosystem_system, clock, seed)
    return system.evaluate_ecological_signals(x, y, z, radius=radius, world=world)


def get_ecological_health(x: float, y: float, z: float, radius: float = 16.0,
                          world=None, world_state=None, climate_system=None,
                          water_system=None, ecology_system=None, creature_system=None,
                          ecosystem_system=None, clock=None, seed=None) -> float:
    state = get_ecosystem_state(x, y, z, radius=radius, world=world, world_state=world_state,
                                climate_system=climate_system, water_system=water_system,
                                ecology_system=ecology_system, creature_system=creature_system,
                                ecosystem_system=ecosystem_system, clock=clock, seed=seed)
    return state.ecological_health


def get_grazing_pressure(x: float, y: float, z: float, radius: float = 16.0,
                         world=None, world_state=None, climate_system=None,
                         water_system=None, ecology_system=None, creature_system=None,
                         ecosystem_system=None, clock=None, seed=None) -> float:
    state = get_ecosystem_state(x, y, z, radius=radius, world=world, world_state=world_state,
                                climate_system=climate_system, water_system=water_system,
                                ecology_system=ecology_system, creature_system=creature_system,
                                ecosystem_system=ecosystem_system, clock=clock, seed=seed)
    return state.grazing_pressure


def get_vegetation_stress(x: float, y: float, z: float, radius: float = 16.0,
                          world=None, world_state=None, climate_system=None,
                          water_system=None, ecology_system=None, creature_system=None,
                          ecosystem_system=None, clock=None, seed=None) -> float:
    state = get_ecosystem_state(x, y, z, radius=radius, world=world, world_state=world_state,
                                climate_system=climate_system, water_system=water_system,
                                ecology_system=ecology_system, creature_system=creature_system,
                                ecosystem_system=ecosystem_system, clock=clock, seed=seed)
    return state.vegetation_stress


def get_vegetation_recovery(x: float, y: float, z: float, radius: float = 16.0,
                            world=None, world_state=None, climate_system=None,
                            water_system=None, ecology_system=None, creature_system=None,
                            ecosystem_system=None, clock=None, seed=None) -> float:
    state = get_ecosystem_state(x, y, z, radius=radius, world=world, world_state=world_state,
                                climate_system=climate_system, water_system=water_system,
                                ecology_system=ecology_system, creature_system=creature_system,
                                ecosystem_system=ecosystem_system, clock=clock, seed=seed)
    return state.vegetation_recovery


def get_habitat_pressure(x: float, y: float, z: float, radius: float = 16.0,
                         world=None, world_state=None, climate_system=None,
                         water_system=None, ecology_system=None, creature_system=None,
                         ecosystem_system=None, clock=None, seed=None) -> float:
    state = get_ecosystem_state(x, y, z, radius=radius, world=world, world_state=world_state,
                                climate_system=climate_system, water_system=water_system,
                                ecology_system=ecology_system, creature_system=creature_system,
                                ecosystem_system=ecosystem_system, clock=clock, seed=seed)
    return state.habitat_pressure


def get_water_stress(x: float, y: float, z: float, radius: float = 16.0,
                     world=None, world_state=None, climate_system=None,
                     water_system=None, ecology_system=None, creature_system=None,
                     ecosystem_system=None, clock=None, seed=None) -> float:
    state = get_ecosystem_state(x, y, z, radius=radius, world=world, world_state=world_state,
                                climate_system=climate_system, water_system=water_system,
                                ecology_system=ecology_system, creature_system=creature_system,
                                ecosystem_system=ecosystem_system, clock=clock, seed=seed)
    return state.water_stress


def get_drought_pressure(x: float, y: float, z: float, radius: float = 16.0,
                         world=None, world_state=None, climate_system=None,
                         water_system=None, ecology_system=None, creature_system=None,
                         ecosystem_system=None, clock=None, seed=None) -> float:
    state = get_ecosystem_state(x, y, z, radius=radius, world=world, world_state=world_state,
                                climate_system=climate_system, water_system=water_system,
                                ecology_system=ecology_system, creature_system=creature_system,
                                ecosystem_system=ecosystem_system, clock=clock, seed=seed)
    return state.drought_pressure


def get_population_pressure(x: float, y: float, z: float, radius: float = 16.0,
                            world=None, world_state=None, climate_system=None,
                            water_system=None, ecology_system=None, creature_system=None,
                            ecosystem_system=None, clock=None, seed=None) -> float:
    state = get_ecosystem_state(x, y, z, radius=radius, world=world, world_state=world_state,
                                climate_system=climate_system, water_system=water_system,
                                ecology_system=ecology_system, creature_system=creature_system,
                                ecosystem_system=ecosystem_system, clock=clock, seed=seed)
    return state.population_pressure


def get_adaptive_response(x: float, y: float, z: float, radius: float = 16.0,
                          world=None, world_state=None, climate_system=None,
                          water_system=None, ecology_system=None, creature_system=None,
                          ecosystem_system=None, clock=None, seed=None) -> str:
    state = get_ecosystem_state(x, y, z, radius=radius, world=world, world_state=world_state,
                                climate_system=climate_system, water_system=water_system,
                                ecology_system=ecology_system, creature_system=creature_system,
                                ecosystem_system=ecosystem_system, clock=clock, seed=seed)
    return state.adaptive_response


def explain_ecosystem(x: float, y: float, z: float, radius: float = 16.0,
                      world=None, world_state=None, climate_system=None,
                      water_system=None, ecology_system=None, creature_system=None,
                      ecosystem_system=None, clock=None, seed=None) -> str:
    state = get_ecosystem_state(x, y, z, radius=radius, world=world, world_state=world_state,
                                climate_system=climate_system, water_system=water_system,
                                ecology_system=ecology_system, creature_system=creature_system,
                                ecosystem_system=ecosystem_system, clock=clock, seed=seed)
    return state.explain()
