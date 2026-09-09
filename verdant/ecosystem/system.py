"""Deterministic creature ecosystem and population dynamics system for VERDANT M8."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from verdant.creatures.system import VerdantCreatureSystem
from verdant.ecology.system import VerdantEcologySystem
from verdant.ecosystem.dynamics import VerdantPopulationDynamics
from verdant.ecosystem.population import VerdantPopulationSample
from verdant.ecosystem.resources import VerdantResourceEvaluator
from verdant.environment.climate import VerdantClimateSystem
from verdant.environment.seed import VerdantWorldSeed
from verdant.simulation.system import VerdantSystem
from verdant.water.system import VerdantWaterSystem


class VerdantEcosystemSystem(VerdantSystem):
    """Macro-ecological population dynamics and resource pressure simulation layer.

    Evaluates local populations and habitat quality within bounded regions (radius <= 16.0).
    Hooks into VerdantSimulationManager without creating duplicate entities or threads.
    """

    MAX_EVALUATION_RADIUS = 16.0

    def __init__(self, world_state=None, climate_system=None, water_system=None,
                 ecology_system=None, creature_system=None, clock=None, *,
                 name: str = 'verdant_ecosystem', seed: Optional[int] = None):
        super().__init__(name=name)
        self.world_state = world_state
        self.climate_system = climate_system
        self.water_system = water_system
        self.ecology_system = ecology_system
        self.creature_system = creature_system
        self.clock = clock

        if seed is not None:
            self.seed = int(seed)
        elif world_state is not None and hasattr(world_state, 'metadata') and 'seed' in world_state.metadata:
            self.seed = int(world_state.metadata['seed'])
        else:
            self.seed = 0

        self.seed_source = VerdantWorldSeed(self.seed)
        self.resource_evaluator = VerdantResourceEvaluator(self.seed)
        self.dynamics = VerdantPopulationDynamics(self.seed)

    def initialize(self, context=None):
        if context and 'world' in context:
            self.bind_world(context['world'])
        if self.world_state is not None and hasattr(self.world_state, 'metadata') and 'seed' in self.world_state.metadata:
            self.seed = int(self.world_state.metadata['seed'])
        self.seed_source = VerdantWorldSeed(self.seed)
        self.initialized = True
        return self

    def bind_world(self, world):
        if self.world_state is not None:
            self.world_state.bind_world(world)
        if self.climate_system is not None and hasattr(self.climate_system, 'world_state') and self.climate_system.world_state is not None:
            self.climate_system.world_state.bind_world(world)
        if self.water_system is not None:
            self.water_system.bind_world(world)
        if self.ecology_system is not None:
            self.ecology_system.bind_world(world)
        if self.creature_system is not None:
            self.creature_system.bind_world(world)
        return self

    def bind_climate_system(self, climate_system):
        self.climate_system = climate_system
        return self

    def bind_water_system(self, water_system):
        self.water_system = water_system
        return self

    def bind_ecology_system(self, ecology_system):
        self.ecology_system = ecology_system
        return self

    def bind_creature_system(self, creature_system):
        self.creature_system = creature_system
        return self

    def bind_clock(self, clock):
        self.clock = clock
        return self

    def _resolve_world(self):
        if self.world_state is not None and getattr(self.world_state, 'world', None) is not None:
            return self.world_state.world
        return None

    def _resolve_climate_system(self) -> VerdantClimateSystem:
        if self.climate_system is None:
            self.climate_system = VerdantClimateSystem(world_state=self.world_state, seed=self.seed)
        if self.water_system is not None:
            self.climate_system.water_system = self.water_system
        return self.climate_system

    def _resolve_water_system(self) -> VerdantWaterSystem:
        if self.water_system is not None:
            return self.water_system
        climate = self._resolve_climate_system()
        self.water_system = VerdantWaterSystem(world_state=self.world_state, climate_system=climate, seed=self.seed)
        if self.world_state is not None and getattr(self.world_state, 'world', None) is not None:
            self.water_system.bind_world(self.world_state.world)
        return self.water_system

    def _resolve_ecology_system(self) -> VerdantEcologySystem:
        if self.ecology_system is None:
            climate = self._resolve_climate_system()
            water = self._resolve_water_system()
            self.ecology_system = VerdantEcologySystem(
                world_state=self.world_state,
                climate_system=climate,
                water_system=water,
                clock=self.clock,
                seed=self.seed,
            )
        return self.ecology_system

    def _resolve_creature_system(self) -> VerdantCreatureSystem:
        if self.creature_system is None:
            climate = self._resolve_climate_system()
            water = self._resolve_water_system()
            ecology = self._resolve_ecology_system()
            self.creature_system = VerdantCreatureSystem(
                world_state=self.world_state,
                climate_system=climate,
                water_system=water,
                ecology_system=ecology,
                clock=self.clock,
                seed=self.seed,
            )
        return self.creature_system

    def get_world_age_ticks(self) -> int:
        if self.clock is not None:
            return int(self.clock.elapsed_ticks)
        if self.world_state is not None:
            return int(self.world_state.world_age_ticks)
        return 0

    def _sanitize_radius(self, radius: float) -> float:
        return max(1.0, min(self.MAX_EVALUATION_RADIUS, float(radius)))

    def count_local_entities(self, x: float, y: float, z: float, radius: float = 16.0,
                             species_filter: Optional[str] = None, world=None) -> int:
        """Counts existing living entities within a bounded spatial box.

        Never performs full world scans. Uses existing world.entityMap.
        """
        r = self._sanitize_radius(radius)
        w = world or self._resolve_world()
        if w is None:
            return 0

        min_x = x - r
        min_y = max(0.0, y - r)
        min_z = z - r
        max_x = x + r
        max_y = min(float(getattr(w, 'height', 64)), y + r)
        max_z = z + r

        entities = []
        if hasattr(w, 'entityMap') and w.entityMap is not None:
            try:
                entities = w.entityMap.getEntities(None, min_x, min_y, min_z, max_x, max_y, max_z)
            except Exception:
                entities = []
        elif hasattr(w, 'entities'):
            # Fallback for mock worlds
            entities = [
                e for e in w.entities
                if min_x <= e.posX <= max_x and min_y <= e.posY <= max_y and min_z <= e.posZ <= max_z
            ]

        filter_lower = species_filter.lower() if species_filter else None
        count = 0
        for ent in entities:
            cls_name = getattr(ent, 'entity_type', ent.__class__.__name__).lower()
            if not ('living' in cls_name or 'creature' in cls_name or 'animal' in cls_name or 'mob' in cls_name or 'pig' in cls_name or 'sheep' in cls_name or 'zombie' in cls_name or 'skeleton' in cls_name or 'spider' in cls_name or 'creeper' in cls_name):
                continue

            if filter_lower:
                if filter_lower in cls_name:
                    count += 1
                elif filter_lower == 'herbivore' and ('pig' in cls_name or 'sheep' in cls_name or 'cow' in cls_name or 'animal' in cls_name):
                    count += 1
                elif filter_lower == 'small_animal' and ('chicken' in cls_name or 'bird' in cls_name):
                    count += 1
                elif filter_lower == 'hostile' and ('zombie' in cls_name or 'skeleton' in cls_name or 'spider' in cls_name or 'creeper' in cls_name or 'mob' in cls_name):
                    count += 1
            else:
                count += 1

        return count

    def evaluate_population_sample(self, x: float, y: float, z: float, radius: float = 16.0,
                                   species: str = 'herbivore', world=None) -> VerdantPopulationSample:
        """Evaluates a localized population sample and ecological metrics."""
        r = self._sanitize_radius(radius)
        w = world or self._resolve_world()
        climate = self._resolve_climate_system()
        water = self._resolve_water_system()
        ecology = self._resolve_ecology_system()
        creatures = self._resolve_creature_system()

        ix, iy, iz = int(x), int(y), int(z)
        env = climate.get_environment(ix, iy, iz)
        moisture = water.get_soil_moisture(ix, iy, iz)
        surface_water = water.get_surface_water_presence(ix, iy, iz)
        water_prox = getattr(env, 'water_proximity', water.get_water_proximity(ix, iy, iz))
        fertility = ecology.get_fertility(ix, iy, iz, env=env, moisture=moisture)
        growth_potential = ecology.get_growth_potential(ix, iy, iz, env=env, moisture=moisture, fertility=fertility)
        veg_health = ecology.get_vegetation_health(ix, iy, iz, env=env, moisture=moisture, fertility=fertility)
        base_stress = ecology.get_environmental_stress(ix, iy, iz, env=env, moisture=moisture)

        # 1. Count entities within bounded radius
        count = self.count_local_entities(x, y, z, radius=r, species_filter=species, world=w)

        # 2. Resource evaluations
        food = self.resource_evaluator.evaluate_food_availability(
            species=species,
            growth_potential=growth_potential,
            vegetation_health=veg_health,
            fertility=fertility,
            biome_name=env.biome_name,
        )
        water_avail = self.resource_evaluator.evaluate_water_availability(
            soil_moisture=moisture,
            surface_water=surface_water,
            water_proximity=water_prox,
        )
        shelter = self.resource_evaluator.evaluate_shelter_availability(
            species=species,
            x=x, y=y, z=z,
            world=w,
            sunlight=env.sunlight,
            elevation=env.elevation,
        )

        # 3. Habitat quality from M7
        habitat_quality = creatures.get_habitat_score(species, x, y, z, world=w)

        # 4. Dynamics calculations
        density = self.dynamics.calculate_density(count, species)
        pop_pressure = self.dynamics.calculate_population_pressure(count, species)
        resource_pressure = self.resource_evaluator.calculate_resource_pressure(
            food=food,
            water=water_avail,
            shelter=shelter,
            population_demand=pop_pressure,
            species=species,
        )
        habitat_pressure = self.dynamics.calculate_habitat_pressure(habitat_quality, count, species)
        eco_stress = self.dynamics.calculate_ecological_stress(
            habitat_pressure=habitat_pressure,
            resource_pressure=resource_pressure,
            base_stress=base_stress,
            species=species,
        )
        sustainability = self.dynamics.calculate_sustainability(
            habitat_quality=habitat_quality,
            food=food,
            water=water_avail,
            shelter=shelter,
            population_pressure=pop_pressure,
            species=species,
        )
        recovery_tendency = self.dynamics.calculate_recovery_tendency(
            sustainability=sustainability,
            population_pressure=pop_pressure,
            food=food,
            water=water_avail,
            stress=eco_stress,
        )
        expansion_tendency = self.dynamics.calculate_expansion_tendency(
            sustainability=sustainability,
            population_pressure=pop_pressure,
            density=density,
            stress=eco_stress,
        )
        trend = self.dynamics.classify_trend(
            sustainability=sustainability,
            population_pressure=pop_pressure,
            recovery_tendency=recovery_tendency,
            density=density,
        )

        return VerdantPopulationSample(
            species=species,
            center_x=float(x),
            center_y=float(y),
            center_z=float(z),
            radius=float(r),
            count=count,
            density=density,
            habitat_quality=habitat_quality,
            food_availability=food,
            water_availability=water_avail,
            shelter_availability=shelter,
            population_pressure=pop_pressure,
            resource_pressure=resource_pressure,
            ecological_stress=eco_stress,
            sustainability=sustainability,
            recovery_tendency=recovery_tendency,
            expansion_tendency=expansion_tendency,
            trend=trend,
        )

    def get_herbivore_grazing_pressure(self, x: float, y: float, z: float, radius: float = 16.0,
                                       world=None) -> float:
        """Safe feedback query for M6 vegetation layer.

        Exposes ecological grazing pressure without modifying terrain blocks or scanning the world.
        """
        sample = self.evaluate_population_sample(x, y, z, radius=radius, species='herbivore', world=world)
        return sample.population_pressure

    def update(self, context=None, delta_ticks: int = 1):
        """Simulation manager tick hook.

        Maintains cadence without iterating over every world entity or block.
        """
        if context and 'world' in context:
            self.bind_world(context['world'])
        return self

    def snapshot(self) -> Dict[str, Any]:
        return {
            'initialized': self.initialized,
            'seed': self.seed,
            'world_age_ticks': self.get_world_age_ticks(),
        }

    def __repr__(self) -> str:
        return f"VerdantEcosystemSystem(seed={self.seed}, initialized={self.initialized})"
