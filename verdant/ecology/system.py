"""Deterministic ecology and vegetation condition simulation system for VERDANT M6."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from verdant.ecology.vegetation_state import VerdantVegetationState
from verdant.environment.biome import VerdantBiomeResolver
from verdant.environment.climate import VerdantClimateSystem
from verdant.environment.seed import VerdantWorldSeed
from verdant.simulation.system import VerdantSystem
from verdant.vegetation.rules import VerdantVegetationRuleSet
from verdant.water.system import VerdantWaterSystem


class VerdantEcologySystem(VerdantSystem):
    """Deterministic, temporal vegetation condition and ecological health layer.

    Translates time, climate, and dynamic moisture into localized vegetation health,
    fertility, growth potential, and environmental stress. Operates purely through
    on-demand queries without requiring full world scans or per-block persistent allocations.
    """

    SEASON_PROFILES: Dict[str, Dict[str, float]] = {
        'spring': {
            'growth_modifier': 0.20,
            'moisture_response': 1.20,
            'temperature_optimum': 18.0,
            'base_stress': 0.05,
            'cold_stress_factor': 0.20,
            'heat_stress_factor': 0.10,
        },
        'summer': {
            'growth_modifier': 0.25,
            'moisture_response': 1.30,
            'temperature_optimum': 24.0,
            'base_stress': 0.10,
            'cold_stress_factor': 0.05,
            'heat_stress_factor': 0.30,
        },
        'autumn': {
            'growth_modifier': -0.05,
            'moisture_response': 0.90,
            'temperature_optimum': 14.0,
            'base_stress': 0.10,
            'cold_stress_factor': 0.25,
            'heat_stress_factor': 0.10,
        },
        'winter': {
            'growth_modifier': -0.35,
            'moisture_response': 0.60,
            'temperature_optimum': 8.0,
            'base_stress': 0.25,
            'cold_stress_factor': 0.45,
            'heat_stress_factor': 0.0,
        },
    }

    TICKS_PER_DAY = 24000

    def __init__(self, world_state=None, climate_system=None, water_system=None, clock=None,
                 *, name: str = 'verdant_ecology', seed: Optional[int] = None):
        super().__init__(name=name)
        self.world_state = world_state
        self.climate_system = climate_system
        self.water_system = water_system
        self.clock = clock

        if seed is not None:
            self.seed = int(seed)
        elif world_state is not None and hasattr(world_state, 'metadata') and 'seed' in world_state.metadata:
            self.seed = int(world_state.metadata['seed'])
        else:
            self.seed = 0

        self.seed_source = VerdantWorldSeed(self.seed)
        self.biome_resolver = VerdantBiomeResolver()
        self.rules = VerdantVegetationRuleSet()

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
        return self

    def bind_climate_system(self, climate_system):
        self.climate_system = climate_system
        return self

    def bind_water_system(self, water_system):
        self.water_system = water_system
        return self

    def bind_clock(self, clock):
        self.clock = clock
        return self

    def _clamp(self, value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(maximum, float(value)))

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

    def get_season_progress(self) -> float:
        ticks = self.get_world_age_ticks()
        return (ticks % self.TICKS_PER_DAY) / float(self.TICKS_PER_DAY)

    def get_season_modifier(self, x: Optional[int] = None, y: Optional[int] = None, z: Optional[int] = None) -> float:
        season = self.get_current_season()
        profile = self.SEASON_PROFILES.get(season, self.SEASON_PROFILES['spring'])
        base_mod = profile['growth_modifier']
        if x is None or y is None or z is None:
            return base_mod

        # Incorporate smooth temporal progression within season
        progress = self.get_season_progress()
        variation = (progress - 0.5) * 0.05
        local_jitter = (self.seed_source.noise(x + 51, y + 23, z + 77) * 0.02)
        return base_mod + variation + local_jitter

    def _calculate_temperature_suitability(self, temperature: float, season: str) -> float:
        profile = self.SEASON_PROFILES.get(season, self.SEASON_PROFILES['spring'])
        optimum = profile['temperature_optimum']
        diff = abs(temperature - optimum)
        if diff <= 4.0:
            return 1.0 - (diff / 20.0)
        elif diff <= 15.0:
            return max(0.2, 0.8 - ((diff - 4.0) / 20.0))
        else:
            return max(0.0, 0.25 - ((diff - 15.0) / 25.0))

    def _resolve_moisture(self, x: int, y: int, z: int, env=None, moisture=None) -> float:
        if moisture is not None:
            return float(moisture)
        if self.water_system is not None:
            return float(self.water_system.get_soil_moisture(x, y, z))
        if env is not None and hasattr(env, 'soil_moisture') and env.soil_moisture is not None:
            return float(env.soil_moisture)
        water = self._resolve_water_system()
        return float(water.get_soil_moisture(x, y, z))

    def get_fertility(self, x: int, y: int, z: int, env=None, moisture=None) -> float:
        if env is None:
            climate = self._resolve_climate_system()
            env = climate.get_environment(x, y, z)
        moisture = self._resolve_moisture(x, y, z, env=env, moisture=moisture)

        temperature = env.temperature
        rainfall = env.rainfall
        humidity = env.humidity
        elevation = env.elevation
        biome_name = env.biome_name

        # Base fertility from moisture and organic inputs
        base = 0.25 + 0.35 * moisture + 0.20 * rainfall + 0.15 * humidity

        # Temperature optimum range for biological fertility (12C to 28C)
        if 12.0 <= temperature <= 28.0:
            base += 0.12
        elif temperature < 4.0:
            base -= min(0.25, (4.0 - temperature) * 0.015)
        elif temperature > 34.0:
            base -= min(0.25, (temperature - 34.0) * 0.02)

        # Biome adjustments
        biome_key = biome_name.lower().replace(' ', '').replace('/', '')
        if 'forest' in biome_key:
            base += 0.15
        elif 'plains' in biome_key:
            base += 0.12
        elif 'swamp' in biome_key:
            base += 0.08
        elif 'mountains' in biome_key:
            base -= 0.10
        elif 'snow' in biome_key or 'tundra' in biome_key:
            base -= 0.20
        elif 'desert' in biome_key:
            base -= 0.30

        # Elevation penalty
        if elevation > 35.0:
            base -= min(0.20, (elevation - 35.0) * 0.005)

        # Deterministic noise jitter
        jitter = (self.seed_source.noise(x + 37, y + 17, z + 83) * 0.04)
        return self._clamp(base + jitter)

    def get_environmental_stress(self, x: int, y: int, z: int, env=None, moisture=None) -> float:
        if env is None:
            climate = self._resolve_climate_system()
            env = climate.get_environment(x, y, z)
        moisture = self._resolve_moisture(x, y, z, env=env, moisture=moisture)

        season = self.get_current_season()
        profile = self.SEASON_PROFILES.get(season, self.SEASON_PROFILES['spring'])

        temperature = env.temperature
        sunlight = env.sunlight

        stress = profile['base_stress']

        # Drought stress: when moisture is deficient
        if moisture < 0.25:
            drought_severity = (0.25 - moisture) / 0.25
            stress += drought_severity * 0.45

        # Cold stress: when temperature is below freezing or very low
        if temperature < 4.0:
            cold_severity = max(0.0, min(1.0, (4.0 - temperature) / 25.0))
            stress += cold_severity * (0.35 + profile['cold_stress_factor'])

        # Heat stress: high temperatures combine with low moisture
        if temperature > 30.0:
            heat_severity = max(0.0, min(1.0, (temperature - 30.0) / 15.0))
            stress += heat_severity * (0.25 + profile['heat_stress_factor'] * (1.0 - moisture))

        # Extreme darkness or light starvation
        if sunlight < 0.15:
            stress += (0.15 - sunlight) * 0.30

        return self._clamp(stress)

    def get_vegetation_health(self, x: int, y: int, z: int, env=None, moisture=None, fertility=None, stress=None) -> float:
        if env is None:
            climate = self._resolve_climate_system()
            env = climate.get_environment(x, y, z)
        moisture = self._resolve_moisture(x, y, z, env=env, moisture=moisture)

        season = self.get_current_season()
        if fertility is None:
            fertility = self.get_fertility(x, y, z, env=env, moisture=moisture)
        if stress is None:
            stress = self.get_environmental_stress(x, y, z, env=env, moisture=moisture)

        temp_suitability = self._calculate_temperature_suitability(env.temperature, season)
        sunlight = env.sunlight

        # Favorable conditions build health
        health_potential = (
            0.30 * temp_suitability
            + 0.30 * moisture
            + 0.20 * fertility
            + 0.20 * sunlight
        )

        # Environmental stress directly damages vegetation health
        health = health_potential * (1.0 - 0.70 * stress)
        return self._clamp(health)

    def get_growth_potential(self, x: int, y: int, z: int, env=None, moisture=None, health=None, stress=None, fertility=None) -> float:
        if env is None:
            climate = self._resolve_climate_system()
            env = climate.get_environment(x, y, z)
        moisture = self._resolve_moisture(x, y, z, env=env, moisture=moisture)

        season = self.get_current_season()
        profile = self.SEASON_PROFILES.get(season, self.SEASON_PROFILES['spring'])

        if stress is None:
            stress = self.get_environmental_stress(x, y, z, env=env, moisture=moisture)
        if fertility is None:
            fertility = self.get_fertility(x, y, z, env=env, moisture=moisture)
        if health is None:
            health = self.get_vegetation_health(x, y, z, env=env, moisture=moisture, fertility=fertility, stress=stress)

        temp_suitability = self._calculate_temperature_suitability(env.temperature, season)

        # M4 rule baseline for this biome
        rule = self.rules.get_rules(env.biome_name)
        base_density = (rule.tree_density + rule.grass_density + rule.flower_density) / 3.0

        # Seasonal growth factor
        season_growth = profile['growth_modifier']
        moisture_factor = moisture * profile['moisture_response']

        # Composite growth formula
        growth = (
            0.25 * base_density
            + 0.25 * health
            + 0.20 * moisture_factor
            + 0.15 * fertility
            + 0.15 * temp_suitability
            + season_growth
        ) - (0.50 * stress)

        # Extreme cold strongly suppresses growth
        if env.temperature < -2.0:
            growth *= max(0.05, 1.0 - abs(env.temperature) * 0.03)

        # Severe dryness suppresses growth
        if moisture < 0.15:
            growth *= max(0.05, moisture / 0.15)

        return self._clamp(growth)

    def _detect_events(self, growth_potential: float, stress: float, moisture: float, temperature: float) -> Tuple[str, ...]:
        events: List[str] = []
        if growth_potential >= 0.60 and stress <= 0.25:
            events.append('growth_favorable')
        if moisture < 0.20 and stress >= 0.40:
            events.append('drought_stress')
        if temperature < 2.0 and stress >= 0.35:
            events.append('cold_stress')
        if moisture >= 0.65 and stress < 0.30:
            events.append('moisture_recovery')
        return tuple(events)

    def is_growth_favorable(self, x: int, y: int, z: int) -> bool:
        climate = self._resolve_climate_system()
        env = climate.get_environment(x, y, z)
        moisture = self._resolve_moisture(x, y, z, env=env)
        stress = self.get_environmental_stress(x, y, z, env=env, moisture=moisture)
        growth = self.get_growth_potential(x, y, z, env=env, moisture=moisture, stress=stress)
        return growth >= 0.50 and stress <= 0.35

    def get_vegetation_state(self, x: int, y: int, z: int) -> VerdantVegetationState:
        climate = self._resolve_climate_system()
        season = self.get_current_season()
        season_progress = self.get_season_progress()

        env = climate.get_environment(x, y, z)
        moisture = self._resolve_moisture(x, y, z, env=env)

        fertility = self.get_fertility(x, y, z, env=env, moisture=moisture)
        stress = self.get_environmental_stress(x, y, z, env=env, moisture=moisture)
        health = self.get_vegetation_health(x, y, z, env=env, moisture=moisture, fertility=fertility, stress=stress)
        growth_potential = self.get_growth_potential(x, y, z, env=env, moisture=moisture, health=health, stress=stress, fertility=fertility)
        temp_suitability = self._calculate_temperature_suitability(env.temperature, season)
        events = self._detect_events(growth_potential, stress, moisture, env.temperature)

        return VerdantVegetationState(
            x=x,
            y=y,
            z=z,
            growth_potential=growth_potential,
            moisture=moisture,
            temperature_suitability=temp_suitability,
            sunlight=env.sunlight,
            fertility=fertility,
            stress=stress,
            health=health,
            season=season,
            season_progress=season_progress,
            biome_name=env.biome_name,
            events=events,
        )

    def update(self, context=None, delta_ticks: int = 1):
        """Simulation tick hook invoked via VerdantSimulationManager.

        Does not run whole-world scans or spawn entities. Simply maintains
        synchronization with the simulation clock and active world state.
        """
        if context and 'world' in context:
            self.bind_world(context['world'])
        return self

    def snapshot(self) -> Dict[str, Any]:
        return {
            'initialized': self.initialized,
            'seed': self.seed,
            'current_season': self.get_current_season(),
            'season_progress': self.get_season_progress(),
            'world_age_ticks': self.get_world_age_ticks(),
        }

    def __repr__(self) -> str:
        return f"VerdantEcologySystem(seed={self.seed}, season={self.get_current_season()}, initialized={self.initialized})"
