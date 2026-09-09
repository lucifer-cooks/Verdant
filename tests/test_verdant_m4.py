import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verdant.environment.biome import VerdantBiomeResolver
from verdant.environment.climate import VerdantClimateSystem
from verdant.environment.seed import VerdantWorldSeed
from verdant.vegetation.rules import VerdantVegetationRuleSet
from verdant.vegetation.system import VerdantVegetationSystem
from verdant.world.state import VerdantWorldState


def test_vegetation_rules_exist_for_every_initial_biome():
    rules = VerdantVegetationRuleSet()
    for biome_name in ['Ocean', 'Plains', 'Forest', 'Desert', 'Mountains', 'Snow/Tundra', 'Swamp']:
        assert biome_name in rules.rule_index
        assert rules.get_rules(biome_name).biome == biome_name


def test_seeded_vegetation_is_deterministic():
    system_a = VerdantVegetationSystem(world_state=VerdantWorldState())
    system_a.seed = 123
    system_a.seed_source = VerdantWorldSeed(123)

    system_b = VerdantVegetationSystem(world_state=VerdantWorldState())
    system_b.seed = 123
    system_b.seed_source = VerdantWorldSeed(123)

    env_a = system_a.get_environment_for(8, 10, 12)
    env_b = system_b.get_environment_for(8, 10, 12)
    assert env_a.temperature == env_b.temperature
    assert env_a.humidity == env_b.humidity
    assert env_a.rainfall == env_b.rainfall


def test_different_coordinates_produce_different_deterministic_decisions():
    system = VerdantVegetationSystem(world_state=VerdantWorldState())
    system.seed = 55
    system.seed_source = VerdantWorldSeed(55)

    env_a = system.get_environment_for(1, 20, 1)
    env_b = system.get_environment_for(12, 20, 12)
    assert env_a != env_b


def test_forest_has_greater_tree_suitability_than_desert():
    forest_env = VerdantClimateSystem(world_state=VerdantWorldState(current_season='spring')).get_environment(20, 15, 20)
    desert_env = VerdantClimateSystem(world_state=VerdantWorldState(current_season='summer')).get_environment(10, 5, 10)
    forest_biome = VerdantBiomeResolver().resolve(forest_env)
    desert_biome = VerdantBiomeResolver().resolve(desert_env)

    forest_rules = VerdantVegetationRuleSet().get_rules(forest_biome.name)
    desert_rules = VerdantVegetationRuleSet().get_rules(desert_biome.name)
    assert forest_rules.tree_density > desert_rules.tree_density


def test_plains_have_strong_grass_suitability():
    rules = VerdantVegetationRuleSet().get_rules('Plains')
    assert rules.grass_density >= 0.7


def test_desert_has_very_low_normal_vegetation_suitability():
    rules = VerdantVegetationRuleSet().get_rules('Desert')
    assert rules.grass_density < 0.1
    assert rules.tree_density == 0.0


def test_swamp_is_moisture_favorable():
    rules = VerdantVegetationRuleSet().get_rules('Swamp')
    assert rules.mushroom_density > 0.8
    assert rules.moisture_suitability >= 0.9


def test_snow_tundra_has_low_vegetation_suitability():
    rules = VerdantVegetationRuleSet().get_rules('Snow/Tundra')
    assert rules.tree_density < 0.1
    assert rules.grass_density < 0.2


def test_vegetation_rules_response_to_environment_inputs():
    system = VerdantVegetationSystem(world_state=VerdantWorldState())
    env = system.get_environment_for(6, 8, 9)
    assert system.is_vegetation_suitable(env, 'grass') in (True, False)
    assert system.get_tree_density(env) >= 0.0
    assert system.get_grass_density(env) >= 0.0
    assert system.get_flower_density(env) >= 0.0
    assert system.get_mushroom_density(env) >= 0.0


def test_indev_vegetation_apis_remain_usable():
    from mc.net.minecraft.game.level.block.Blocks import blocks
    assert blocks.plantYellow is not None
    assert blocks.plantRed is not None
    assert blocks.mushroomBrown is not None
    assert blocks.mushroomRed is not None
    assert blocks.sapling is not None
