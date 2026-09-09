import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verdant.world.state import VerdantWorldState
from verdant.world.clock import VerdantSimulationClock
from verdant.simulation.manager import VerdantSimulationManager
from verdant.environment.climate import VerdantClimateSystem
from verdant.water.system import VerdantWaterSystem
from verdant.ecology.system import VerdantEcologySystem
from verdant.creatures.system import VerdantCreatureSystem
from verdant.ecosystem import (
    VerdantPopulationSample,
    VerdantResourceEvaluator,
    VerdantPopulationDynamics,
    VerdantEcosystemSystem,
    get_population_state,
    get_population_pressure,
    get_resource_pressure,
    get_food_availability,
    get_water_availability,
    get_shelter_availability,
    get_sustainability,
    get_population_trend,
    get_recovery_tendency,
    get_expansion_tendency,
)


class MockWorld:
    """Mock Indev World for unit testing entity and spatial evaluations."""
    def __init__(self, width=64, height=64, length=32):
        self.width = width
        self.height = height
        self.length = length
        self.blocks = bytearray(width * height * length)
        self.data = bytearray(width * height * length)
        self.entities = []

    def _index(self, x, y, z):
        return (int(y) * self.length + int(z)) * self.width + int(x)

    def getBlockId(self, x, y, z):
        if 0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.length:
            return self.blocks[self._index(x, y, z)]
        return 0

    def setBlock(self, x, y, z, block_id):
        if 0 <= x < self.width and 0 <= y < self.height and 0 <= z < self.length:
            self.blocks[self._index(x, y, z)] = block_id

    def isBlockNormalCube(self, x, y, z):
        bid = self.getBlockId(x, y, z)
        return bid in (1, 2, 3, 4, 5, 17, 18)

    def getBlockLightValue(self, x, y, z):
        return 12


class MockEntity:
    def __init__(self, entity_id, name, x, y, z):
        self.entityId = entity_id
        self.entity_type = name
        self.__class__.__name__ = name
        self.posX = float(x)
        self.posY = float(y)
        self.posZ = float(z)


# 1. Population state construction
def test_1_population_state_construction():
    sample = VerdantPopulationSample(
        species='pig',
        center_x=10.0,
        center_y=12.0,
        center_z=14.0,
        radius=16.0,
        count=4,
        density=0.5,
        habitat_quality=0.85,
        food_availability=0.8,
        water_availability=0.75,
        shelter_availability=0.6,
        population_pressure=0.35,
        resource_pressure=0.25,
        ecological_stress=0.15,
        sustainability=0.72,
        recovery_tendency=0.45,
        expansion_tendency=0.2,
        trend='growing',
    )
    assert sample.species == 'pig'
    assert sample.count == 4
    assert sample.density == 0.5
    assert sample.trend == 'growing'

    d = sample.as_dict()
    assert isinstance(d, dict)
    assert d['center_x'] == 10.0
    assert d['sustainability'] == 0.72


# 2. Local population counting
def test_2_local_population_counting():
    system = VerdantEcosystemSystem(seed=100)
    world = MockWorld()

    world.entities = [
        MockEntity(1, 'EntityPig', 10.0, 10.0, 10.0),
        MockEntity(2, 'EntityPig', 12.0, 10.0, 11.0),
        MockEntity(3, 'EntitySheep', 14.0, 10.0, 12.0),
        MockEntity(4, 'EntityZombie', 15.0, 10.0, 15.0),
        MockEntity(5, 'EntityPig', 50.0, 10.0, 50.0),  # Far outside
    ]

    total_count = system.count_local_entities(10.0, 10.0, 10.0, radius=16.0, world=world)
    assert total_count == 4

    herbivore_count = system.count_local_entities(10.0, 10.0, 10.0, radius=16.0, species_filter='herbivore', world=world)
    assert herbivore_count == 3


# 3. Bounded spatial queries
def test_3_bounded_spatial_queries():
    system = VerdantEcosystemSystem(seed=100)
    assert system._sanitize_radius(32.0) == 16.0
    assert system._sanitize_radius(-5.0) == 1.0
    assert system._sanitize_radius(10.0) == 10.0


# 4. Food/resource pressure
def test_4_food_resource_pressure():
    evaluator = VerdantResourceEvaluator()
    food_lush = evaluator.evaluate_food_availability('herbivore', growth_potential=0.9, vegetation_health=0.9, fertility=0.8, biome_name='Plains')
    food_barren = evaluator.evaluate_food_availability('herbivore', growth_potential=0.05, vegetation_health=0.05, fertility=0.05, biome_name='Desert')

    assert food_lush > food_barren
    assert food_barren < 0.10

    # Test resource pressure with abundant food vs starving
    p_lush = evaluator.calculate_resource_pressure(food=food_lush, water=0.8, shelter=0.6, population_demand=0.2, species='herbivore')
    p_starve = evaluator.calculate_resource_pressure(food=food_barren, water=0.8, shelter=0.6, population_demand=0.5, species='herbivore')

    assert p_starve > p_lush
    assert p_starve >= 0.75


