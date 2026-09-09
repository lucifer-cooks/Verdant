"""VERDANT dynamic moisture and water environmental layer."""

from __future__ import annotations

from typing import Any, Dict, Optional

from verdant.environment.biome import VerdantBiomeResolver
from verdant.environment.seed import VerdantWorldSeed
from verdant.simulation.system import VerdantSystem
from verdant.water.moisture import VerdantMoistureState


class VerdantWaterSystem(VerdantSystem):
    """Deterministic, localized moisture model keyed to legacy world state.

    This does not replace the existing Indev liquid system. It simply observes the
    current world and exposes a read-only environmental water model for future
    ecosystem and climate features.
    """

    WATER_BLOCK_IDS = {8, 9, 10, 11, 52, 53}
    WATER_SEARCH_RADIUS = 8

    def __init__(self, world_state=None, query_boundary=None, climate_system=None, *, name='verdant_water', seed: Optional[int] = None):
        super().__init__(name=name)
        self.world_state = world_state
        self.query_boundary = query_boundary
        self.climate_system = climate_system
        self.seed = int(seed if seed is not None else (self.world_state.metadata.get('seed', 0) if self.world_state and hasattr(self.world_state, 'metadata') else 0))
        self.seed_source = VerdantWorldSeed(self.seed)
        self.biome_resolver = VerdantBiomeResolver()

    def initialize(self, context=None):
        if context and 'world' in context:
            self.bind_world(context['world'])
        if self.world_state is not None and hasattr(self.world_state, 'metadata'):
            self.seed = int(self.world_state.metadata.get('seed', self.seed))
        self.seed_source = VerdantWorldSeed(self.seed)
        self.initialized = True
        return self

    def bind_world(self, world):
        if self.world_state is not None:
            self.world_state.bind_world(world)
        if self.query_boundary is not None:
            self.query_boundary.bind_world(world)
        return self

    def bind_climate_system(self, climate_system):
        self.climate_system = climate_system
        if self.query_boundary is not None:
            self.query_boundary.bind_climate_system(climate_system)
        return self

    def _resolve_world(self):
        if self.query_boundary is not None and getattr(self.query_boundary, 'world', None) is not None:
            return self.query_boundary.world
        if self.world_state is not None and getattr(self.world_state, 'world', None) is not None:
            return self.world_state.world
        return None

    def _legacy_block_id(self, x: int, y: int, z: int):
        world = self._resolve_world()
        if world is None:
            return 0
        try:
            return int(world.getBlockId(int(x), int(y), int(z)))
        except Exception:
            return 0

    def _contains_water_block(self, x: int, y: int, z: int):
        world = self._resolve_world()
        if world is None:
            return False
        try:
            block_id = self._legacy_block_id(x, y, z)
            if block_id in self.WATER_BLOCK_IDS:
                return True
            if hasattr(world, 'getBlockMaterial'):
                material = world.getBlockMaterial(int(x), int(y), int(z))
                return material is not None and getattr(material, 'name', '') == 'water'
            return False
        except Exception:
            return False

    def _get_environment(self, x: int, y: int, z: int):
        if self.query_boundary is not None:
            try:
                return self.query_boundary.get_environment(x, y, z)
            except Exception:
                pass
        if self.climate_system is not None:
            try:
                env = self.climate_system.get_environment(x, y, z)
                return {
                    'temperature': env.temperature,
                    'humidity': env.humidity,
                    'rainfall': env.rainfall,
                    'soil_moisture': env.soil_moisture,
                    'elevation': env.elevation,
                    'biome': env.biome_name,
                    'sunlight': env.sunlight,
                    'water_proximity': env.water_proximity,
                }
            except Exception:
                pass
        return {
            'temperature': 20.0,
            'humidity': 0.5,
            'rainfall': 0.5,
            'soil_moisture': 0.5,
            'elevation': max(0.0, abs(x) + abs(z)) * 0.1,
            'biome': 'Plains',
            'sunlight': 0.5,
            'water_proximity': 0.0,
        }

    def _clamp(self, value: float, minimum: float = 0.0, maximum: float = 1.0):
        return max(minimum, min(maximum, float(value)))

    def get_surface_water_presence(self, x: int, y: int, z: int):
        world = self._resolve_world()
        if world is None:
            return 0.0

        radius = 2
        hits = 0.0
        total = 0.0
        for dx in range(-radius, radius + 1):
            for dy in range(-2, 3):
                for dz in range(-radius, radius + 1):
                    total += 1.0
                    if self._contains_water_block(x + dx, y + dy, z + dz):
                        hits += 1.0
        if total <= 0.0:
            return 0.0
        return self._clamp(hits / total)

    def get_water_proximity(self, x: int, y: int, z: int):
        world = self._resolve_world()
        if world is None:
            return 0.0

        radius = self.WATER_SEARCH_RADIUS
        best = 1.0
        found = False
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                for dz in range(-radius, radius + 1):
                    if self._contains_water_block(x + dx, y + dy, z + dz):
                        dist = (dx * dx + dy * dy + dz * dz) ** 0.5
                        if dist <= 0.0:
                            return 1.0
                        best = min(best, max(0.0, 1.0 - (dist / max(1.0, radius))))
                        found = True
        if not found:
            return 0.0
        return self._clamp(best)

    def get_water_influence(self, x: int, y: int, z: int):
        surface = self.get_surface_water_presence(x, y, z)
        proximity = self.get_water_proximity(x, y, z)
        return self._clamp(0.65 * surface + 0.35 * proximity)

    def is_near_water(self, x: int, y: int, z: int):
        return self.get_water_proximity(x, y, z) > 0.15 or self.get_surface_water_presence(x, y, z) > 0.0

    def get_soil_moisture(self, x: int, y: int, z: int):
        env = self._get_environment(x, y, z)
        rainfall = float(env.get('rainfall', 0.5))
        humidity = float(env.get('humidity', 0.5))
        temperature = float(env.get('temperature', 20.0))
        elevation = float(env.get('elevation', 0.0))
        biome_name = str(env.get('biome', 'Plains'))
        surface = self.get_surface_water_presence(x, y, z)
        proximity = self.get_water_proximity(x, y, z)
        water_proximity = float(env.get('water_proximity', proximity))

        moisture = 0.12 + 0.25 * rainfall + 0.35 * humidity + 0.20 * proximity + 0.20 * water_proximity + 0.20 * surface
        if 18.0 <= temperature <= 28.0 and humidity >= 0.5 and rainfall >= 0.4:
            moisture += 0.15
        if temperature > 28.0 and humidity <= 0.6:
            moisture -= 0.18
        if temperature <= 8.0 and humidity <= 0.8:
            moisture -= 0.10

        biome_key = biome_name.lower().replace(' ', '').replace('/', '')
        if 'desert' in biome_key:
            moisture -= 0.35
        elif 'swamp' in biome_key:
            moisture += 0.30
        elif 'forest' in biome_key:
            moisture += 0.10
        elif 'snow' in biome_key or 'tundra' in biome_key:
            moisture -= 0.20
        elif 'ocean' in biome_key:
            moisture = max(moisture, 0.95)

        if elevation > 30.0:
            moisture -= min(0.25, (elevation - 30.0) / 250.0)
        if temperature > 30.0:
            moisture -= min(0.25, (temperature - 30.0) / 80.0)
        moisture += (self.seed_source.value(x, y, z) - 0.5) * 0.08
        moisture = self._clamp(moisture)

        if surface >= 0.9:
            return 1.0
        return moisture

    def get_moisture_state(self, x: int, y: int, z: int):
        env = self._get_environment(x, y, z)
        rainfall = float(env.get('rainfall', 0.5))
        humidity = float(env.get('humidity', 0.5))
        temperature = float(env.get('temperature', 20.0))
        elevation = float(env.get('elevation', 0.0))
        surface = self.get_surface_water_presence(x, y, z)
        proximity = self.get_water_proximity(x, y, z)
        influence = self.get_water_influence(x, y, z)
        soil_moisture = self.get_soil_moisture(x, y, z)
        evaporation = self._clamp((temperature / 45.0) * 0.8 + (1.0 - humidity) * 0.4 + (1.0 - rainfall) * 0.2)
        accessibility = self._clamp((0.4 * soil_moisture) + (0.6 * influence))
        nearby_water = self.is_near_water(x, y, z)
        biome_name = str(env.get('biome', 'Plains'))

        return VerdantMoistureState(
            x=x,
            y=y,
            z=z,
            soil_moisture=soil_moisture,
            surface_water_presence=surface,
            water_proximity=proximity,
            water_influence=influence,
            evaporation_potential=evaporation,
            water_accessibility=accessibility,
            nearby_water=nearby_water,
            biome_name=biome_name,
            rainfall=rainfall,
            humidity=humidity,
            temperature=temperature,
            elevation=elevation,
        )

    def get_soil_moisture_for(self, x: int, y: int, z: int):
        return self.get_soil_moisture(x, y, z)

    def update(self, context=None, delta_ticks: int = 1):
        return self

    def snapshot(self):
        return {
            'initialized': self.initialized,
            'seed': self.seed,
            'water_search_radius': self.WATER_SEARCH_RADIUS,
        }

    def __repr__(self):
        return f"VerdantWaterSystem(seed={self.seed}, initialized={self.initialized})"
