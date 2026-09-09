"""VERDANT M9 — Ecological Feedback & Adaptive World Architecture.

This package establishes the central ecological feedback loop connecting climate (M3),
water (M5), vegetation condition (M6), creature habitats (M7), and population dynamics (M8).

Core Architecture Principles:
-----------------------------
1. KEEP -> STUDY -> WRAP -> EXTEND -> eventually REPLACE:
   - Original Minecraft Indev engine remains authoritative for blocks, entities, fluids, and AI.
   - Non-destructive macro-feedback that measures and predicts system response without
     destroying blocks or altering water physics.

2. Unidirectional Non-Circular Evaluation Flow:
   - Update cadence: Clock -> Climate -> Moisture -> Vegetation -> Creature Habitat -> Population Dynamics -> Feedback System.
   - Feedback is exposed as state for consumption in subsequent cycles.

3. Temporal Smoothing & Hysteresis:
   - Signals adapt smoothly without erratic one-tick flipping.
"""

from verdant.feedback.signals import VerdantEcologicalSignals
from verdant.feedback.vegetation_feedback import VerdantVegetationFeedback
from verdant.feedback.habitat_feedback import VerdantHabitatFeedback
from verdant.feedback.water_feedback import VerdantWaterFeedback
from verdant.feedback.system import VerdantFeedbackSystem
from verdant.feedback.queries import (
    get_ecosystem_state,
    get_ecological_health,
    get_grazing_pressure,
    get_vegetation_stress,
    get_vegetation_recovery,
    get_habitat_pressure,
    get_water_stress,
    get_drought_pressure,
    get_population_pressure,
    get_adaptive_response,
    explain_ecosystem,
)

__all__ = [
    'VerdantEcologicalSignals',
    'VerdantVegetationFeedback',
    'VerdantHabitatFeedback',
    'VerdantWaterFeedback',
    'VerdantFeedbackSystem',
    'get_ecosystem_state',
    'get_ecological_health',
    'get_grazing_pressure',
    'get_vegetation_stress',
    'get_vegetation_recovery',
    'get_habitat_pressure',
    'get_water_stress',
    'get_drought_pressure',
    'get_population_pressure',
    'get_adaptive_response',
    'explain_ecosystem',
]
