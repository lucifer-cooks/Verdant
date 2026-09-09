"""VERDANT M8 — Creature Ecology & Population Dynamics Architecture.

This package establishes a macro-ecological population-dynamics foundation
wrapped non-intrusively around the existing Minecraft Indev creature and mob systems.

Core Architecture Principles:
-----------------------------
1. KEEP -> STUDY -> WRAP -> EXTEND -> eventually REPLACE:
   - Authoritative entity mechanics, physics, and legacy spawning remain untouched.
   - Observes existing entities in World.entityMap within bounded radii (r <= 16.0).
   - Never creates duplicate entities or a secondary entity registry.

2. Deterministic Macro-Ecological Modeling:
   - Evaluates resources (food, water, shelter) and dynamics (pressure, sustainability,
     recovery, expansion, and trend).
   - Driven strictly by world seed, coordinates, world age, and state from M3, M5, M6, and M7.
   - Zero dependence on Python's global random module or wall-clock time.

3. Performance & Bounded Evaluation:
   - Strict spatial bounds (r <= 16.0 blocks).
   - Zero whole-world scans or per-block entity tracking.
"""

from verdant.ecosystem.population import VerdantPopulationSample
from verdant.ecosystem.resources import VerdantResourceEvaluator
from verdant.ecosystem.dynamics import VerdantPopulationDynamics
from verdant.ecosystem.system import VerdantEcosystemSystem
from verdant.ecosystem.queries import (
    get_population_state,
    get_population_pressure,
    get_resource_pressure,
    get_food_availability,
    get_water_availability,
    get_shelter_availability,
    get_sustainability,
    get_population_trend,
    get_recovery_tendency,
    get_expansion_tendency,
)

__all__ = [
    'VerdantPopulationSample',
    'VerdantResourceEvaluator',
    'VerdantPopulationDynamics',
    'VerdantEcosystemSystem',
    'get_population_state',
    'get_population_pressure',
    'get_resource_pressure',
    'get_food_availability',
    'get_water_availability',
    'get_shelter_availability',
    'get_sustainability',
    'get_population_trend',
    'get_recovery_tendency',
    'get_expansion_tendency',
]
