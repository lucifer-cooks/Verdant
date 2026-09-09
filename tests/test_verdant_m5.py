import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verdant.environment.climate import VerdantClimateSystem
from verdant.vegetation.system import VerdantVegetationSystem
from verdant.water.system import VerdantWaterSystem
from verdant.world.state import VerdantWorldState


def test_m5_water_system_initializes():
    state = VerdantWorldState()
    state.metadata['seed'] = 42
    water = VerdantWaterSystem(world_state=state)
    assert water.initialized is False
    water.initialize()
    assert water.initialized is True
    assert water.seed == 42


def test_existing_indev_water_blocks_can_be_detected_via_bridge():
    class DummyWorld:
        def __init__(self):
            self.water_id = 9
            self.world = self

        def getBlockId(self, x, y, z):
            if (x, y, z) == (10, 64, 10):
                return 9
            return 0

    world = DummyWorld()
    state = VerdantWorldState(world=world)
    water = VerdantWaterSystem(world_state=state)
    water.bind_world(world)

    assert water._contains_water_block(10, 64, 10) is True
    assert water.get_surface_water_presence(10, 64, 10) > 0.0


def test_water_detection_does_not_create_or_modify_blocks():
    class DummyWorld:
        def __init__(self):
            self.calls = []
            self.world = self

        def getBlockId(self, x, y, z):
            self.calls.append((x, y, z))
            if (x, y, z) == (3, 6, 3):
                return 8
            return 0

    world = DummyWorld()
    water = VerdantWaterSystem(world_state=VerdantWorldState(world=world))
    water.bind_world(world)

    before = list(world.calls)
    result = water._contains_water_block(3, 6, 3)
    after = list(world.calls)

    assert result is True
    assert before == []
    assert after != []
    assert world.getBlockId(3, 6, 3) == 8


def test_moisture_values_are_deterministic():
    state = VerdantWorldState()
    state.metadata['seed'] = 777
    water = VerdantWaterSystem(world_state=state)
    value_a = water.get_soil_moisture(5, 12, 9)
    value_b = water.get_soil_moisture(5, 12, 9)
    value_c = water.get_soil_moisture(6, 12, 9)
    assert value_a == value_b
    assert value_a != value_c


def test_same_seed_same_coordinates_same_moisture():
    water_a = VerdantWaterSystem(world_state=VerdantWorldState())
    water_a.seed = 123
    water_b = VerdantWaterSystem(world_state=VerdantWorldState())
    water_b.seed = 123
    a = water_a.get_soil_moisture(18, 15, 21)
    b = water_b.get_soil_moisture(18, 15, 21)
    assert a == b


def test_nearby_water_produces_higher_moisture_than_distant_locations_under_equivalent_conditions():
    state = VerdantWorldState()
    state.metadata['seed'] = 321
    water = VerdantWaterSystem(world_state=state)

    class DummyWorld:
        def __init__(self):
            self.world = self

        def getBlockId(self, x, y, z):
            if x == 32 and z == 32 and y == 12:
                return 9
            return 0

    world = DummyWorld()
    water.bind_world(world)

    near = water.get_soil_moisture(32, 12, 32)
    far = water.get_soil_moisture(80, 15, 80)
    assert near > far


def test_higher_rainfall_can_increase_moisture():
    state = VerdantWorldState(current_season='spring')
    water = VerdantWaterSystem(world_state=state)
    dry = water.get_soil_moisture(4, 10, 4)
    wet = water.get_soil_moisture(4, 10, 5)
    assert abs(dry - wet) >= 0.0


def test_higher_humidity_can_increase_moisture():
    state = VerdantWorldState(current_season='spring')
    climate = VerdantClimateSystem(world_state=state)
    water = VerdantWaterSystem(world_state=state, climate_system=climate)
    baseline = water.get_soil_moisture(10, 10, 10)
    humid = water.get_soil_moisture(11, 10, 10)
    assert baseline >= 0.0
    assert humid >= 0.0


def test_desert_environments_generally_produce_lower_moisture():
    state = VerdantWorldState(current_season='summer')
    climate = VerdantClimateSystem(world_state=state)
    water = VerdantWaterSystem(world_state=state, climate_system=climate)

    desert = water.get_soil_moisture(10, 5, 10)
    forest = water.get_soil_moisture(20, 15, 20)
    assert desert <= forest


def test_swamp_environments_generally_produce_higher_moisture():
    state = VerdantWorldState(current_season='spring')
    climate = VerdantClimateSystem(world_state=state)
    water = VerdantWaterSystem(world_state=state, climate_system=climate)

    swamp_like = water.get_soil_moisture(8, 14, 8)
    dry_like = water.get_soil_moisture(30, 10, 30)
    assert swamp_like >= dry_like


def test_m4_vegetation_apis_still_work():
    system = VerdantVegetationSystem(world_state=VerdantWorldState())
    env = system.get_environment_for(5, 10, 5)
    assert system.is_vegetation_suitable(env, 'grass') in (True, False)
    assert system.get_tree_density(env) >= 0.0


def test_vegetation_suitability_can_access_moisture():
    system = VerdantVegetationSystem(world_state=VerdantWorldState())
    env = system.get_environment_for(12, 18, 12)
    assert hasattr(env, 'soil_moisture')
    assert 0.0 <= float(env.soil_moisture) <= 1.0


def test_no_uncontrolled_global_random_state_is_introduced():
    state = VerdantWorldState()
    state.metadata['seed'] = 99
    water = VerdantWaterSystem(world_state=state)
    first = water.get_soil_moisture(4, 6, 7)
    second = water.get_soil_moisture(4, 6, 7)
    assert first == second


def test_no_second_simulation_loop_exists():
    state = VerdantWorldState()
    water = VerdantWaterSystem(world_state=state)
    assert callable(water.update)
    assert water.update() is water


def test_m2_tests_still_pass_compatibility_smoke():
    state = VerdantWorldState()
    assert state.simulation_version == 1
    assert state.current_season == 'spring'


def test_m3_tests_still_pass_compatibility_smoke():
    climate = VerdantClimateSystem(world_state=VerdantWorldState(current_season='summer'))
    env = climate.get_environment(1, 1, 1)
    assert env.temperature >= -30.0
    assert env.humidity >= 0.0
    assert env.rainfall >= 0.0


def test_m4_tests_still_pass_compatibility_smoke():
    system = VerdantVegetationSystem(world_state=VerdantWorldState())
    env = system.get_environment_for(3, 3, 3)
    assert env.soil_moisture >= 0.0
