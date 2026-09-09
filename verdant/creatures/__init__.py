"""
VERDANT M7 — Creatures & Living Ecosystem Architecture
======================================================

The M7 Creature & Living Ecosystem layer provides an ecological evaluation and
behavioral context model wrapped around the authoritative legacy Minecraft Indev
entities.

Core Architecture Principles:
-----------------------------
1. KEEP -> STUDY -> WRAP -> EXTEND -> eventually REPLACE
   - Authoritative gameplay entity mechanics (movement, physics, rendering, standard
     Indev AI, spawning thresholds) remain completely untouched.
   - Verdant attaches an ecological state lens (`VerdantCreatureState`) to existing
     entities (`EntityPig`, `EntitySheep`, `EntityZombie`, `EntitySkeleton`, `EntitySpider`,
     `EntityCreeper`, etc.).

2. Determinism:
   - All ecological condition scoring, habitat evaluations, and behavioral contexts
     depend strictly on world seed, coordinate position, world age, and simulation version.
   - No reliance on global nondeterministic random generators.

3. Performance & Bounded Spatial Queries:
   - Evaluates within local bounds (spatial radius <= 16 blocks).
   - No global entity scanning across the entire world level.
   - Respects chunk / spatial map spatial organization.

4. Integration:
   - `VerdantCreatureSystem` is registered with `VerdantSimulationManager` and receives
     tick and day updates.
   - Leverages M3 Climate, M5 Moisture, and M6 Vegetation State for holistic habitat scoring.
"""

from verdant.creatures.creature_state import VerdantCreatureState
from verdant.creatures.habitat import VerdantHabitatEvaluator
from verdant.creatures.behavior import VerdantBehaviorContext
from verdant.creatures.system import VerdantCreatureSystem
from verdant.creatures.queries import (
    get_creature_state,
    get_habitat_score,
    get_food_suitability,
    get_water_access,
    get_shelter_score,
    get_population_pressure,
    get_activity_tendency,
    get_behavior_context,
)

__all__ = [
    "VerdantCreatureState",
    "VerdantHabitatEvaluator",
    "VerdantBehaviorContext",
    "VerdantCreatureSystem",
    "get_creature_state",
    "get_habitat_score",
    "get_food_suitability",
    "get_water_access",
    "get_shelter_score",
    "get_population_pressure",
    "get_activity_tendency",
    "get_behavior_context",
]
