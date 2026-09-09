import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verdant.world.state import VerdantWorldState
from verdant.world.clock import VerdantSimulationClock
from verdant.simulation.manager import VerdantSimulationManager
from verdant.environment.climate import VerdantClimateSystem
from verdant.environment.biome import VerdantBiomeResolver
from verdant.water.system import VerdantWaterSystem
from verdant.ecology.system import VerdantEcologySystem
from verdant.creatures import (
    VerdantCreatureState,
    VerdantHabitatEvaluator,
    VerdantBehaviorContext,
    VerdantCreatureSystem,
    get_creature_state,
    get_habitat_score,
    get_food_suitability,
    get_water_access,
    get_shelter_score,
    get_population_pressure,
    get_activity_tendency,
    get_behavior_context,
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
        self.__class__.__name__ = name
        self.posX = float(x)
        self.posY = float(y)
        self.posZ = float(z)


# 1. Creature state construction
def test_1_creature_state_construction():
    state = VerdantCreatureState(
        species='pig',
        habitat_score=0.82,
        temperature_score=0.9,
        moisture_score=0.75,
        food_score=0.8,
        water_score=0.7,
        shelter_score=0.5,
        safety_score=0.95,
        population_pressure=0.2,
        stress=0.1,
        activity='active',
        movement_bias=(0.1, 0.0, -0.2),
        behavior_context='wander',
    )
    assert state.species == 'pig'
    assert state.habitat_score == 0.82
    assert state.stress == 0.1
    assert state.behavior_context == 'wander'

    d = state.as_dict()
    assert isinstance(d, dict)
    assert d['species'] == 'pig'
    assert d['habitat_score'] == 0.82
    assert tuple(d['movement_bias']) == (0.1, 0.0, -0.2)


# 2. Deterministic habitat evaluation
def test_2_deterministic_habitat_evaluation():
    evaluator = VerdantHabitatEvaluator(seed=12345)
    world = MockWorld()

    eval_1 = evaluator.evaluate_habitat(
        species='pig',
        temperature=20.0,
        soil_moisture=0.6,
        water_proximity=0.5,
        surface_water=0.0,
        growth_potential=0.8,
        vegetation_health=0.85,
        fertility=0.7,
        ecological_stress=0.1,
        biome_name='Plains',
        sunlight=0.8,
        world=world,
        x=10.0, y=10.0, z=10.0,
    )
    eval_2 = evaluator.evaluate_habitat(
        species='pig',
        temperature=20.0,
        soil_moisture=0.6,
        water_proximity=0.5,
        surface_water=0.0,
        growth_potential=0.8,
        vegetation_health=0.85,
        fertility=0.7,
        ecological_stress=0.1,
        biome_name='Plains',
        sunlight=0.8,
        world=world,
        x=10.0, y=10.0, z=10.0,
    )

    assert eval_1 == eval_2
    assert 0.0 <= eval_1['habitat_score'] <= 1.0


# 3. Biome compatibility
def test_3_biome_compatibility():
    evaluator = VerdantHabitatEvaluator()
    plains_score = evaluator.get_biome_compatibility('pig', 'Plains')
    desert_score = evaluator.get_biome_compatibility('pig', 'Desert')

    assert plains_score > desert_score
    assert plains_score == 1.0
    assert desert_score == 0.10


# 4. Temperature suitability
def test_4_temperature_suitability():
    evaluator = VerdantHabitatEvaluator()

    # Ideal temperature for herbivore (14-24C)
    score_ideal = evaluator.get_temperature_score('pig', 20.0)
    assert score_ideal == 1.0

    # Extreme cold
    score_cold = evaluator.get_temperature_score('pig', -10.0)
    assert score_cold < 0.20

    # Extreme heat
    score_hot = evaluator.get_temperature_score('pig', 45.0)
    assert score_hot == 0.0


# 5. Moisture suitability
def test_5_moisture_suitability():
    evaluator = VerdantHabitatEvaluator()

    moist_high = evaluator.get_moisture_score('pig', soil_moisture=0.8, water_proximity=0.9)
    moist_drought = evaluator.get_moisture_score('pig', soil_moisture=0.05, water_proximity=0.0)

    assert moist_high > moist_drought
    assert moist_drought < 0.20


# 6. Food/vegetation suitability
def test_6_food_vegetation_suitability():
    evaluator = VerdantHabitatEvaluator()

    food_lush = evaluator.get_food_suitability('sheep', growth_potential=0.9, vegetation_health=0.9, fertility=0.8, biome_name='Plains')
    food_barren = evaluator.get_food_suitability('sheep', growth_potential=0.1, vegetation_health=0.1, fertility=0.1, biome_name='Desert')

    assert food_lush > food_barren
    assert food_barren < 0.10


# 7. Water accessibility
def test_7_water_accessibility():
    evaluator = VerdantHabitatEvaluator()

    water_near = evaluator.get_water_access('pig', soil_moisture=0.8, surface_water=1.0, water_proximity=1.0)
    water_none = evaluator.get_water_access('pig', soil_moisture=0.0, surface_water=0.0, water_proximity=0.0)

    assert water_near > 0.8
    assert water_none == 0.0


# 8. Shelter evaluation
def test_8_shelter_evaluation():
    evaluator = VerdantHabitatEvaluator()
    world = MockWorld()

    # Build an overhead ceiling (leaves/wood/stone)
    for dy in range(1, 4):
        world.setBlock(10, 10 + dy, 10, 1)  # stone overhead

    sheltered = evaluator.get_shelter_score('zombie', 10, 10, 10, world=world)
    open_sky = evaluator.get_shelter_score('zombie', 30, 10, 30, world=world, sunlight=1.0)

    assert sheltered > open_sky
    assert sheltered >= 0.60


# 9. Population pressure logic
def test_9_population_pressure_logic():
    system = VerdantCreatureSystem(seed=42)
    world = MockWorld()

    # System without entityMap falls back to deterministic bounded noise
    press_val = system.get_population_pressure(10, 10, 10, radius=16.0, world=world)
    assert 0.0 <= press_val <= 1.0

    # Test calculate_population_pressure entity overload
    pig = MockEntity(1, 'EntityPig', 10, 10, 10)
    press_ent = system.calculate_population_pressure(pig, world=world, radius=16.0)
    assert 0.0 <= press_ent <= 1.0


# 10. Behavior context
def test_10_behavior_context():
    behavior_ctx = VerdantBehaviorContext()

    # Severe dehydration
    res_thirst = behavior_ctx.determine_behavior(
        species='pig',
        habitat_score=0.5,
        food_score=0.8,
        water_score=0.1,
        shelter_score=0.5,
        safety_score=1.0,
        population_pressure=0.0,
        stress=0.5,
        is_daylight=True,
    )
    assert res_thirst['behavior_context'] == 'seek_water'

    # High crowding pressure
    res_crowd = behavior_ctx.determine_behavior(
        species='pig',
        habitat_score=0.5,
        food_score=0.8,
        water_score=0.8,
        shelter_score=0.5,
        safety_score=1.0,
        population_pressure=0.85,
        stress=0.8,
        is_daylight=True,
    )
    assert res_crowd['behavior_context'] == 'avoid_stress'

    # Undead in direct daylight with no shelter
    res_undead = behavior_ctx.determine_behavior(
        species='zombie',
        habitat_score=0.3,
        food_score=0.5,
        water_score=0.5,
        shelter_score=0.2,
        safety_score=0.1,
        population_pressure=0.0,
        stress=0.2,
        is_daylight=True,
    )
    assert res_undead['behavior_context'] == 'seek_shelter'


# 11. Deterministic repeated evaluation
def test_11_deterministic_repeated_evaluation():
    system = VerdantCreatureSystem(seed=7777)
    world = MockWorld()

    results = []
    for _ in range(5):
        st = system.get_creature_state('sheep', 20.0, 10.0, 20.0, world=world)
        results.append(st.as_dict())

    # Ensure all 5 runs are strictly identical
    for r in results[1:]:
        assert r == results[0]


# 12. No global random dependency
def test_12_no_global_random_dependency():
    import random
    system = VerdantCreatureSystem(seed=8888)
    world = MockWorld()

    # Perturb python's global random seed
    random.seed(1111)
    st_a = system.get_creature_state('zombie', 15.0, 10.0, 15.0, world=world)

    random.seed(999999)
    st_b = system.get_creature_state('zombie', 15.0, 10.0, 15.0, world=world)

    assert st_a.habitat_score == st_b.habitat_score
    assert st_a.stress == st_b.stress
    assert st_a.behavior_context == st_b.behavior_context


# 13. Existing entity compatibility (EntityPig, EntitySheep, EntityZombie, etc.)
def test_13_existing_entity_compatibility():
    system = VerdantCreatureSystem(seed=123)
    world = MockWorld()

    pig = MockEntity(1, 'EntityPig', 10, 5, 10)
    sheep = MockEntity(2, 'EntitySheep', 12, 5, 10)
    zombie = MockEntity(3, 'EntityZombie', 14, 5, 10)
    skeleton = MockEntity(4, 'EntitySkeleton', 16, 5, 10)
    spider = MockEntity(5, 'EntitySpider', 18, 5, 10)
    creeper = MockEntity(6, 'EntityCreeper', 20, 5, 10)

    for entity in [pig, sheep, zombie, skeleton, spider, creeper]:
        species = system._map_entity_to_species(entity)
        assert species in ['pig', 'sheep', 'zombie', 'skeleton', 'spider', 'creeper']

        state = system.get_or_evaluate_creature(entity, world=world, tick=100)
        assert state is not None
        assert state.species == species
        assert 0.0 <= state.habitat_score <= 1.0


# 14. Simulation manager integration
def test_14_simulation_manager_integration():
    world_state = VerdantWorldState()
    clock = VerdantSimulationClock(world_state)
    manager = VerdantSimulationManager(context={'world': MockWorld()})
    creature_sys = VerdantCreatureSystem(world_state=world_state, clock=clock)

    assert manager.register(clock) is True
    assert manager.register(creature_sys) is True

    manager.initialize()
    assert creature_sys.initialized is True

    # Advance ticks
    manager.update(delta_ticks=20)
    assert clock.elapsed_ticks == 20
    assert creature_sys.get_world_age_ticks() == 20


# 15. Queries module coverage
def test_15_queries_module_coverage():
    world = MockWorld()
    state = get_creature_state('pig', 10.0, 10.0, 10.0, world=world, seed=54321)

    hab = get_habitat_score('pig', 10.0, 10.0, 10.0, world=world, seed=54321)
    food = get_food_suitability('pig', 10.0, 10.0, 10.0, world=world, seed=54321)
    water = get_water_access('pig', 10.0, 10.0, 10.0, world=world, seed=54321)
    shelter = get_shelter_score('pig', 10.0, 10.0, 10.0, world=world, seed=54321)
    pressure = get_population_pressure(10.0, 10.0, 10.0, world=world, seed=54321)
    act = get_activity_tendency('pig', 10.0, 10.0, 10.0, world=world, seed=54321)
    beh = get_behavior_context('pig', 10.0, 10.0, 10.0, world=world, seed=54321)

    assert hab == state.habitat_score
    assert food == state.food_score
    assert water == state.water_score
    assert shelter == state.shelter_score
    assert pressure == state.population_pressure
    assert act == state.activity
    assert beh == state.behavior_context
