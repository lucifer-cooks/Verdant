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
from verdant.ecosystem.system import VerdantEcosystemSystem
from verdant.feedback import (
    VerdantEcologicalSignals,
    VerdantVegetationFeedback,
    VerdantHabitatFeedback,
    VerdantWaterFeedback,
    VerdantFeedbackSystem,
    get_ecosystem_state,
    get_ecological_health,
    get_grazing_pressure,
    get_vegetation_stress,
    get_vegetation_recovery,
    get_habitat_pressure,
    get_water_stress,
    get_drought_pressure,
    get_population_pressure,
    get_adaptive_response,
    explain_ecosystem,
)


class MockWorld:
    """Mock Indev World for unit testing feedback mechanisms."""
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


# 1. Signal construction
def test_1_signal_construction():
    signals = VerdantEcologicalSignals(
        x=10.0, y=10.0, z=10.0, radius=16.0,
        grazing_pressure=0.25, vegetation_stress=0.3,
        vegetation_recovery=0.7, habitat_pressure=0.2,
        resource_pressure=0.15, water_stress=0.2,
        drought_pressure=0.1, population_pressure=0.3,
        ecological_health=0.8, ecosystem_stability=0.75,
        adaptive_response='healthy',
    )
    assert signals.x == 10.0
    assert signals.grazing_pressure == 0.25
    assert signals.adaptive_response == 'healthy'

    d = signals.as_dict()
    assert isinstance(d, dict)
    assert d['ecological_health'] == 0.8


# 2. Signal normalization
def test_2_signal_normalization():
    system = VerdantFeedbackSystem(seed=42)
    world = MockWorld()
    signals = system.evaluate_ecological_signals(10.0, 10.0, 10.0, radius=16.0, world=world)

    for field in [
        'grazing_pressure', 'vegetation_stress', 'vegetation_recovery',
        'habitat_pressure', 'resource_pressure', 'water_stress',
        'drought_pressure', 'population_pressure', 'ecological_health',
        'ecosystem_stability',
    ]:
        val = getattr(signals, field)
        assert 0.0 <= val <= 1.0, f"{field} was {val}, out of [0, 1]"


# 3. Grazing pressure
def test_3_grazing_pressure():
    veg_fb = VerdantVegetationFeedback()
    gp_zero = veg_fb.evaluate_grazing_pressure(0)
    gp_mod = veg_fb.evaluate_grazing_pressure(4)
    gp_high = veg_fb.evaluate_grazing_pressure(10)

    assert gp_zero == 0.0
    assert gp_mod > gp_zero
    assert gp_high > gp_mod
    assert gp_high >= 0.80


# 4. Vegetation stress feedback
def test_4_vegetation_stress_feedback():
    veg_fb = VerdantVegetationFeedback()
    stress_base = veg_fb.calculate_vegetation_stress_feedback(base_stress=0.2, grazing_pressure=0.1, moisture=0.8)
    stress_grazed = veg_fb.calculate_vegetation_stress_feedback(base_stress=0.2, grazing_pressure=0.8, moisture=0.1)

    assert stress_grazed > stress_base
    assert stress_grazed > 0.50


# 5. Vegetation recovery feedback
def test_5_vegetation_recovery_feedback():
    veg_fb = VerdantVegetationFeedback()
    rec_healthy = veg_fb.calculate_vegetation_recovery_feedback(
        growth_potential=0.9, vegetation_health=0.9, fertility=0.8,
        grazing_pressure=0.1, vegetation_stress=0.1,
    )
    rec_strained = veg_fb.calculate_vegetation_recovery_feedback(
        growth_potential=0.9, vegetation_health=0.9, fertility=0.8,
        grazing_pressure=0.9, vegetation_stress=0.8,
    )

    assert rec_healthy > rec_strained
    assert rec_healthy >= 0.60


# 6. Habitat pressure
def test_6_habitat_pressure():
    hab_fb = VerdantHabitatFeedback()
    p_low = hab_fb.calculate_habitat_pressure(base_habitat_quality=0.9, population_pressure=0.1, resource_pressure=0.1)
    p_high = hab_fb.calculate_habitat_pressure(base_habitat_quality=0.2, population_pressure=0.8, resource_pressure=0.8)

    assert p_high > p_low
    assert p_high >= 0.65

    score_norm = hab_fb.modulate_habitat_score(0.8, habitat_pressure=p_low, ecosystem_health=0.8)
    score_deg = hab_fb.modulate_habitat_score(0.8, habitat_pressure=p_high, ecosystem_health=0.2)
    assert score_norm > score_deg


