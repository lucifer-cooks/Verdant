"""Deterministic creature and living ecosystem simulation system for VERDANT M7."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from verdant.creatures.behavior import VerdantBehaviorContext
from verdant.creatures.creature_state import VerdantCreatureState
from verdant.creatures.habitat import VerdantHabitatEvaluator
from verdant.ecology.system import VerdantEcologySystem
from verdant.environment.climate import VerdantClimateSystem
from verdant.environment.seed import VerdantWorldSeed
from verdant.simulation.system import VerdantSystem
from verdant.water.system import VerdantWaterSystem


class VerdantCreatureSystem(VerdantSystem):
    """Deterministic ecological creature and habitat layer for VERDANT.

    Observes existing Indev entities and evaluates their ecological habitat,
    local population pressure, environmental stress, and behavioral context
    without mutating the legacy entity engine or AI pathfinding.
    """

    def __init__(self, world_state=None, climate_system=None, water_system=None,
                 ecology_system=None, clock=None, *, name: str = 'verdant_creatures',
                 seed: Optional[int] = None):
        super().__init__(name=name)
        self.world_state = world_state
        self.climate_system = climate_system
        self.water_system = water_system
        self.ecology_system = ecology_system
        self.clock = clock

        if seed is not None:
            self.seed = int(seed)
        elif world_state is not None and hasattr(world_state, 'metadata') and 'seed' in world_state.metadata:
            self.seed = int(world_state.metadata['seed'])
        else:
            self.seed = 0

        self.seed_source = VerdantWorldSeed(self.seed)
        self.habitat_evaluator = VerdantHabitatEvaluator()
        self.behavior_evaluator = VerdantBehaviorContext()

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

    def get_world_age_ticks(self) -> int:
        if self.clock is not None:
            return int(self.clock.elapsed_ticks)
        if self.world_state is not None:
            return int(self.world_state.world_age_ticks)
        return 0

    def get_current_season(self) -> str:
        if self.clock is not None:
            return str(self.clock.get_current_season())
        if self.world_state is not None:
            return str(self.world_state.current_season)
        return 'spring'

    def is_daylight(self, world=None) -> bool:
        w = world or self._resolve_world()
        if w is not None and hasattr(w, 'worldTime'):
            phase = int(w.worldTime) % 24000
            return phase < 12000
        ticks = self.get_world_age_ticks() % 24000
        return ticks < 12000

    def _identify_species(self, entity_or_species: Any) -> Tuple[str, Optional[int], float, float, float]:
        if isinstance(entity_or_species, str):
            return entity_or_species.lower(), None, 0.0, 0.0, 0.0

        # Handle existing Indev Entity instance
        cls_name = entity_or_species.__class__.__name__.lower()
        species = 'animal'
        if 'pig' in cls_name:
            species = 'pig'
        elif 'sheep' in cls_name:
            species = 'sheep'
        elif 'cow' in cls_name:
            species = 'cow'
        elif 'chicken' in cls_name:
            species = 'chicken'
        elif 'zombie' in cls_name:
            species = 'zombie'
        elif 'skeleton' in cls_name:
            species = 'skeleton'
        elif 'spider' in cls_name:
            species = 'spider'
        elif 'creeper' in cls_name:
            species = 'creeper'
        elif 'giant' in cls_name:
            species = 'giant'
        elif 'mob' in cls_name or 'monster' in cls_name:
            species = 'monster'

        entity_id = getattr(entity_or_species, 'entityId', None)
        x = float(getattr(entity_or_species, 'posX', 0.0))
        y = float(getattr(entity_or_species, 'posY', 0.0))
        z = float(getattr(entity_or_species, 'posZ', 0.0))
        return species, entity_id, x, y, z

    def _map_entity_to_species(self, entity: Any) -> str:
        species, _, _, _, _ = self._identify_species(entity)
        return species

    def get_or_evaluate_creature(self, entity: Any, world=None, tick: Optional[int] = None) -> VerdantCreatureState:
        return self.get_creature_state(entity, world=world)

    def calculate_population_pressure(self, entity_or_x: Any, world=None, y: float = 0.0,
                                     z: float = 0.0, radius: float = 16.0) -> float:
        if not isinstance(entity_or_x, (int, float)):
            x = float(getattr(entity_or_x, 'posX', 0.0))
            y = float(getattr(entity_or_x, 'posY', 0.0))
            z = float(getattr(entity_or_x, 'posZ', 0.0))
            return self.get_population_pressure(x, y, z, radius=radius, world=world)
        return self.get_population_pressure(float(entity_or_x), y, z, radius=radius, world=world)

    def get_population_pressure(self, x: float, y: float, z: float, radius: float = 16.0,
                                world=None) -> float:
        """Calculate normalized local population pressure within a bounded radius.

        Never performs full world scans. Uses existing entityMap if available, or
        evaluates against nearby entities in the local neighborhood.
        """
        w = world or self._resolve_world()
        if w is not None and hasattr(w, 'entityMap') and w.entityMap is not None:
            try:
                # Bounded AABB search in the existing spatial hash
                r = float(radius)
                min_x = x - r
                min_y = max(0.0, y - r)
                min_z = z - r
                max_x = x + r
                max_y = min(float(getattr(w, 'height', 64)), y + r)
                max_z = z + r

                entities = w.entityMap.getEntities(None, min_x, min_y, min_z, max_x, max_y, max_z)
                count = 0
                for ent in entities:
                    # Count living creatures
                    cls_name = ent.__class__.__name__
                    if 'Living' in cls_name or 'Creature' in cls_name or 'Animal' in cls_name or 'Mob' in cls_name:
                        count += 1

                # 0-1 entities: low pressure (0.0 - 0.15)
                # 4-6 entities: moderate pressure (0.45 - 0.65)
                # 10+ entities: maximum saturation (1.0)
                return max(0.0, min(1.0, count / 10.0))
            except Exception:
                pass

        # Deterministic spatial noise fallback if world entityMap is unavailable
        noise_val = abs(self.seed_source.noise(int(x) + 47, int(y) + 19, int(z) + 61))
        return max(0.0, min(1.0, noise_val * 0.40))

    def get_creature_state(self, entity_or_species: Any, x: Optional[float] = None,
                           y: Optional[float] = None, z: Optional[float] = None,
                           world=None) -> VerdantCreatureState:
        species, entity_id, def_x, def_y, def_z = self._identify_species(entity_or_species)
        pos_x = float(x if x is not None else def_x)
        pos_y = float(y if y is not None else def_y)
        pos_z = float(z if z is not None else def_z)

        w = world or self._resolve_world()
        climate = self._resolve_climate_system()
        water = self._resolve_water_system()
        ecology = self._resolve_ecology_system()

        ix, iy, iz = int(pos_x), int(pos_y), int(pos_z)
        env = climate.get_environment(ix, iy, iz)
        moisture = getattr(env, 'soil_moisture', None)
        if moisture is None:
            moisture = water.get_soil_moisture(ix, iy, iz)

        surface_water = water.get_surface_water_presence(ix, iy, iz)
        water_prox = getattr(env, 'water_proximity', water.get_water_proximity(ix, iy, iz))
        fertility = ecology.get_fertility(ix, iy, iz, env=env, moisture=moisture)
        growth_potential = ecology.get_growth_potential(ix, iy, iz, env=env, moisture=moisture, fertility=fertility)
        veg_health = ecology.get_vegetation_health(ix, iy, iz, env=env, moisture=moisture, fertility=fertility)
        stress = ecology.get_environmental_stress(ix, iy, iz, env=env, moisture=moisture)
        season = self.get_current_season()
        daylight = self.is_daylight(w)

        # Habitat evaluation
        habitat_data = self.habitat_evaluator.evaluate_habitat(
            species=species,
            temperature=env.temperature,
            soil_moisture=moisture,
            water_proximity=water_prox,
            surface_water=surface_water,
            growth_potential=growth_potential,
            vegetation_health=veg_health,
            fertility=fertility,
            ecological_stress=stress,
            biome_name=env.biome_name,
            sunlight=env.sunlight,
            elevation=env.elevation,
            season=season,
            is_daylight=daylight,
            world=w,
            x=pos_x, y=pos_y, z=pos_z,
        )

        pop_pressure = self.get_population_pressure(pos_x, pos_y, pos_z, world=w)

        # Behavior context
        day_phase = self.get_world_age_ticks() % 24000
        behavior_data = self.behavior_evaluator.determine_behavior(
            species=species,
            habitat_score=habitat_data['habitat_score'],
            food_score=habitat_data['food_score'],
            water_score=habitat_data['water_score'],
            shelter_score=habitat_data['shelter_score'],
            safety_score=habitat_data['safety_score'],
            population_pressure=pop_pressure,
            stress=stress,
            is_daylight=daylight,
            day_phase=day_phase,
        )

        movement_bias = self.behavior_evaluator.calculate_movement_bias(
            behavior_context=behavior_data['behavior_context'],
            x=pos_x, y=pos_y, z=pos_z,
            noise_source=self.seed_source,
        )

        return VerdantCreatureState(
            species=species,
            entity_id=entity_id,
            x=pos_x,
            y=pos_y,
            z=pos_z,
            habitat_score=habitat_data['habitat_score'],
            temperature_score=habitat_data['temperature_score'],
            moisture_score=habitat_data['moisture_score'],
            food_score=habitat_data['food_score'],
            water_score=habitat_data['water_score'],
            shelter_score=habitat_data['shelter_score'],
            safety_score=habitat_data['safety_score'],
            population_pressure=pop_pressure,
            stress=stress,
            activity=behavior_data['activity'],
            movement_bias=movement_bias,
            behavior_context=behavior_data['behavior_context'],
        )

    def get_habitat_score(self, entity_or_species: Any, x: Optional[float] = None,
                          y: Optional[float] = None, z: Optional[float] = None,
                          world=None) -> float:
        state = self.get_creature_state(entity_or_species, x, y, z, world=world)
        return state.habitat_score

    def get_food_suitability(self, entity_or_species: Any, x: Optional[float] = None,
                             y: Optional[float] = None, z: Optional[float] = None,
                             world=None) -> float:
        state = self.get_creature_state(entity_or_species, x, y, z, world=world)
        return state.food_score

    def get_water_access(self, entity_or_species: Any, x: Optional[float] = None,
                         y: Optional[float] = None, z: Optional[float] = None,
                         world=None) -> float:
        state = self.get_creature_state(entity_or_species, x, y, z, world=world)
        return state.water_score

    def get_shelter_score(self, entity_or_species: Any, x: Optional[float] = None,
                          y: Optional[float] = None, z: Optional[float] = None,
                          world=None) -> float:
        state = self.get_creature_state(entity_or_species, x, y, z, world=world)
        return state.shelter_score

    def get_activity_tendency(self, entity_or_species: Any, x: Optional[float] = None,
                             y: Optional[float] = None, z: Optional[float] = None,
                             world=None) -> str:
        state = self.get_creature_state(entity_or_species, x, y, z, world=world)
        return state.activity

    def get_behavior_context(self, entity_or_species: Any, x: Optional[float] = None,
                             y: Optional[float] = None, z: Optional[float] = None,
                             world=None) -> str:
        state = self.get_creature_state(entity_or_species, x, y, z, world=world)
        return state.behavior_context

    def update(self, context=None, delta_ticks: int = 1):
        """Simulation manager tick hook.

        Does not run global entity loops or mutate entity states.
        """
        if context and 'world' in context:
            self.bind_world(context['world'])
        return self

    def snapshot(self) -> Dict[str, Any]:
        return {
            'initialized': self.initialized,
            'seed': self.seed,
            'season': self.get_current_season(),
            'world_age_ticks': self.get_world_age_ticks(),
        }

    def __repr__(self) -> str:
        return f"VerdantCreatureSystem(seed={self.seed}, season={self.get_current_season()}, initialized={self.initialized})"
