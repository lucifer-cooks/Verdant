# VERDANT M7 — Creatures & Living Ecosystem

## Overview

The `verdant.creatures` package provides an ecological condition, habitat evaluation, and behavior context layer built around existing Minecraft Indev passive (`EntityPig`, `EntitySheep`) and hostile (`EntityZombie`, `EntitySkeleton`, `EntitySpider`, `EntityCreeper`) entities.

Following the core VERDANT principle:
**KEEP → STUDY → WRAP → EXTEND → eventually REPLACE**

authoritative entity mechanics (physics, rendering, collision, health, legacy pathfinding, legacy spawning) remain in the existing Indev codebase. VERDANT attaches an ecological state lens (`VerdantCreatureState`) that interprets entity condition in the context of the living world.

---

## Architecture

### 1. Creature State (`creature_state.py`)
Encapsulates the ecological condition of an entity:
- `species`: Species or entity category identifier (e.g. `'pig'`, `'sheep'`, `'zombie'`).
- `habitat_score`: Overall composite suitability `[0.0, 1.0]`.
- `temperature_score`: Thermal comfort score `[0.0, 1.0]`.
- `moisture_score`: Hydrological comfort score `[0.0, 1.0]`.
- `food_score`: Foraging/prey availability `[0.0, 1.0]`.
- `water_score`: Proximity/access to hydration `[0.0, 1.0]`.
- `shelter_score`: Canopy, roof, or cave coverage `[0.0, 1.0]`.
- `safety_score`: Predator or environmental hazard safety `[0.0, 1.0]`.
- `population_pressure`: Local crowding ratio (evaluated within radius $\le 16$).
- `stress`: Stress index `[0.0, 1.0]` derived from unmet needs and crowding.
- `activity`: Diurnal/nocturnal activity tendency `[0.0, 1.0]`.
- `movement_bias`: Vector `(dx, dy, dz)` indicating ecological environmental drift.
- `behavior_context`: Context flag (`'wander'`, `'seek_food'`, `'seek_water'`, `'seek_shelter'`, `'avoid_stress'`, `'flee'`, `'idle'`, `'investigate'`).

### 2. Habitat Evaluator (`habitat.py`)
Evaluates local environmental suitability based on species profiles:
- **Herbivore (`pig`)**: Moderate temp, high moisture preference, grass/vegetation food dependency, open/semi-sheltered.
- **Small Animal / Grazer (`sheep`)**: Temperate/cool preference, moderate moisture, grass/flower food dependency, open plains preference.
- **Spider (`spider`)**: Broad temperature/moisture tolerance, canopy/crevice shelter preference, nocturnal/dark activity.
- **Hostile (`creeper`)**: Dark activity, avoids bright open spaces, nocturnal bias.
- **Undead (`zombie`, `skeleton`)**: Shelter-critical to avoid sunlight, nocturnal activity.

Leverages:
- M3 Biome & Climate (`VerdantBiomeClimate`) for temperature and rainfall.
- M5 Moisture Model for localized soil/water hydration.
- M6 Vegetation State for vegetation health and forage availability.

### 3. Behavior Context (`behavior.py`)
Translates ecological pressures into behavioral intent without overriding legacy AI:
- High thirst/low water $\to$ `seek_water` with gradient bias toward water.
- High hunger/low food $\to$ `seek_food` with gradient bias toward lush vegetation.
- Severe sunlight for undead or high stress $\to$ `seek_shelter`.
- High population pressure $\to$ `avoid_stress` pointing away from centroid of neighbors.
- Balanced condition $\to$ `wander` or `idle` based on circadian activity curve.

### 4. Bounded Queries & Performance
- Spatial queries are bounded strictly to radius $\le 16$ blocks.
- Uses `level.entityMap` or chunk-bounded spatial queries.
- Zero whole-world entity scans.
- Fully deterministic evaluations driven by world seed, coordinates, world age, and simulation tick.
