"""Deterministic habitat evaluation model for VERDANT creatures (M7)."""

from __future__ import annotations

from typing import Any, Dict, Optional


class VerdantHabitatEvaluator:
    """Evaluates environmental suitability for living creatures across biomes.

    Combines climate (M3), moisture (M5), and vegetation condition (M6) into
    ecological suitability scores without modifying legacy entity behaviors.
    """

    HERBIVORES = {'pig', 'sheep', 'cow', 'animal'}
    SMALL_ANIMALS = {'chicken', 'bird'}
    HOSTILE_MOBS = {'zombie', 'skeleton', 'spider', 'creeper', 'giant', 'monster'}
    UNDEAD = {'zombie', 'skeleton'}

    def __init__(self, seed: Optional[int] = None):
        self.seed = int(seed) if seed is not None else 0

    BIOME_COMPATIBILITY: Dict[str, Dict[str, float]] = {
        'herbivore': {
            'Plains': 1.00,
            'Forest': 0.95,
            'Swamp': 0.70,
            'Mountains': 0.45,
            'Snow/Tundra': 0.30,
            'Desert': 0.10,
            'Ocean': 0.05,
        },
        'small_animal': {
            'Plains': 0.95,
            'Forest': 1.00,
            'Swamp': 0.80,
            'Mountains': 0.50,
            'Snow/Tundra': 0.35,
            'Desert': 0.20,
            'Ocean': 0.05,
        },
        'spider': {
            'Forest': 1.00,
            'Swamp': 0.90,
            'Mountains': 0.85,
            'Plains': 0.70,
            'Desert': 0.65,
            'Snow/Tundra': 0.40,
            'Ocean': 0.10,
        },
        'hostile': {
            'Mountains': 0.95,
            'Swamp': 0.90,
            'Forest': 0.85,
            'Desert': 0.80,
            'Snow/Tundra': 0.75,
            'Plains': 0.70,
            'Ocean': 0.10,
        },
    }

    def _clamp(self, value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, float(value)))

    def _get_category(self, species: str) -> str:
        s = str(species).lower()
        if s in self.HERBIVORES:
            return 'herbivore'
        if s in self.SMALL_ANIMALS:
            return 'small_animal'
        if s == 'spider':
            return 'spider'
        return 'hostile'

    def get_biome_compatibility(self, species: str, biome_name: str) -> float:
        category = self._get_category(species)
        compat_map = self.BIOME_COMPATIBILITY.get(category, self.BIOME_COMPATIBILITY['hostile'])
        return compat_map.get(biome_name, 0.50)

    def get_temperature_score(self, species: str, temperature: float, season: str = 'spring') -> float:
        category = self._get_category(species)
        temp = float(temperature)

        if category in ('herbivore', 'small_animal'):
            # Optimum: 14C to 24C
            if 14.0 <= temp <= 24.0:
                return 1.0
            elif temp < 14.0:
                # Cold penalty
                diff = 14.0 - temp
                return self._clamp(1.0 - (diff / 25.0))
            else:
                # Heat penalty
                diff = temp - 24.0
                return self._clamp(1.0 - (diff / 20.0))
        elif species.lower() == 'spider':
            # Spiders prefer 10C to 28C
            if 10.0 <= temp <= 28.0:
                return 1.0
            return self._clamp(1.0 - abs(temp - 19.0) / 30.0)
        else:
            # Undead / Monsters tolerate cold well, avoid extreme blistering heat
            if -10.0 <= temp <= 30.0:
                return 1.0
            return self._clamp(1.0 - abs(temp - 15.0) / 40.0)

    def get_moisture_score(self, species: str, soil_moisture: float, water_proximity: float = 0.0) -> float:
        category = self._get_category(species)
        moisture = float(soil_moisture)
        prox = float(water_proximity)

        if category in ('herbivore', 'small_animal'):
            # Herbivores need adequate moisture for grass and hydration
            base = 0.30 + 0.50 * moisture + 0.20 * prox
            if moisture < 0.15:
                base *= 0.40  # Severe drought penalty
            return self._clamp(base)
        else:
            # Monsters are largely indifferent to moisture, though swamps and moderate dampness are favored
            return self._clamp(0.60 + 0.30 * moisture + 0.10 * prox)

    def get_food_suitability(self, species: str, growth_potential: float, vegetation_health: float,
                             fertility: float, biome_name: str = 'Plains') -> float:
        category = self._get_category(species)
        if category in ('herbivore', 'small_animal'):
            # Direct dependency on living vegetation, growth potential, and soil fertility
            score = 0.40 * growth_potential + 0.35 * vegetation_health + 0.25 * fertility
            if biome_name == 'Desert':
                score *= 0.20
            elif biome_name == 'Snow/Tundra':
                score *= 0.40
            return self._clamp(score)
        else:
            # Hostile mobs do not graze; food suitability reflects prey availability / organic activity
            return self._clamp(0.50 + 0.30 * fertility + 0.20 * growth_potential)

    def get_water_access(self, species: str, soil_moisture: float, surface_water: float,
                         water_proximity: float) -> float:
        # Evaluates accessibility to natural hydration sources
        access = 0.35 * float(soil_moisture) + 0.35 * float(water_proximity) + 0.30 * float(surface_water)
        return self._clamp(access)

    def get_shelter_score(self, species: str, x: float, y: float, z: float,
                          world=None, sunlight: float = 0.5, elevation: float = 0.0) -> float:
        # Check overhead coverage from terrain or trees
        if world is not None:
            try:
                ix, iy, iz = int(x), int(y), int(z)
                overhead_solid = 0
                for dy in range(1, 6):
                    if world.isBlockNormalCube(ix, iy + dy, iz):
                        overhead_solid += 1
                if overhead_solid > 0:
                    return self._clamp(0.60 + overhead_solid * 0.10)
            except Exception:
                pass

        # In open air, sunlight is inverse to shelter; elevation penalizes exposure
        shelter = (1.0 - float(sunlight)) * 0.70 + 0.30
        if elevation > 40.0:
            shelter -= min(0.25, (elevation - 40.0) * 0.008)
        return self._clamp(shelter)

    def get_safety_score(self, species: str, ecological_stress: float, sunlight: float = 0.5,
                         is_daylight: bool = True) -> float:
        s = str(species).lower()
        stress = float(ecological_stress)
        sun = float(sunlight)

        if s in self.UNDEAD:
            # Zombies and Skeletons burn in direct sunlight during daytime!
            if is_daylight and sun > 0.60:
                return 0.10  # Extreme danger of burning
            return self._clamp(1.0 - 0.50 * stress)
        elif s in self.HOSTILE_MOBS:
            # Creepers and spiders tolerate light better but prefer darkness
            if is_daylight and sun > 0.75:
                return 0.40
            return self._clamp(1.0 - 0.50 * stress)
        else:
            # Passive animals prefer daylight and low environmental stress
            light_pref = sun * 0.30 if is_daylight else 0.10
            return self._clamp(0.70 * (1.0 - stress) + light_pref)

    def evaluate_habitat(self, species: str, temperature: float, soil_moisture: float,
                         water_proximity: float, surface_water: float, growth_potential: float,
                         vegetation_health: float, fertility: float, ecological_stress: float,
                         biome_name: str, sunlight: float = 0.5, elevation: float = 0.0,
                         season: str = 'spring', is_daylight: bool = True,
                         world=None, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> Dict[str, float]:
        temp_score = self.get_temperature_score(species, temperature, season)
        moist_score = self.get_moisture_score(species, soil_moisture, water_proximity)
        food_score = self.get_food_suitability(species, growth_potential, vegetation_health, fertility, biome_name)
        water_score = self.get_water_access(species, soil_moisture, surface_water, water_proximity)
        shelter_score = self.get_shelter_score(species, x, y, z, world=world, sunlight=sunlight, elevation=elevation)
        safety_score = self.get_safety_score(species, ecological_stress, sunlight, is_daylight)
        biome_compat = self.get_biome_compatibility(species, biome_name)

        category = self._get_category(species)
        if category in ('herbivore', 'small_animal'):
            composite = (
                0.25 * food_score
                + 0.20 * temp_score
                + 0.15 * water_score
                + 0.15 * moist_score
                + 0.15 * safety_score
                + 0.10 * biome_compat
            )
        else:
            composite = (
                0.30 * safety_score
                + 0.25 * shelter_score
                + 0.20 * temp_score
                + 0.15 * biome_compat
                + 0.10 * food_score
            )

        return {
            'habitat_score': self._clamp(composite),
            'temperature_score': temp_score,
            'moisture_score': moist_score,
            'food_score': food_score,
            'water_score': water_score,
            'shelter_score': shelter_score,
            'safety_score': safety_score,
            'biome_compatibility': biome_compat,
        }
