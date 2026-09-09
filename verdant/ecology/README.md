# VERDANT Ecology & Vegetation Condition (M6)

## Overview

The `verdant.ecology` package introduces the temporal environmental condition layer for VERDANT. In earlier milestones (M1–M5), world vegetation and moisture were calculated as static properties or generation-time placements. M6 establishes how environmental favorability, vegetation health, fertility, and stress evolve across simulation time and seasons without physically altering terrain blocks or introducing costly full-world scans.

## Conceptual Pipeline

```
Simulation Clock (world_age_ticks)
       ↓
Season / Climate Progression (VerdantClimateSystem)
       ↓
Dynamic Moisture & Proximity (VerdantWaterSystem)
       ↓
Vegetation Rules & Biome Preferences (VerdantVegetationRuleSet)
       ↓
Vegetation Condition State (VerdantVegetationState)
       ↓
Growth Potential / Fertility / Health / Environmental Stress
```

## Key Components

### 1. `VerdantVegetationState`
A lightweight, immutable dataclass representing the environmental suitability profile for any `(x, y, z)` location:
- `growth_potential`: Normalized `[0.0, 1.0]` indicator of how favorably plants can grow right now.
- `moisture`: Normalized `[0.0, 1.0]` soil moisture level integrated from M5.
- `temperature_suitability`: Normalized `[0.0, 1.0]` proximity to biological optimums.
- `sunlight`: Sunlight exposure `[0.0, 1.0]`.
- `fertility`: Soil/biome biological fertility `[0.0, 1.0]`.
- `stress`: Cumulative environmental stress (drought, cold, extreme heat, darkness) in `[0.0, 1.0]`.
- `health`: Overall vegetation vitality in `[0.0, 1.0]`.
- `season`: Current season (`spring`, `summer`, `autumn`, `winter`).
- `season_progress`: Normalized progress `[0.0, 1.0]` through the active season.
- `biome_name`: Resolved biome.
- `events`: Tuple of triggered ecological events (`growth_favorable`, `drought_stress`, `cold_stress`, `moisture_recovery`).

### 2. `VerdantEcologySystem`
A standard `VerdantSystem` that registers into `VerdantSimulationManager`:
- Advances deterministically with world age / simulation ticks.
- Uses data-driven seasonal profiles:
  - **Spring**: High growth potential (`+0.20`), strong moisture response (`1.20x`), low base stress (`0.05`).
  - **Summer**: Highest peak growth potential (`+0.25`), elevated heat/drought stress factor.
  - **Autumn**: Declining growth potential (`-0.05`), moderate temperatures.
  - **Winter**: Lowest growth potential (`-0.35`), highest cold stress (`+0.45x`), reduced moisture absorption.
- **Zero World Scans**: Operates as a stateless mathematical query engine over deterministic noise and climate samples.
- **Zero Global Randomness**: Every query derives solely from `(world_seed, x, y, z, world_age_ticks)`.

### 3. Convenience Queries (`verdant.ecology.queries`)
- `get_vegetation_state(x, y, z, ...)`
- `get_growth_potential(x, y, z, ...)`
- `get_vegetation_health(x, y, z, ...)`
- `get_environmental_stress(x, y, z, ...)`
- `get_fertility(x, y, z, ...)`
- `get_season_modifier(x, y, z, ...)`
- `get_current_season(...)`
- `get_season_progress(...)`
- `is_growth_favorable(x, y, z, ...)`

## Performance & Scaling Principles

- **No per-block object allocation**: States are transient query results.
- **No independent background loop**: Ticks arrive strictly through `VerdantSimulationManager.update()`.
- **Backward Compatibility**: Fully integrates with existing Indev plant blocks, M2 simulation clocks, M3 climate, M4 vegetation rules, and M5 dynamic water.
