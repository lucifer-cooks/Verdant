"""Deterministic ecological feedback and adaptive response system for VERDANT M9."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from verdant.creatures.system import VerdantCreatureSystem
from verdant.ecology.system import VerdantEcologySystem
from verdant.ecosystem.system import VerdantEcosystemSystem
from verdant.environment.climate import VerdantClimateSystem
from verdant.environment.seed import VerdantWorldSeed
from verdant.feedback.habitat_feedback import VerdantHabitatFeedback
from verdant.feedback.signals import VerdantEcologicalSignals
from verdant.feedback.vegetation_feedback import VerdantVegetationFeedback
from verdant.feedback.water_feedback import VerdantWaterFeedback
from verdant.simulation.system import VerdantSystem
from verdant.water.system import VerdantWaterSystem


class VerdantFeedbackSystem(VerdantSystem):
    """Integrates ecological feedback across climate, water, vegetation, and creatures.

    Acts as the central closed-loop feedback layer of the VERDANT simulation.
    Operates with unidirectional update flow to strictly avoid recursive circular calculations.
    """

    MAX_EVALUATION_RADIUS = 16.0

    STATE_THRIVING = 'thriving'
    STATE_HEALTHY = 'healthy'
    STATE_STABLE = 'stable'
    STATE_STRESSED = 'stressed'
    STATE_RECOVERING = 'recovering'
    STATE_DEGRADED = 'degraded'

    def __init__(self, world_state=None, climate_system=None, water_system=None,
                 ecology_system=None, creature_system=None, ecosystem_system=None,
                 clock=None, *, name: str = 'verdant_feedback', seed: Optional[int] = None):
        super().__init__(name=name)
        self.world_state = world_state
        self.climate_system = climate_system
        self.water_system = water_system
        self.ecology_system = ecology_system
        self.creature_system = creature_system
        self.ecosystem_system = ecosystem_system
        self.clock = clock

        if seed is not None:
            self.seed = int(seed)
        elif world_state is not None and hasattr(world_state, 'metadata') and 'seed' in world_state.metadata:
            self.seed = int(world_state.metadata['seed'])
        else:
            self.seed = 0

        self.seed_source = VerdantWorldSeed(self.seed)
        self.veg_feedback = VerdantVegetationFeedback(self.seed)
        self.hab_feedback = VerdantHabitatFeedback(self.seed)
        self.water_feedback = VerdantWaterFeedback(self.seed)

        # Bounded temporal smoothing cache: {(region_key): (health, stress, response)}
        self._temporal_cache: Dict[Tuple[int, int, int], Tuple[float, float, str]] = {}

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
        if self.ecosystem_system is not None:
            self.ecosystem_system.bind_world(world)
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

    def bind_ecosystem_system(self, ecosystem_system):
        self.ecosystem_system = ecosystem_system
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

    def _resolve_ecosystem_system(self) -> VerdantEcosystemSystem:
        if self.ecosystem_system is None:
            climate = self._resolve_climate_system()
            water = self._resolve_water_system()
            ecology = self._resolve_ecology_system()
            creatures = self._resolve_creature_system()
            self.ecosystem_system = VerdantEcosystemSystem(
                world_state=self.world_state,
                climate_system=climate,
                water_system=water,
                ecology_system=ecology,
                creature_system=creatures,
                clock=self.clock,
                seed=self.seed,
            )
        return self.ecosystem_system

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

    def _sanitize_radius(self, radius: float) -> float:
        return max(1.0, min(self.MAX_EVALUATION_RADIUS, float(radius)))

    def _clamp(self, val: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, float(val)))

    def calculate_ecosystem_health(self, climate_suitability: float, moisture: float,
                                   vegetation_health: float, fertility: float,
                                   habitat_quality: float, population_pressure: float,
                                   resource_pressure: float, drought_pressure: float) -> float:
        """Calculates multi-dimensional composite ecosystem health in [0.0, 1.0]."""
        # Positive supportive capacity
        supportive = (
            0.20 * climate_suitability
            + 0.20 * moisture
            + 0.25 * vegetation_health
            + 0.15 * fertility
            + 0.20 * habitat_quality
        )
        # Adverse ecological pressures
        pressures = (
            0.35 * resource_pressure
            + 0.35 * drought_pressure
            + 0.30 * population_pressure
        )
        # Health balances supportive condition against systemic strain
        health = supportive * (1.0 - 0.65 * pressures)
        return self._clamp(health)

    def calculate_ecosystem_stability(self, health: float, moisture: float,
                                     fertility: float, stress: float) -> float:
        """Calculates ecological stability / resilience in [0.0, 1.0]."""
        resilience_factors = 0.40 * health + 0.35 * moisture + 0.25 * fertility
        stability = resilience_factors * (1.0 - 0.60 * stress)
        return self._clamp(stability)

    def classify_adaptive_response(self, health: float, stability: float,
                                  stress: float, recovery: float,
                                  prev_state: Optional[str] = None) -> str:
        """Classifies the adaptive ecological state with hysteresis stability."""
        # 1. Extreme degradation
        if health < 0.22 or (stress >= 0.75 and recovery < 0.15):
            return self.STATE_DEGRADED

        # 2. Thriving
        if health >= 0.78 and stability >= 0.70 and stress <= 0.20:
            return self.STATE_THRIVING

        # 3. Healthy
        if health >= 0.60 and stress <= 0.35:
            return self.STATE_HEALTHY

        # 4. Recovering (improving condition under low-to-moderate stress)
        if recovery >= 0.45 and health >= 0.40 and stress <= 0.50:
            return self.STATE_RECOVERING

        # 5. Stressed
        if stress >= 0.55 or health < 0.42:
            return self.STATE_STRESSED

        # 6. Stable baseline buffer
        if prev_state in (self.STATE_HEALTHY, self.STATE_STABLE, self.STATE_RECOVERING):
            return self.STATE_STABLE
        return self.STATE_STABLE

    def evaluate_ecological_signals(self, x: float, y: float, z: float, radius: float = 16.0,
                                    world=None) -> VerdantEcologicalSignals:
        """Calculates all normalized ecological feedback signals for a bounded area."""
        r = self._sanitize_radius(radius)
        w = world or self._resolve_world()
        climate = self._resolve_climate_system()
        water = self._resolve_water_system()
        ecology = self._resolve_ecology_system()
        creatures = self._resolve_creature_system()
        ecosystem = self._resolve_ecosystem_system()

        ix, iy, iz = int(x), int(y), int(z)
        env = climate.get_environment(ix, iy, iz)
        moisture = water.get_soil_moisture(ix, iy, iz)
        fertility = ecology.get_fertility(ix, iy, iz, env=env, moisture=moisture)
        base_veg_health = ecology.get_vegetation_health(ix, iy, iz, env=env, moisture=moisture, fertility=fertility)
        growth_potential = ecology.get_growth_potential(ix, iy, iz, env=env, moisture=moisture, fertility=fertility)
        base_stress = ecology.get_environmental_stress(ix, iy, iz, env=env, moisture=moisture)
        season = self.get_current_season()

        # 1. Population & Creature State
        herbivore_count = ecosystem.count_local_entities(x, y, z, radius=r, species_filter='herbivore', world=w)
        pop_sample = ecosystem.evaluate_population_sample(x, y, z, radius=r, species='herbivore', world=w)
        population_pressure = pop_sample.population_pressure
        resource_pressure = pop_sample.resource_pressure
        base_habitat = creatures.get_habitat_score('herbivore', x, y, z, world=w)

        # 2. Vegetation Feedback
        grazing_pressure = self.veg_feedback.evaluate_grazing_pressure(herbivore_count)
        veg_stress = self.veg_feedback.calculate_vegetation_stress_feedback(base_stress, grazing_pressure, moisture)
        veg_recovery = self.veg_feedback.calculate_vegetation_recovery_feedback(
            growth_potential=growth_potential,
            vegetation_health=base_veg_health,
            fertility=fertility,
            grazing_pressure=grazing_pressure,
            vegetation_stress=veg_stress,
        )

        # 3. Water & Drought Feedback
        water_stress = self.water_feedback.calculate_water_stress(
            soil_moisture=moisture,
            rainfall=env.rainfall,
            temperature=env.temperature,
            ecosystem_demand=resource_pressure,
        )
        drought_pressure = self.water_feedback.calculate_drought_pressure(
            water_stress=water_stress,
            soil_moisture=moisture,
            rainfall=env.rainfall,
            season=season,
        )

        # 4. Habitat Feedback
        habitat_pressure = self.hab_feedback.calculate_habitat_pressure(
            base_habitat_quality=base_habitat,
            population_pressure=population_pressure,
            resource_pressure=resource_pressure,
        )

        # 5. Composite Ecosystem Health & Stability
        climate_suitability = 1.0 - abs(env.temperature - 20.0) / 30.0
        climate_suitability = self._clamp(climate_suitability)
        raw_health = self.calculate_ecosystem_health(
            climate_suitability=climate_suitability,
            moisture=moisture,
            vegetation_health=base_veg_health,
            fertility=fertility,
            habitat_quality=base_habitat,
            population_pressure=population_pressure,
            resource_pressure=resource_pressure,
            drought_pressure=drought_pressure,
        )

        # 6. Temporal Smoothing & Hysteresis
        region_key = (ix // 16, iy // 16, iz // 16)
        prev_health, prev_stress, prev_state = self._temporal_cache.get(region_key, (raw_health, veg_stress, self.STATE_STABLE))
        smoothed_health = self._clamp(0.70 * prev_health + 0.30 * raw_health)
        smoothed_stress = self._clamp(0.70 * prev_stress + 0.30 * veg_stress)

        stability = self.calculate_ecosystem_stability(
            health=smoothed_health,
            moisture=moisture,
            fertility=fertility,
            stress=smoothed_stress,
        )

        adaptive_response = self.classify_adaptive_response(
            health=smoothed_health,
            stability=stability,
            stress=smoothed_stress,
            recovery=veg_recovery,
            prev_state=prev_state,
        )
        self._temporal_cache[region_key] = (smoothed_health, smoothed_stress, adaptive_response)

        return VerdantEcologicalSignals(
            x=float(x),
            y=float(y),
            z=float(z),
            radius=float(r),
            grazing_pressure=grazing_pressure,
            vegetation_stress=smoothed_stress,
            vegetation_recovery=veg_recovery,
            habitat_pressure=habitat_pressure,
            resource_pressure=resource_pressure,
            water_stress=water_stress,
            drought_pressure=drought_pressure,
            population_pressure=population_pressure,
            ecological_health=smoothed_health,
            ecosystem_stability=stability,
            adaptive_response=adaptive_response,
        )

    def update(self, context=None, delta_ticks: int = 1):
        """Simulation manager tick hook.

        Maintains update cadence without whole-world iteration.
        """
        if context and 'world' in context:
            self.bind_world(context['world'])
        return self

    def snapshot(self) -> Dict[str, Any]:
        return {
            'initialized': self.initialized,
            'seed': self.seed,
            'cached_regions': len(self._temporal_cache),
            'world_age_ticks': self.get_world_age_ticks(),
        }

    def __repr__(self) -> str:
        return f"VerdantFeedbackSystem(seed={self.seed}, regions={len(self._temporal_cache)}, initialized={self.initialized})"