# 7. Water stress
def test_7_water_stress():
    water_fb = VerdantWaterFeedback()
    stress_wet = water_fb.calculate_water_stress(soil_moisture=0.8, rainfall=0.9, temperature=18.0, ecosystem_demand=0.2)
    stress_dry = water_fb.calculate_water_stress(soil_moisture=0.05, rainfall=0.1, temperature=35.0, ecosystem_demand=0.8)

    assert stress_dry > stress_wet
    assert stress_dry >= 0.70


# 8. Drought pressure
def test_8_drought_pressure():
    water_fb = VerdantWaterFeedback()
    dp_mild = water_fb.calculate_drought_pressure(water_stress=0.2, soil_moisture=0.8, rainfall=0.8, season='spring')
    dp_severe = water_fb.calculate_drought_pressure(water_stress=0.85, soil_moisture=0.05, rainfall=0.05, season='summer')

    assert dp_severe > dp_mild
    assert dp_severe >= 0.80


# 9. Ecosystem health
def test_9_ecosystem_health():
    system = VerdantFeedbackSystem(seed=555)

    health_prime = system.calculate_ecosystem_health(
        climate_suitability=0.9, moisture=0.85, vegetation_health=0.9,
        fertility=0.85, habitat_quality=0.9, population_pressure=0.1,
        resource_pressure=0.1, drought_pressure=0.1,
    )

    health_crisis = system.calculate_ecosystem_health(
        climate_suitability=0.2, moisture=0.1, vegetation_health=0.2,
        fertility=0.2, habitat_quality=0.2, population_pressure=0.9,
        resource_pressure=0.9, drought_pressure=0.9,
    )

    assert health_prime > health_crisis
    assert health_prime >= 0.70
    assert health_crisis <= 0.15


# 10. Adaptive response states
def test_10_adaptive_response_states():
    system = VerdantFeedbackSystem()

    s_thriving = system.classify_adaptive_response(health=0.85, stability=0.80, stress=0.10, recovery=0.8)
    assert s_thriving == 'thriving'

    s_healthy = system.classify_adaptive_response(health=0.65, stability=0.60, stress=0.25, recovery=0.6)
    assert s_healthy == 'healthy'

    s_stressed = system.classify_adaptive_response(health=0.35, stability=0.30, stress=0.65, recovery=0.2)
    assert s_stressed == 'stressed'

    s_degraded = system.classify_adaptive_response(health=0.15, stability=0.10, stress=0.85, recovery=0.05)
    assert s_degraded == 'degraded'


# 11. Temporal smoothing
def test_11_temporal_smoothing():
    system = VerdantFeedbackSystem(seed=777)
    world = MockWorld()

    # Initial state evaluation
    s1 = system.evaluate_ecological_signals(10.0, 10.0, 10.0, radius=16.0, world=world)

    # Now add severe disturbance (e.g. overcrowding)
    for i in range(12):
        world.entities.append(MockEntity(i, 'EntityPig', 10.0, 10.0, 10.0))

    s2 = system.evaluate_ecological_signals(10.0, 10.0, 10.0, radius=16.0, world=world)
    s3 = system.evaluate_ecological_signals(10.0, 10.0, 10.0, radius=16.0, world=world)

    # Health smoothly declines across evaluations rather than instantaneously crashing to 0
    assert s1.ecological_health >= s2.ecological_health
    assert s2.ecological_health >= s3.ecological_health


# 12. Hysteresis / stability
def test_12_hysteresis_stability():
    system = VerdantFeedbackSystem()

    # In stable state, a minor stress blip stays in stable buffer rather than flapping
    state = system.classify_adaptive_response(health=0.50, stability=0.50, stress=0.45, recovery=0.40, prev_state='stable')
    assert state == 'stable'


# 13. Local spatial bounds
def test_13_local_spatial_bounds():
    system = VerdantFeedbackSystem()
    assert system._sanitize_radius(32.0) == 16.0
    assert system._sanitize_radius(0.0) == 1.0
    assert system._sanitize_radius(12.0) == 12.0


# 14. Deterministic repeated evaluation
def test_14_deterministic_repeated_evaluation():
    system = VerdantFeedbackSystem(seed=999)
    world = MockWorld()

    runs = []
    for _ in range(5):
        sig = system.evaluate_ecological_signals(20.0, 10.0, 20.0, radius=16.0, world=world)
        runs.append(sig.as_dict())

    # All runs must be strictly identical once cached
    for r in runs[1:]:
        assert r == runs[0]


