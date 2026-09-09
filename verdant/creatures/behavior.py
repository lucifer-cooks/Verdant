"""Deterministic behavior context and tendency model for VERDANT creatures (M7)."""

from __future__ import annotations

from typing import Any, Dict, Tuple


class VerdantBehaviorContext:
    """Evaluates ecological behavior contexts and tendencies for creatures.

    Acts as an advisory, observational layer that exposes decision-support context
    without overriding or mutating the legacy Indev creature AI.
    """

    CONTEXTS = (
        'idle',
        'wander',
        'seek_food',
        'seek_water',
        'seek_shelter',
        'avoid_stress',
        'flee',
        'investigate',
    )

    ACTIVITIES = (
        'resting',
        'active',
        'foraging',
        'seeking_refuge',
    )

    def determine_behavior(self, species: str, habitat_score: float, food_score: float,
                           water_score: float, shelter_score: float, safety_score: float,
                           population_pressure: float, stress: float, is_daylight: bool = True,
                           day_phase: int = 6000) -> Dict[str, Any]:
        s = str(species).lower()
        is_herbivore = s in {'pig', 'sheep', 'cow', 'animal', 'chicken'}
        is_undead = s in {'zombie', 'skeleton'}

        # 1. Critical safety threats (e.g. Undead in direct daylight)
        if safety_score < 0.20:
            if is_undead and is_daylight:
                return {
                    'behavior_context': 'seek_shelter',
                    'activity': 'seeking_refuge',
                }
            return {
                'behavior_context': 'flee',
                'activity': 'seeking_refuge',
            }

        # 2. Extreme environmental or population stress
        if population_pressure >= 0.75 or stress >= 0.70:
            return {
                'behavior_context': 'avoid_stress',
                'activity': 'active',
            }

        # 3. Resource deficiencies for herbivores
        if is_herbivore:
            if water_score < 0.25:
                return {
                    'behavior_context': 'seek_water',
                    'activity': 'foraging',
                }
            if food_score < 0.30:
                return {
                    'behavior_context': 'seek_food',
                    'activity': 'foraging',
                }

        # 4. Severe shelter deficiency for night creatures during dawn/day
        if (is_undead or s == 'creeper') and is_daylight and shelter_score < 0.40:
            return {
                'behavior_context': 'seek_shelter',
                'activity': 'seeking_refuge',
            }

        # 5. Night resting / day activity cycle for animals
        if is_herbivore and not is_daylight:
            return {
                'behavior_context': 'idle',
                'activity': 'resting',
            }

        # 6. Favorable conditions: active wandering or investigating
        if habitat_score >= 0.70 and food_score >= 0.60 and water_score >= 0.50:
            # Well-satisfied creature: idle resting or calm wandering
            if day_phase % 4000 < 1500:
                return {
                    'behavior_context': 'idle',
                    'activity': 'resting',
                }
            return {
                'behavior_context': 'wander',
                'activity': 'active',
            }

        if habitat_score < 0.45:
            return {
                'behavior_context': 'investigate',
                'activity': 'active',
            }

        return {
            'behavior_context': 'wander',
            'activity': 'active',
        }

    def calculate_movement_bias(self, behavior_context: str, x: float, y: float, z: float,
                                noise_source=None) -> Tuple[float, float, float]:
        if noise_source is not None:
            nx = float(noise_source.noise(int(x) + 11, int(y) + 3, int(z) + 17))
            nz = float(noise_source.noise(int(x) + 23, int(y) + 7, int(z) + 31))
        else:
            nx = 0.0
            nz = 0.0

        if behavior_context in ('idle', 'resting'):
            return (0.0, 0.0, 0.0)
        elif behavior_context in ('seek_shelter', 'flee', 'avoid_stress'):
            # Heightened directional impetus away from open center
            length = (nx * nx + nz * nz + 0.001) ** 0.5
            return (nx / length, 0.0, nz / length)
        else:
            # Gentle wandering bias
            return (nx * 0.5, 0.0, nz * 0.5)
