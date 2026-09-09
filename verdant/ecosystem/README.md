# VERDANT M8 — Creature Ecology & Population Dynamics

## Overview

The `verdant.ecosystem` package creates a macro-ecological population-dynamics layer built non-intrusively around existing Minecraft Indev passive (`EntityPig`, `EntitySheep`) and hostile (`EntityZombie`, `EntitySkeleton`, `EntitySpider`, `EntityCreeper`) entities.

Following the core VERDANT principle:
**KEEP → STUDY → WRAP → EXTEND → eventually REPLACE**

The authoritative entity engine remains completely responsible for physics, collision, damage, health, pathfinding, and legacy spawning thresholds. VERDANT attaches an ecological population lens (`VerdantPopulationSample`) that interprets how local creature density and environmental resources interact over simulation time.

---

## Key Modules

### 1. Bounded Population Sample (`population.py`)
Encapsulates ecological metrics within a localized spatial sphere ($r \le 16.0$ blocks):
- `count`, `density`, `habitat_quality`
- `food_availability`, `water_availability`, `shelter_availability`
- `population_pressure`, `resource_pressure`, `ecological_stress`
- `sustainability`, `recovery_tendency`, `expansion_tendency`
- `trend` (`'stable'`, `'recovering'`, `'growing'`, `'pressured'`, `'declining'`)

### 2. Resource Pressure Model (`resources.py`)
Evaluates resource presence and demand deficits:
- **Food**: Living vegetation health, growth potential, and soil fertility (from M6).
- **Water**: Surface water presence, soil moisture, and proximity (from M5).
- **Shelter**: Overhead solid block raycast detection and sunlight exposure.
- **Resource Pressure**: Calculated when population demand exceeds local regenerative capacity.

### 3. Population Dynamics Model (`dynamics.py`)
Data-driven ecological dynamics across species guilds:
- `herbivore`: High vegetation dependence, moderate water dependence, carrying capacity 8.
- `small_animal`: Foraging seeds/insects, carrying capacity 12.
- `spider`: Crevice/darkness affinity, carrying capacity 10.
- `hostile`: Darkness/low-light affinity, indifferent to grazing vegetation.

### 4. Ecosystem System (`system.py`)
- Registered with `VerdantSimulationManager`.
- Bounded spatial queries ($r \le 16.0$) using `World.entityMap`.
- Zero whole-world scans or entity duplication.
- Provides safe, non-mutating query hooks for M6 vegetation feedback.
