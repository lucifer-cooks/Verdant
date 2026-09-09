import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verdant.ecology import (
    VerdantEcologySystem,
    VerdantVegetationState,
    get_current_season,
    get_environmental_stress,
    get_fertility,
    get_growth_potential,
    get_season_modifier,
    get_season_progress,
    get_vegetation_health,
    get_vegetation_state,
    is_growth_favorable,
)
from verdant.environment.climate import VerdantClimateSystem
from verdant.simulation.manager import VerdantSimulationManager
from verdant.vegetation.rules import VerdantVegetationRuleSet
from verdant.vegetation.system import VerdantVegetationSystem
from verdant.water.system import VerdantWaterSystem
from verdant.world.clock import VerdantSimulationClock
from verdant.world.state import VerdantWorldState


# 1. M6 ecology system initializes.
def test_m6_ecology_system_initializes():
    state = VerdantWorldState()
    state.metadata['seed'] = 42
    system = VerdantEcologySystem(world_state=state)
    assert system.initialized is False
    system.initialize()
    assert system.initialized is True
    assert system.seed == 42


# 2. M6 registers correctly with the existing simulation architecture.
def test_m6_registers_correctly_with_simulation_architecture():
    manager = VerdantSimulationManager()
    clock = VerdantSimulationClock()
    ecology = VerdantEcologySystem(clock=clock)

    assert manager.register(clock) is True
    assert manager.register(ecology) is True
    assert manager.register(ecology) is False  # Duplicate prevented

    manager.initialize()
    manager.update(delta_ticks=10)
    assert clock.elapsed_ticks == 10
    assert ecology.get_world_age_ticks() == 10


# 3. Same seed + same coordinate + same world age produces the same result.
def test_same_seed_coordinate_world_age_produces_identical_result():
    state_a = VerdantWorldState(world_age_ticks=12000)
    state_a.metadata['seed'] = 777
    state_b = VerdantWorldState(world_age_ticks=12000)
    state_b.metadata['seed'] = 777

    eco_a = VerdantEcologySystem(world_state=state_a)
    eco_b = VerdantEcologySystem(world_state=state_b)

    res_a = eco_a.get_vegetation_state(15, 20, 25)
    res_b = eco_b.get_vegetation_state(15, 20, 25)

    assert res_a == res_b
    assert res_a.growth_potential == res_b.growth_potential
    assert res_a.health == res_b.health
    assert res_a.stress == res_b.stress
    assert res_a.fertility == res_b.fertility


# 4. Different world ages can produce different seasonal conditions.
def test_different_world_ages_produce_different_seasonal_conditions():
    clock = VerdantSimulationClock()
    state = VerdantWorldState()
    clock.set_world_state(state)
    ecology = VerdantEcologySystem(world_state=state, clock=clock, seed=123)

    # Spring (day 0)
    clock.advance(0)
    spring_season = ecology.get_current_season()
    spring_state = ecology.get_vegetation_state(10, 15, 10)

    # Summer (day 1, ticks = 24000)
    clock.advance(24000)
    summer_season = ecology.get_current_season()
    summer_state = ecology.get_vegetation_state(10, 15, 10)

    # Winter (day 3, ticks = 72000 total)
    clock.advance(48000)
    winter_season = ecology.get_current_season()
    winter_state = ecology.get_vegetation_state(10, 15, 10)

    assert spring_season == 'spring'
    assert summer_season == 'summer'
    assert winter_season == 'winter'
    assert spring_state.season != winter_state.season
    assert spring_state.growth_potential != winter_state.growth_potential


# 5. Season progression is deterministic.
def test_season_progression_is_deterministic():
    clock_a = VerdantSimulationClock()
    clock_b = VerdantSimulationClock()

    clock_a.advance(6000)
    clock_b.advance(6000)
    prog_a = clock_a.get_season_progress()
    prog_b = clock_b.get_season_progress()

    assert prog_a == prog_b
    assert prog_a == 0.25

    clock_a.advance(18000)
    assert clock_a.get_current_season() == 'summer'
    assert clock_a.get_season_progress() == 0.0


# 6. Spring has stronger growth potential than winter under equivalent conditions.
def test_spring_has_stronger_growth_potential_than_winter():
    state_spring = VerdantWorldState(current_season='spring', world_age_ticks=5000)
    state_spring.metadata['seed'] = 101
    eco_spring = VerdantEcologySystem(world_state=state_spring, seed=101)

    state_winter = VerdantWorldState(current_season='winter', world_age_ticks=77000)
    state_winter.metadata['seed'] = 101
    eco_winter = VerdantEcologySystem(world_state=state_winter, seed=101)

    # Test across multiple coordinates
    for coords in [(5, 10, 5), (20, 15, 20), (30, 25, 30)]:
        spring_growth = eco_spring.get_growth_potential(*coords)
        winter_growth = eco_winter.get_growth_potential(*coords)
        assert spring_growth > winter_growth


