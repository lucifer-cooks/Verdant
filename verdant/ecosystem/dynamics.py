"""Deterministic population dynamics, sustainability, and trend modeling for VERDANT M8."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


class VerdantPopulationDynamics:
    """Calculates ecological sustainability, stress, recovery, and trend.

    Translates local population density, habitat suitability, and resource pressure
    into deterministic ecological trajectories without mutating entity instances.
    """

    SPECIES_PROFILES: Dict[str, Dict[str, Any]] = {
        'herbivore': {
            'carrying_capacity': 8,
            'food_weight': 0.45,
            'water_weight': 0.35,
            'shelter_weight': 0.20,
            'stress_vulnerability': 1.00,
            'growth_rate': 0.80,
        },
        'small_animal': {
            'carrying_capacity': 12,
            'food_weight': 0.40,
            'water_weight': 0.30,
            'shelter_weight': 0.30,
            'stress_vulnerability': 0.85,
            'growth_rate': 1.00,
        },
        'spider': {
            'carrying_capacity': 10,
            'food_weight': 0.25,
            'water_weight': 0.25,
            'shelter_weight': 0.50,
            'stress_vulnerability': 0.70,
            'growth_rate': 0.90,
        },
        'hostile': {
            'carrying_capacity': 10,
            'food_weight': 0.15,
            'water_weight': 0.15,
            'shelter_weight': 0.70,
            'stress_vulnerability': 0.60,
            'growth_rate': 0.70,
        },
    }

    TREND_RECOVERING = 'recovering'
    TREND_GROWING = 'growing'
    TREND_STABLE = 'stable'
    TREND_PRESSURE = 'pressured'
    TREND_DECLINING = 'declining'

    def __init__(self, seed: Optional[int] = None):
        self.seed = int(seed) if seed is not None else 0

    def _clamp(self, val: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, float(val)))

    def _resolve_guild(self, species: str) -> str:
        s = str(species).lower()
        if s in ('herbivore', 'pig', 'sheep', 'cow', 'animal'):
            return 'herbivore'
        if s in ('small_animal', 'chicken', 'bird'):
            return 'small_animal'
        if s == 'spider':
            return 'spider'
        return 'hostile'

    def get_profile(self, species: str) -> Dict[str, Any]:
        guild = self._resolve_guild(species)
        return self.SPECIES_PROFILES.get(guild, self.SPECIES_PROFILES['hostile'])

    def calculate_density(self, count: int, species: str = 'herbivore') -> float:
        profile = self.get_profile(species)
        cap = float(profile['carrying_capacity'])
        return self._clamp(count / cap)

    def calculate_population_pressure(self, count: int, species: str = 'herbivore') -> float:
        density = self.calculate_density(count, species)
        if density <= 0.25:
            return density * 0.40
        elif density <= 0.75:
            return 0.10 + (density - 0.25) * 0.90
        else:
            return min(1.0, 0.55 + (density - 0.75) * 1.80)

    def calculate_habitat_pressure(self, habitat_quality: float, count: int,
                                   species: str = 'herbivore') -> float:
        density = self.calculate_density(count, species)
        # Low habitat quality combined with moderate-high density creates severe habitat pressure
        deficit = 1.0 - self._clamp(habitat_quality)
        return self._clamp(deficit * 0.70 + density * 0.30)

    def calculate_ecological_stress(self, habitat_pressure: float, resource_pressure: float,
                                   base_stress: float, species: str = 'herbivore') -> float:
        profile = self.get_profile(species)
        vuln = profile['stress_vulnerability']
        raw = 0.45 * resource_pressure + 0.35 * habitat_pressure + 0.20 * base_stress
        return self._clamp(raw * vuln)

    def calculate_sustainability(self, habitat_quality: float, food: float,
                                 water: float, shelter: float, population_pressure: float,
                                 species: str = 'herbivore') -> float:
        profile = self.get_profile(species)
        fw = profile['food_weight']
        ww = profile['water_weight']
        sw = profile['shelter_weight']

        resource_score = fw * food + ww * water + sw * shelter
        support_capacity = 0.60 * resource_score + 0.40 * habitat_quality
        sustainability = support_capacity - (0.50 * population_pressure)
        return self._clamp(sustainability)

    def calculate_recovery_tendency(self, sustainability: float, population_pressure: float,
                                    food: float, water: float, stress: float) -> float:
        """Calculates normalized recovery potential in [-1.0, 1.0].

        Positive (+): Environment is capable of regenerating and supporting growth.
        Negative (-): Environment and population are degrading under severe deficit.
        """
        if sustainability >= 0.60 and population_pressure <= 0.40 and stress <= 0.30:
            # Optimal regeneration conditions
            score = (sustainability - 0.50) * 1.60 + (0.50 - population_pressure) * 0.80
            return max(-1.0, min(1.0, score))
        elif sustainability < 0.35 or stress >= 0.65 or food < 0.15 or water < 0.15:
            # Degradation conditions
            severity = max(0.0, 0.40 - sustainability) + max(0.0, stress - 0.50)
            return max(-1.0, min(1.0, -0.20 - severity * 1.50))
        else:
            # Balanced neutral buffer
            diff = sustainability - (population_pressure * 0.60 + stress * 0.40)
            return max(-1.0, min(1.0, diff * 0.80))

    def calculate_expansion_tendency(self, sustainability: float, population_pressure: float,
                                     density: float, stress: float) -> float:
        """Calculates territorial outward migration tendency in [0.0, 1.0].

        High when population is thriving and crowding its carrying capacity.
        Low when population is sparse or dying from starvation/stress.
        """
        if stress >= 0.70:
            # Starving, dying populations conserve energy rather than expanding
            return 0.05

        if sustainability >= 0.55 and density >= 0.60:
            # Healthy, crowded herd expanding into neighboring territory
            score = 0.40 + (density - 0.50) * 0.80 + (sustainability - 0.50) * 0.40
            return self._clamp(score)
        elif density >= 0.75:
            # Severe overcrowding forced outward drift
            return self._clamp(0.40 + (density - 0.75) * 1.20)
        else:
            return self._clamp(density * 0.25)

    def classify_trend(self, sustainability: float, population_pressure: float,
                       recovery_tendency: float, density: float) -> str:
        if recovery_tendency >= 0.40 and sustainability >= 0.70:
            return self.TREND_RECOVERING
        elif recovery_tendency > 0.10 and sustainability >= 0.55 and density >= 0.40:
            return self.TREND_GROWING
        elif recovery_tendency <= -0.30 or sustainability <= 0.25:
            return self.TREND_DECLINING
        elif population_pressure >= 0.70 or recovery_tendency < -0.10:
            return self.TREND_PRESSURE
        else:
            return self.TREND_STABLE
