"""Deterministic resource pressure and availability evaluator for VERDANT M8."""

from __future__ import annotations

from typing import Any, Dict, Optional


class VerdantResourceEvaluator:
    """Evaluates food, water, and shelter resource availability and pressure.

    Measures existing ecological state from M3 (climate), M5 (moisture), and M6 (vegetation)
    without creating fake resource blocks, altering water physics, or running whole-world scans.
    """

    def __init__(self, seed: Optional[int] = None):
        self.seed = int(seed) if seed is not None else 0

    def _clamp(self, val: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, float(val)))

    def evaluate_food_availability(self, species: str, growth_potential: float,
                                   vegetation_health: float, fertility: float,
                                   biome_name: str = 'Plains') -> float:
        s = str(species).lower()
        if s in ('herbivore', 'pig', 'sheep', 'cow', 'animal'):
            # Herbivores directly graze on living vegetation, grass, and fertile ground
            score = 0.40 * growth_potential + 0.35 * vegetation_health + 0.25 * fertility
            if biome_name == 'Desert':
                score *= 0.15
            elif biome_name in ('Snow/Tundra', 'Mountains'):
                score *= 0.45
            return self._clamp(score)
        elif s in ('small_animal', 'chicken', 'bird'):
            # Small animals forage for seeds, insects, and vegetation undergrowth
            score = 0.35 * fertility + 0.35 * growth_potential + 0.30 * vegetation_health
            if biome_name == 'Desert':
                score *= 0.20
            return self._clamp(score)
        elif s == 'spider':
            # Spiders prey on insects/small organisms, flourishing in moist forests/caves
            score = 0.50 + 0.30 * fertility + 0.20 * vegetation_health
            return self._clamp(score)
        else:
            # Hostiles (zombie, skeleton, creeper): organic activity / general presence
            return self._clamp(0.50 + 0.30 * fertility + 0.20 * growth_potential)

    def evaluate_water_availability(self, soil_moisture: float, surface_water: float,
                                    water_proximity: float) -> float:
        # Evaluates natural hydration access
        score = 0.35 * float(soil_moisture) + 0.35 * float(water_proximity) + 0.30 * float(surface_water)
        return self._clamp(score)

    def evaluate_shelter_availability(self, species: str, x: float, y: float, z: float,
                                     world=None, sunlight: float = 0.5,
                                     elevation: float = 0.0) -> float:
        s = str(species).lower()
        # Direct check for overhead block coverage if world is provided
        if world is not None:
            try:
                ix, iy, iz = int(x), int(y), int(z)
                overhead_solid = 0
                for dy in range(1, 7):
                    if world.isBlockNormalCube(ix, iy + dy, iz):
                        overhead_solid += 1
                if overhead_solid > 0:
                    return self._clamp(0.60 + overhead_solid * 0.08)
            except Exception:
                pass

        # In open air, sunlight is inverse to shelter for dark/nocturnal creatures
        if s in ('hostile', 'zombie', 'skeleton', 'creeper', 'spider', 'monster'):
            shelter = (1.0 - float(sunlight)) * 0.75 + 0.25
        else:
            # Animals seek mild natural enclosure; extreme exposure reduces shelter
            shelter = 0.60 + 0.20 * (1.0 - abs(sunlight - 0.70))

        if elevation > 40.0:
            shelter -= min(0.25, (elevation - 40.0) * 0.008)
        return self._clamp(shelter)

    def calculate_resource_pressure(self, food: float, water: float, shelter: float,
                                     population_demand: float, species: str = 'herbivore') -> float:
        """Calculates normalized resource deficit pressure when demand exceeds availability."""
        s = str(species).lower()
        if s in ('herbivore', 'pig', 'sheep', 'cow', 'animal'):
            # Herbivores are highly sensitive to food and water shortages
            resource_capacity = 0.50 * food + 0.35 * water + 0.15 * shelter
        elif s in ('small_animal', 'chicken'):
            resource_capacity = 0.40 * food + 0.30 * water + 0.30 * shelter
        elif s in ('hostile', 'zombie', 'skeleton', 'creeper', 'spider'):
            resource_capacity = 0.20 * food + 0.20 * water + 0.60 * shelter
        else:
            resource_capacity = 0.40 * food + 0.35 * water + 0.25 * shelter

        # If population demand exceeds resource capacity, pressure rises
        demand = self._clamp(population_demand)
        if resource_capacity >= demand:
            # Low to moderate resource pressure
            base_pressure = max(0.0, demand * 0.30 + (1.0 - resource_capacity) * 0.20)
        else:
            shortfall = demand - resource_capacity
            base_pressure = min(1.0, 0.40 + shortfall * 1.20)

        # Extreme starvation condition: if critical resource is nearly 0
        if s in ('herbivore', 'pig', 'sheep') and (food < 0.10 or water < 0.10):
            base_pressure = max(base_pressure, 0.75)

        return self._clamp(base_pressure)