# 7. Suitable moisture improves vegetation growth potential.
def test_suitable_moisture_improves_vegetation_growth_potential():
    class DummyWaterDry(VerdantWaterSystem):
        def get_soil_moisture(self, x, y, z):
            return 0.05

    class DummyWaterMoist(VerdantWaterSystem):
        def get_soil_moisture(self, x, y, z):
            return 0.70

    state = VerdantWorldState(current_season='spring')
    state.metadata['seed'] = 202

    eco_dry = VerdantEcologySystem(world_state=state, water_system=DummyWaterDry(), seed=202)
    eco_moist = VerdantEcologySystem(world_state=state, water_system=DummyWaterMoist(), seed=202)

    dry_growth = eco_dry.get_growth_potential(10, 10, 10)
    moist_growth = eco_moist.get_growth_potential(10, 10, 10)

    assert moist_growth > dry_growth


# 8. Severe dryness increases environmental stress.
def test_severe_dryness_increases_environmental_stress():
    class DummyWaterArid(VerdantWaterSystem):
        def get_soil_moisture(self, x, y, z):
            return 0.02

    class DummyWaterModerate(VerdantWaterSystem):
        def get_soil_moisture(self, x, y, z):
            return 0.60

    state = VerdantWorldState(current_season='summer')
    state.metadata['seed'] = 303

    eco_arid = VerdantEcologySystem(world_state=state, water_system=DummyWaterArid(), seed=303)
    eco_moderate = VerdantEcologySystem(world_state=state, water_system=DummyWaterModerate(), seed=303)

    arid_stress = eco_arid.get_environmental_stress(12, 12, 12)
    moderate_stress = eco_moderate.get_environmental_stress(12, 12, 12)

    assert arid_stress > moderate_stress


# 9. Extreme cold reduces growth potential.
def test_extreme_cold_reduces_growth_potential():
    class DummyClimateCold:
        def get_environment(self, x, y, z):
            sample = type('Env', (), {
                'temperature': -20.0,
                'humidity': 0.3,
                'rainfall': 0.1,
                'elevation': 20.0,
                'sunlight': 0.5,
                'biome_name': 'Snow/Tundra',
            })()
            return sample

    class DummyClimateMild:
        def get_environment(self, x, y, z):
            sample = type('Env', (), {
                'temperature': 18.0,
                'humidity': 0.6,
                'rainfall': 0.5,
                'elevation': 20.0,
                'sunlight': 0.7,
                'biome_name': 'Plains',
            })()
            return sample

    state = VerdantWorldState(current_season='spring')
    eco_cold = VerdantEcologySystem(world_state=state, climate_system=DummyClimateCold(), seed=404)
    eco_mild = VerdantEcologySystem(world_state=state, climate_system=DummyClimateMild(), seed=404)

    cold_growth = eco_cold.get_growth_potential(5, 5, 5)
    mild_growth = eco_mild.get_growth_potential(5, 5, 5)

    assert cold_growth < mild_growth


# 10. Fertility is deterministic.
def test_fertility_is_deterministic():
    state = VerdantWorldState()
    state.metadata['seed'] = 505
    eco = VerdantEcologySystem(world_state=state)

    f1 = eco.get_fertility(8, 14, 8)
    f2 = eco.get_fertility(8, 14, 8)
    f3 = eco.get_fertility(9, 14, 8)

    assert f1 == f2
    assert 0.0 <= f1 <= 1.0
    assert 0.0 <= f3 <= 1.0


# 11. Vegetation health remains within documented bounds.
def test_vegetation_health_within_bounds():
    state = VerdantWorldState()
    eco = VerdantEcologySystem(world_state=state, seed=606)

    for x in range(0, 30, 5):
        for z in range(0, 30, 5):
            health = eco.get_vegetation_health(x, 15, z)
            assert 0.0 <= health <= 1.0


# 12. Growth potential remains within documented bounds.
def test_growth_potential_within_bounds():
    state = VerdantWorldState()
    eco = VerdantEcologySystem(world_state=state, seed=707)

    for season in ['spring', 'summer', 'autumn', 'winter']:
        state.set_season(season)
        for x in [0, 10, 25]:
            growth = eco.get_growth_potential(x, 12, x)
            assert 0.0 <= growth <= 1.0


