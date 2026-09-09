"""Data-driven vegetation suitability rules for M4."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class VerdantVegetationRule:
    """Environmental suitability profile for a biome."""

    biome: str
    tree_density: float = 0.0
    grass_density: float = 0.0
    flower_density: float = 0.0
    mushroom_density: float = 0.0
    moisture_suitability: float = 0.0
    temperature_suitability: float = 0.0
    altitude_suitability: float = 0.0
    preferred_types: tuple = ()


class VerdantVegetationRuleSet:
    """Centralized, data-driven vegetation rules for the initial VERDANT biomes."""

    RULES: Dict[str, VerdantVegetationRule] = {
        'Ocean': VerdantVegetationRule(
            biome='Ocean',
            tree_density=0.0,
            grass_density=0.0,
            flower_density=0.0,
            mushroom_density=0.0,
            moisture_suitability=1.0,
            temperature_suitability=0.4,
            altitude_suitability=0.2,
            preferred_types=('water',),
        ),
        'Plains': VerdantVegetationRule(
            biome='Plains',
            tree_density=0.25,
            grass_density=0.9,
            flower_density=0.8,
            mushroom_density=0.2,
            moisture_suitability=0.7,
            temperature_suitability=0.8,
            altitude_suitability=0.8,
            preferred_types=('grass', 'flower'),
        ),
        'Forest': VerdantVegetationRule(
            biome='Forest',
            tree_density=0.9,
            grass_density=0.8,
            flower_density=0.5,
            mushroom_density=0.5,
            moisture_suitability=0.9,
            temperature_suitability=0.8,
            altitude_suitability=0.7,
            preferred_types=('tree', 'grass', 'flower', 'mushroom'),
        ),
        'Desert': VerdantVegetationRule(
            biome='Desert',
            tree_density=0.0,
            grass_density=0.05,
            flower_density=0.02,
            mushroom_density=0.0,
            moisture_suitability=0.1,
            temperature_suitability=0.9,
            altitude_suitability=0.5,
            preferred_types=('cacti',),
        ),
        'Mountains': VerdantVegetationRule(
            biome='Mountains',
            tree_density=0.15,
            grass_density=0.35,
            flower_density=0.2,
            mushroom_density=0.15,
            moisture_suitability=0.5,
            temperature_suitability=0.5,
            altitude_suitability=0.9,
            preferred_types=('sparse_tree', 'grass'),
        ),
        'Snow/Tundra': VerdantVegetationRule(
            biome='Snow/Tundra',
            tree_density=0.05,
            grass_density=0.1,
            flower_density=0.05,
            mushroom_density=0.08,
            moisture_suitability=0.4,
            temperature_suitability=0.2,
            altitude_suitability=0.7,
            preferred_types=('scrub', 'lichen'),
        ),
        'Swamp': VerdantVegetationRule(
            biome='Swamp',
            tree_density=0.6,
            grass_density=0.7,
            flower_density=0.3,
            mushroom_density=0.9,
            moisture_suitability=1.0,
            temperature_suitability=0.7,
            altitude_suitability=0.5,
            preferred_types=('mushroom', 'reeds', 'tree'),
        ),
    }

    def __init__(self):
        self.rule_index = dict(self.RULES)

    def get_rules(self, biome_name: str):
        return self.rule_index.get(str(biome_name), self.rule_index['Plains'])

    def get_tree_density(self, environment):
        rule = self.get_rules(getattr(environment, 'biome_name', 'Plains'))
        return rule.tree_density

    def get_grass_density(self, environment):
        rule = self.get_rules(getattr(environment, 'biome_name', 'Plains'))
        return rule.grass_density

    def get_flower_density(self, environment):
        rule = self.get_rules(getattr(environment, 'biome_name', 'Plains'))
        return rule.flower_density

    def get_mushroom_density(self, environment):
        rule = self.get_rules(getattr(environment, 'biome_name', 'Plains'))
        return rule.mushroom_density

    def is_suitable(self, environment, vegetation_type: str):
        biome_name = getattr(environment, 'biome_name', 'Plains')
        rule = self.get_rules(biome_name)
        lookup = {
            'tree': rule.tree_density,
            'grass': rule.grass_density,
            'flower': rule.flower_density,
            'mushroom': rule.mushroom_density,
        }
        return lookup.get(vegetation_type, 0.0) > 0.0

    def list_biomes(self):
        return tuple(self.rule_index.keys())
