"""
Biome Generator for Minecraft Python
Adds biome variety to world generation
"""
import random
import math


class BiomeGenerator:
    """Generates different biomes with varied terrain and features"""
    
    BIOME_PLAINS = 0
    BIOME_FOREST = 1
    BIOME_DESERT = 2
    BIOME_MOUNTAINS = 3
    BIOME_SWAMP = 4
    BIOME_TUNDRA = 5
    BIOME_JUNGLE = 6
    BIOME_OCEAN = 7
    
    BIOME_NAMES = {
        BIOME_PLAINS: "Plains",
        BIOME_FOREST: "Forest", 
        BIOME_DESERT: "Desert",
        BIOME_MOUNTAINS: "Mountains",
        BIOME_SWAMP: "Swamp",
        BIOME_TUNDRA: "Tundra",
        BIOME_JUNGLE: "Jungle",
        BIOME_OCEAN: "Ocean"
    }
    
    def __init__(self, seed):
        self.seed = seed
        self.random = random.Random(seed)
        
    def get_biome_at(self, x, z):
        """Get biome type at given coordinates using noise-like generation"""
        # Simple coordinate-based biome selection with seed
        combined = (x * 374761393 + z * 668265263) ^ self.seed
        hash_val = combined * (combined * combined * 15731 + 789221) + 1376312589
        biome_value = (hash_val >> 16) & 0x7FFF
        
        # Weighted biome selection
        if biome_value < 2000:
            return self.BIOME_OCEAN
        elif biome_value < 5000:
            return self.BIOME_TUNDRA
        elif biome_value < 9000:
            return self.BIOME_PLAINS
        elif biome_value < 13000:
            return self.BIOME_FOREST
        elif biome_value < 16000:
            return self.BIOME_DESERT
        elif biome_value < 19000:
            return self.BIOME_MOUNTAINS
        elif biome_value < 22000:
            return self.BIOME_SWAMP
        else:
            return self.BIOME_JUNGLE
    
    def get_biome_height_modifier(self, biome):
        """Get height modifier for biome"""
        modifiers = {
            self.BIOME_PLAINS: 0.0,
            self.BIOME_FOREST: 2.0,
            self.BIOME_DESERT: -1.0,
            self.BIOME_MOUNTAINS: 8.0,
            self.BIOME_SWAMP: -2.0,
            self.BIOME_TUNDRA: 1.0,
            self.BIOME_JUNGLE: 3.0,
            self.BIOME_OCEAN: -15.0
        }
        return modifiers.get(biome, 0.0)
    
    def get_biome_tree_density(self, biome):
        """Get tree density for biome (0.0 to 1.0)"""
        densities = {
            self.BIOME_PLAINS: 0.05,
            self.BIOME_FOREST: 0.8,
            self.BIOME_DESERT: 0.0,
            self.BIOME_MOUNTAINS: 0.1,
            self.BIOME_SWAMP: 0.3,
            self.BIOME_TUNDRA: 0.02,
            self.BIOME_JUNGLE: 0.9,
            self.BIOME_OCEAN: 0.0
        }
        return densities.get(biome, 0.0)
    
    def get_biome_grass_color(self, biome):
        """Get grass color for biome"""
        colors = {
            self.BIOME_PLAINS: 0x7CBA4F,
            self.BIOME_FOREST: 0x5B8F36,
            self.BIOME_DESERT: 0xAEA358,
            self.BIOME_MOUNTAINS: 0x8DB360,
            self.BIOME_SWAMP: 0x6A7049,
            self.BIOME_TUNDRA: 0x8DB360,
            self.BIOME_JUNGLE: 0x548B4A,
            self.BIOME_OCEAN: 0x7CBA4F
        }
        return colors.get(biome, 0x7CBA4F)
    
    def should_generate_caves(self, biome):
        """Whether caves should generate in this biome"""
        return biome not in [self.BIOME_OCEAN]
    
    def get_water_level_modifier(self, biome):
        """Get water level modifier for biome"""
        if biome == self.BIOME_OCEAN:
            return 10
        elif biome == self.BIOME_SWAMP:
            return 2
        return 0