# 5. Water/resource pressure
def test_5_water_resource_pressure():
    evaluator = VerdantResourceEvaluator()
    w_rich = evaluator.evaluate_water_availability(soil_moisture=0.8, surface_water=1.0, water_proximity=0.9)
    w_dry = evaluator.evaluate_water_availability(soil_moisture=0.0, surface_water=0.0, water_proximity=0.0)

    assert w_rich > w_dry
    assert w_dry == 0.0

    p_drought = evaluator.calculate_resource_pressure(food=0.8, water=w_dry, shelter=0.6, population_demand=0.3, species='herbivore')
    assert p_drought >= 0.75


# 6. Shelter/resource pressure
def test_6_shelter_resource_pressure():
    evaluator = VerdantResourceEvaluator()
    world = MockWorld()

    for dy in range(1, 4):
        world.setBlock(10, 10 + dy, 10, 1)

    shelter_cave = evaluator.evaluate_shelter_availability('hostile', 10, 10, 10, world=world)
    shelter_open = evaluator.evaluate_shelter_availability('hostile', 30, 10, 30, world=world, sunlight=1.0)

    assert shelter_cave > shelter_open
    assert shelter_cave >= 0.60


# 7. Habitat pressure
def test_7_habitat_pressure():
    dynamics = VerdantPopulationDynamics()
    # High habitat quality + low count = low habitat pressure
    p_low = dynamics.calculate_habitat_pressure(habitat_quality=0.9, count=1, species='herbivore')
    # Low habitat quality + high count = high habitat pressure
    p_high = dynamics.calculate_habitat_pressure(habitat_quality=0.1, count=8, species='herbivore')

    assert p_high > p_low
    assert p_high > 0.70


# 8. Sustainability calculation
def test_8_sustainability_calculation():
    dynamics = VerdantPopulationDynamics()

    # Thriving condition
    s_thriving = dynamics.calculate_sustainability(
        habitat_quality=0.9,
        food=0.9,
        water=0.85,
        shelter=0.7,
        population_pressure=0.1,
        species='herbivore',
    )

    # Starving/overcrowded condition
    s_starving = dynamics.calculate_sustainability(
        habitat_quality=0.2,
        food=0.1,
        water=0.1,
        shelter=0.3,
        population_pressure=0.9,
        species='herbivore',
    )

    assert s_thriving > s_starving
    assert s_thriving >= 0.70
    assert s_starving <= 0.15


# 9. Recovery tendency
def test_9_recovery_tendency():
    dynamics = VerdantPopulationDynamics()

    # Optimal conditions: high sustainability, low pressure, low stress
    rec_pos = dynamics.calculate_recovery_tendency(
        sustainability=0.85,
        population_pressure=0.15,
        food=0.9,
        water=0.8,
        stress=0.1,
    )
    assert rec_pos > 0.30

    # Severe stress condition
    rec_neg = dynamics.calculate_recovery_tendency(
        sustainability=0.20,
        population_pressure=0.80,
        food=0.1,
        water=0.1,
        stress=0.75,
    )
    assert rec_neg < -0.20


# 10. Expansion tendency
def test_10_expansion_tendency():
    dynamics = VerdantPopulationDynamics()

    # Thriving, dense population ready to expand
    exp_high = dynamics.calculate_expansion_tendency(
        sustainability=0.8,
        population_pressure=0.6,
        density=0.7,
        stress=0.2,
    )

    # Sparse population
    exp_low = dynamics.calculate_expansion_tendency(
        sustainability=0.8,
        population_pressure=0.1,
        density=0.1,
        stress=0.2,
    )

    assert exp_high > exp_low
    assert exp_high > 0.40


# 11. Population trend classification
def test_11_population_trend_classification():
    dynamics = VerdantPopulationDynamics()

    t_rec = dynamics.classify_trend(sustainability=0.85, population_pressure=0.1, recovery_tendency=0.5, density=0.2)
    assert t_rec == 'recovering'

    t_grow = dynamics.classify_trend(sustainability=0.70, population_pressure=0.3, recovery_tendency=0.2, density=0.5)
    assert t_grow == 'growing'

    t_dec = dynamics.classify_trend(sustainability=0.15, population_pressure=0.8, recovery_tendency=-0.4, density=0.8)
    assert t_dec == 'declining'