# 15. Global random independence
def test_15_global_random_independence():
    import random
    system = VerdantFeedbackSystem(seed=1234)
    world = MockWorld()

    random.seed(1111)
    s1 = system.evaluate_ecological_signals(15.0, 10.0, 15.0, radius=16.0, world=world)

    random.seed(999999)
    system._temporal_cache.clear()
    s2 = system.evaluate_ecological_signals(15.0, 10.0, 15.0, radius=16.0, world=world)

    assert s1.grazing_pressure == s2.grazing_pressure
    assert s1.water_stress == s2.water_stress
    assert s1.drought_pressure == s2.drought_pressure


# 16. M6 compatibility
def test_16_m6_compatibility():
    system = VerdantFeedbackSystem(seed=42)
    world = MockWorld()
    signals = system.evaluate_ecological_signals(10.0, 10.0, 10.0, radius=16.0, world=world)

    assert hasattr(signals, 'vegetation_stress')
    assert hasattr(signals, 'vegetation_recovery')
    assert 0.0 <= signals.vegetation_stress <= 1.0


# 17. M7 compatibility
def test_17_m7_compatibility():
    system = VerdantFeedbackSystem(seed=42)
    world = MockWorld()
    signals = system.evaluate_ecological_signals(10.0, 10.0, 10.0, radius=16.0, world=world)

    assert hasattr(signals, 'habitat_pressure')
    assert 0.0 <= signals.habitat_pressure <= 1.0


# 18. M8 compatibility
def test_18_m8_compatibility():
    system = VerdantFeedbackSystem(seed=42)
    world = MockWorld()
    signals = system.evaluate_ecological_signals(10.0, 10.0, 10.0, radius=16.0, world=world)

    assert hasattr(signals, 'population_pressure')
    assert hasattr(signals, 'resource_pressure')
    assert 0.0 <= signals.population_pressure <= 1.0


# 19. Simulation manager integration
def test_19_simulation_manager_integration():
    world_state = VerdantWorldState()
    clock = VerdantSimulationClock(world_state)
    manager = VerdantSimulationManager(context={'world': MockWorld()})
    fb_sys = VerdantFeedbackSystem(world_state=world_state, clock=clock)

    assert manager.register(clock) is True
    assert manager.register(fb_sys) is True

    manager.initialize()
    assert fb_sys.initialized is True

    manager.update(delta_ticks=50)
    assert clock.elapsed_ticks == 50
    assert fb_sys.get_world_age_ticks() == 50


# 20. No circular update failure & public queries
def test_20_no_circular_update_and_queries():
    world = MockWorld()
    state = get_ecosystem_state(10.0, 10.0, 10.0, radius=16.0, world=world, seed=888)

    health = get_ecological_health(10.0, 10.0, 10.0, radius=16.0, world=world, seed=888)
    grazing = get_grazing_pressure(10.0, 10.0, 10.0, radius=16.0, world=world, seed=888)
    veg_stress = get_vegetation_stress(10.0, 10.0, 10.0, radius=16.0, world=world, seed=888)
    veg_rec = get_vegetation_recovery(10.0, 10.0, 10.0, radius=16.0, world=world, seed=888)
    hab_p = get_habitat_pressure(10.0, 10.0, 10.0, radius=16.0, world=world, seed=888)
    w_stress = get_water_stress(10.0, 10.0, 10.0, radius=16.0, world=world, seed=888)
    d_press = get_drought_pressure(10.0, 10.0, 10.0, radius=16.0, world=world, seed=888)
    pop_p = get_population_pressure(10.0, 10.0, 10.0, radius=16.0, world=world, seed=888)
    resp = get_adaptive_response(10.0, 10.0, 10.0, radius=16.0, world=world, seed=888)
    exp = explain_ecosystem(10.0, 10.0, 10.0, radius=16.0, world=world, seed=888)

    assert health == state.ecological_health
    assert grazing == state.grazing_pressure
    assert veg_stress == state.vegetation_stress
    assert veg_rec == state.vegetation_recovery
    assert hab_p == state.habitat_pressure
    assert w_stress == state.water_stress
    assert d_press == state.drought_pressure
    assert pop_p == state.population_pressure
    assert resp == state.adaptive_response
    assert "Ecosystem at" in exp
