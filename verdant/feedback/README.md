# VERDANT M9 — Ecological Feedback & Adaptive World

## Overview

The `verdant.feedback` package establishes the central closed-loop feedback layer of the VERDANT simulation:

```
M3 Climate / Biome
      ↓
M5 Moisture & Hydration
      ↓
M6 Vegetation Health & Stress
      ↓
M7 Creature Habitat
      ↓
M8 Population & Resource Dynamics
      ↓
M9 Ecological Feedback (Grazing, Drought, Habitat Pressure, Adaptive Response)
      └──────────────────────────────────────────────────────────→ Cycle Closes
```

Following the core VERDANT principle:
**KEEP → STUDY → WRAP → EXTEND → eventually REPLACE**

The authoritative Minecraft Indev game engine remains untouched. M9 adds an intelligent macro-feedback layer that allows the living world to understand its own health and stability without destroying blocks, altering fluid mechanics, or replacing entity AI.

---

## Key Modules

### 1. Ecological Signals (`signals.py`)
Encapsulates 10 normalized signals in $[0.0, 1.0]$:
- `grazing_pressure`: Herbivore feeding demand.
- `vegetation_stress`: Cumulative vegetation strain under climate and grazing.
- `vegetation_recovery`: Natural regrowth capability.
- `habitat_pressure`: Ecological crowding and resource deficits.
- `resource_pressure`: Demand outstripping local resource capacity.
- `water_stress`: Local hydrological deficit.
- `drought_pressure`: Aridification pressure.
- `population_pressure`: Bounded creature saturation.
- `ecological_health`: Composite multi-factor health index.
- `ecosystem_stability`: Resilience to environmental perturbations.
- `adaptive_response`: Trajectory (`'thriving'`, `'healthy'`, `'stable'`, `'stressed'`, `'recovering'`, `'degraded'`).

### 2. Vegetation Feedback (`vegetation_feedback.py`)
- Modulates vegetation stress as a function of herbivore grazing pressure and soil moisture.
- Calculates regrowth recovery potential without physical block destruction.

### 3. Habitat Feedback (`habitat_feedback.py`)
- Modulates creature habitat suitability in response to population pressure and resource exhaustion.
- Authoritative Indev mob spawning and AI remain unchanged.

### 4. Water Feedback (`water_feedback.py`)
- Evaluates evaporative demand, rainfall shortfalls, and drought pressure.
- No modifications to Indev fluid physics.

### 5. Feedback System & Temporal Smoothing (`system.py`)
- Registered with `VerdantSimulationManager`.
- Unidirectional execution to prevent circular dependencies.
- Bounded spatial queries ($r \le 16.0$ blocks).
- Temporal smoothing and hysteresis cache to prevent erratic 1-tick fluctuations.