# 12. Species profile behavior
def test_12_species_profile_behavior():
    dynamics = VerdantPopulationDynamics()

    prof_herb = dynamics.get_profile('herbivore')
    prof_host = dynamics.get_profile('hostile')

    assert prof_herb['food_weight'] > prof_host['food_weight']
    assert prof_host['shelter_weight'] > prof_herb['shelter_weight']


# 13. Deterministic repeated evaluation
def test_13_deterministic_repeated_evaluation():
    system = VerdantEcosystemSystem(seed=777)
    world = MockWorld()
    world.entities = [MockEntity(1, 'EntityPig', 10.0, 10.0, 10.0)]

    samples = []
    for _ in range(5):
        s = system.evaluate_population_sample(10.0, 10.0, 10.0, radius=16.0, species='herbivore', world=world)
        samples.append(s.as_dict())

    for s in samples[1:]:
        assert s == samples[0]


# 14. Global random independence
def test_14_global_random_independence():
    import random
    system = VerdantEcosystemSystem(seed=999)
    world = MockWorld()

    random.seed(12345)
    s1 = system.evaluate_population_sample(15.0, 10.0, 15.0, radius=16.0, species='pig', world=world)

    random.seed(987654)
    s2 = system.evaluate_population_sample(15.0, 10.0, 15.0, radius=16.0, species='pig', world=world)

    assert s1.as_dict() == s2.as_dict()


# 15. Simulation manager integration
def test_15_simulation_manager_integration():
    world_state = VerdantWorldState()
    clock = VerdantSimulationClock(world_state)
    manager = VerdantSimulationManager(context={'world': MockWorld()})
    eco_sys = VerdantEcosystemSystem(world_state=world_state, clock=clock)

    assert manager.register(clock) is True
    assert manager.register(eco_sys) is True

    manager.initialize()
    assert eco_sys.initialized is True

    manager.update(delta_ticks=40)
    assert clock.elapsed_ticks == 40
    assert eco_sys.get_world_age_ticks() == 40


# 16. M7 creature compatibility
def test_16_m7_creature_compatibility():
    system = VerdantEcosystemSystem(seed=42)
    world = MockWorld()
    world.entities = [
        MockEntity(1, 'EntityPig', 10.0, 10.0, 10.0),
        MockEntity(2, 'EntitySheep', 12.0, 10.0, 12.0),
    ]

    sample = system.evaluate_population_sample(10.0, 10.0, 10.0, radius=16.0, species='pig', world=world)
    assert sample.count >= 1
    assert 0.0 <= sample.habitat_quality <= 1.0


# 17. M6 vegetation compatibility
def test_17_m6_vegetation_compatibility():
    system = VerdantEcosystemSystem(seed=42)
    world = MockWorld()
    world.entities = [MockEntity(i, 'EntityPig', 10.0, 10.0, 10.0) for i in range(6)]

    grazing_pressure = system.get_herbivore_grazing_pressure(10.0, 10.0, 10.0, radius=16.0, world=world)
    assert 0.0 <= grazing_pressure <= 1.0
    assert grazing_pressure > 0.40


# 18. Public query coverage
def test_18_public_queries():
    world = MockWorld()
    state = get_population_state(10.0, 10.0, 10.0, radius=16.0, species='pig', world=world, seed=555)

    pop_p = get_population_pressure(10.0, 10.0, 10.0, radius=16.0, species='pig', world=world, seed=555)
    res_p = get_resource_pressure(10.0, 10.0, 10.0, radius=16.0, species='pig', world=world, seed=555)
    food = get_food_availability(10.0, 10.0, 10.0, radius=16.0, species='pig', world=world, seed=555)
    water = get_water_availability(10.0, 10.0, 10.0, radius=16.0, world=world, seed=555)
    shelter = get_shelter_availability(10.0, 10.0, 10.0, radius=16.0, species='pig', world=world, seed=555)
    sust = get_sustainability(10.0, 10.0, 10.0, radius=16.0, species='pig', world=world, seed=555)
    trend = get_population_trend(10.0, 10.0, 10.0, radius=16.0, species='pig', world=world, seed=555)
    rec = get_recovery_tendency(10.0, 10.0, 10.0, radius=16.0, species='pig', world=world, seed=555)
    exp = get_expansion_tendency(10.0, 10.0, 10.0, radius=16.0, species='pig', world=world, seed=555)

    assert pop_p == state.population_pressure
    assert res_p == state.resource_pressure
    assert food == state.food_availability
    assert water == state.water_availability
    assert shelter == state.shelter_availability
    assert sust == state.sustainability
    assert trend == state.trend
    assert rec == state.recovery_tendency
    assert exp == state.expansion_tendency
