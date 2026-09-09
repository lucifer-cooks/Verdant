import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verdant.environment.biome import VerdantBiomeDefinition, VerdantBiomeResolver
from verdant.environment.climate import VerdantClimateSystem
from verdant.environment.seed import VerdantWorldSeed
from verdant.world.clock import VerdantSimulationClock
from verdant.world.queries import VerdantWorldQueryBoundary
from verdant.world.state import VerdantWorldState


def test_climate_is_deterministic():
    state = VerdantWorldState(world_age_ticks=100, current_season='summer')
    state.metadata['seed'] = 12345
    climate = VerdantClimateSystem(world_state=state)

    env_a = climate.get_environment(10, 20, 30)
    env_b = climate.get_environment(10, 20, 30)
    env_c = climate.get_environment(11, 20, 30)

    assert env_a.temperature == env_b.temperature
    assert env_a.humidity == env_b.humidity
    assert env_a.rainfall == env_b.rainfall
    assert env_a != env_c


def test_seasonal_modifiers_work():
    state = VerdantWorldState(current_season='winter')
    state.metadata['seed'] = 7
    summer_state = VerdantWorldState(current_season='summer')
    summer_state.metadata['seed'] = 7

    climate_winter = VerdantClimateSystem(world_state=state)
    climate_summer = VerdantClimateSystem(world_state=summer_state)

    winter_env = climate_winter.get_environment(8, 12, 5)
    summer_env = climate_summer.get_environment(8, 12, 5)

    assert winter_env.temperature < summer_env.temperature
    assert winter_env.rainfall <= summer_env.rainfall + 0.01


def test_biome_resolver_returns_valid_biome():
    state = VerdantWorldState(current_season='spring')
    state.metadata['seed'] = 99
    climate = VerdantClimateSystem(world_state=state)
    resolver = VerdantBiomeResolver()

    env = climate.get_environment(15, 17, 9)
    biome = resolver.resolve(env)

    assert isinstance(biome, VerdantBiomeDefinition)
    assert biome.name
    assert biome.name in resolver.biome_index


def test_world_elevation_comes_through_query_boundary():
    world = type('DummyWorld', (), {'getGroundLevel': lambda self: 24, 'getBlockId': lambda self, x, y, z: 0})()
    query = VerdantWorldQueryBoundary(world)
    query.bind_climate_system(VerdantClimateSystem(world_state=VerdantWorldState(current_season='autumn')))

    elevation = query.get_elevation(5, 10, 7)
    env = query.get_environment(5, 10, 7)

    assert elevation >= 0
    assert env['elevation'] == elevation


def test_environment_queries_are_consistent():
    query = VerdantWorldQueryBoundary()
    query.bind_climate_system(VerdantClimateSystem(world_state=VerdantWorldState(current_season='spring')))

    env = query.get_environment(2, 3, 4)
    assert env['temperature'] == query.get_temperature(2, 3, 4)
    assert env['humidity'] == query.get_humidity(2, 3, 4)
    assert env['rainfall'] == query.get_rainfall(2, 3, 4)
    assert env['biome'] == query.get_biome(2, 3, 4)


def test_seed_is_deterministic_and_uses_no_global_randomness():
    seed_a = VerdantWorldSeed(123)
    seed_b = VerdantWorldSeed(123)

    assert seed_a.noise(4, 5, 6) == seed_b.noise(4, 5, 6)
    assert seed_a.noise(8, 2, 1) != seed_a.noise(8, 2, 2)


def test_clock_and_climate_stay_consistent():
    state = VerdantWorldState(current_season='spring')
    state.metadata['seed'] = 50
    clock = VerdantSimulationClock(state, simulation_speed=2)
    clock.advance(3)

    climate = VerdantClimateSystem(world_state=state)
    env = climate.get_environment(0, 0, 0)

    assert env.season == 'summer'