# 13. Stress remains within documented bounds.
def test_stress_within_bounds():
    state = VerdantWorldState()
    eco = VerdantEcologySystem(world_state=state, seed=808)

    for season in ['spring', 'summer', 'autumn', 'winter']:
        state.set_season(season)
        for x in [2, 14, 28]:
            stress = eco.get_environmental_stress(x, 10, x)
            assert 0.0 <= stress <= 1.0


# 14. M5 moisture queries remain functional.
def test_m5_moisture_queries_remain_functional():
    from verdant.water.queries import get_soil_moisture, get_surface_water_presence, is_near_water
    state = VerdantWorldState()
    state.metadata['seed'] = 909

    moisture = get_soil_moisture(10, 10, 10, world_state=state)
    presence = get_surface_water_presence(10, 10, 10, world_state=state)
    near = is_near_water(10, 10, 10, world_state=state)

    assert 0.0 <= moisture <= 1.0
    assert 0.0 <= presence <= 1.0
    assert isinstance(near, bool)


# 15. M4 vegetation queries remain functional.
def test_m4_vegetation_queries_remain_functional():
    system = VerdantVegetationSystem(world_state=VerdantWorldState())
    env = system.get_environment_for(4, 8, 4)

    assert system.is_vegetation_suitable(env, 'grass') in (True, False)
    assert system.get_tree_density(env) >= 0.0
    assert system.get_grass_density(env) >= 0.0


# 16. M3 climate queries remain functional.
def test_m3_climate_queries_remain_functional():
    climate = VerdantClimateSystem(world_state=VerdantWorldState(current_season='spring'))
    env = climate.get_environment(5, 10, 5)

    assert env.temperature >= -30.0
    assert 0.0 <= env.humidity <= 1.0
    assert 0.0 <= env.rainfall <= 1.0
    assert env.biome_name in ['Ocean', 'Plains', 'Forest', 'Desert', 'Mountains', 'Snow/Tundra', 'Swamp']


# 17. M2 simulation tests still pass.
def test_m2_simulation_tests_still_pass():
    state = VerdantWorldState()
    assert state.simulation_version == 1
    assert state.current_season == 'spring'
    clock = VerdantSimulationClock(state)
    clock.advance(5)
    assert clock.elapsed_ticks == 5


# 18. M3 tests still pass.
def test_m3_smoke_compatibility():
    import tests.test_verdant_m3 as m3
    for name in dir(m3):
        if name.startswith('test_') and callable(getattr(m3, name)):
            getattr(m3, name)()


# 19. M4 tests still pass.
def test_m4_smoke_compatibility():
    import tests.test_verdant_m4 as m4
    for name in dir(m4):
        if name.startswith('test_') and callable(getattr(m4, name)):
            getattr(m4, name)()


# 20. M5 tests still pass.
def test_m5_smoke_compatibility():
    import tests.test_verdant_m5 as m5
    for name in dir(m5):
        if name.startswith('test_') and callable(getattr(m5, name)):
            getattr(m5, name)()


# 21. No second simulation loop exists.
def test_no_second_simulation_loop_exists():
    state = VerdantWorldState()
    eco = VerdantEcologySystem(world_state=state)
    assert callable(eco.update)
    assert eco.update() is eco
    assert not hasattr(eco, '_thread')
    assert not hasattr(eco, '_running_loop')


# 22. No global world scan is introduced.
def test_no_global_world_scan_is_introduced():
    class MonitoredWorld:
        def __init__(self):
            self.calls = []

        def getBlockId(self, x, y, z):
            self.calls.append((x, y, z))
            return 0

        def getGroundLevel(self):
            return 64

    world = MonitoredWorld()
    state = VerdantWorldState(world=world)
    eco = VerdantEcologySystem(world_state=state)

    # Calling query for single coord should only touch local neighbourhood or none at all
    _ = eco.get_vegetation_state(10, 64, 10)
    assert len(world.calls) < 25000  # Well bounded, localized radius around (x, y, z), nowhere near a full map scan (4.2M blocks)


# 23. No uncontrolled global random state is introduced.
def test_no_uncontrolled_global_random_state():
    state = VerdantWorldState()
    state.metadata['seed'] = 12345
    eco = VerdantEcologySystem(world_state=state)

    res_first = [eco.get_vegetation_state(i, 10, i).as_dict() for i in range(5)]
    res_second = [eco.get_vegetation_state(i, 10, i).as_dict() for i in range(5)]

    assert res_first == res_second
