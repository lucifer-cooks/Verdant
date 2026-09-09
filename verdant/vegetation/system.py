"""Deterministic vegetation population bridge for VERDANT."""

from __future__ import annotations

import hashlib
from typing import Optional

from verdant.environment.biome import VerdantBiomeResolver
from verdant.environment.climate import VerdantClimateSystem
from verdant.environment.seed import VerdantWorldSeed
from verdant.simulation.system import VerdantSystem
from verdant.vegetation.rules import VerdantVegetationRuleSet


def _get_legacy_blocks():
    """Resolve the legacy blocks registry lazily to avoid import cycles.

    Importing this registry at module import time triggers the game's Cython
    dependency graph before the world classes are initialized. The registry is
    therefore deferred until the actual vegetation placement logic needs it.
    """
    from mc.net.minecraft.game.level.block.Blocks import blocks
    return blocks


def build_generation_seed(world=None, *, user_name: str = 'anonymous', width: int = 0,
                         depth: int = 0, height: int = 0, level_type: int = 0,
                         population_version: int = 1):
    """Return a stable, deterministic seed for vegetation generation.

    The legacy engine does not expose a user-provided world seed, so we derive a
    reproducible seed from the generation inputs instead of using global random
    state. The same world configuration will therefore resolve the same plant
    density decisions for the same coordinates.
    """
    seed_text = (
        f"verdant-vegetation|{user_name}|{width}|{depth}|{height}|{level_type}|"
        f"{population_version}|{getattr(world, 'name', '')}"
    )
    digest = hashlib.sha256(seed_text.encode('utf-8')).hexdigest()
    return int(digest[:16], 16) % (2 ** 31 - 1)


class VerdantVegetationSystem(VerdantSystem):
    """Vegetation decision layer for the existing Indev world.

    This does not replace the legacy vegetation engine. It decides which
    vegetation is suitable for a local environment and then delegates placement to
    the known-good Indev mechanisms such as world.growTrees and block placement.
    """

    def __init__(self, world_state=None, *, name='verdant_vegetation', seed: Optional[int] = None):
        super().__init__(name=name)
        self.world_state = world_state
        self.seed = int(seed if seed is not None else (world_state.metadata.get('seed', 0) if world_state else 0))
        self.seed_source = VerdantWorldSeed(self.seed)
        self.rules = VerdantVegetationRuleSet()
        self.biome_resolver = VerdantBiomeResolver()
        self.climate_system = VerdantClimateSystem(world_state=world_state, seed=self.seed)

    def initialize(self, context=None):
        if context and 'world' in context:
            self.world_state = getattr(context.get('world'), 'verdant_state', self.world_state)
        if self.world_state is not None:
            self.seed = int(self.world_state.metadata.get('seed', self.seed))
            self.seed_source = VerdantWorldSeed(self.seed)
            self.climate_system = VerdantClimateSystem(world_state=self.world_state, seed=self.seed)
        self.initialized = True
        return self

    def get_vegetation_rules(self, biome):
        return self.rules.get_rules(biome)

    def get_tree_density(self, environment):
        return self.rules.get_tree_density(environment)

    def get_grass_density(self, environment):
        return self.rules.get_grass_density(environment)

    def get_flower_density(self, environment):
        return self.rules.get_flower_density(environment)

    def get_mushroom_density(self, environment):
        return self.rules.get_mushroom_density(environment)

    def is_vegetation_suitable(self, environment, vegetation_type: str):
        return self.rules.is_suitable(environment, vegetation_type)

    def get_environment_for(self, x: int, y: int, z: int):
        return self.climate_system.get_environment(x, y, z)

    def populate_world(self, world, *, max_candidates: int = 250):
        if world is None:
            return 0

        blocks = _get_legacy_blocks()
        width = getattr(world, 'width', 32)
        depth = getattr(world, 'length', 32)
        height = getattr(world, 'height', 64)
        ground_level = getattr(world, 'groundLevel', 32)

        candidates = 0
        step = max(2, min(12, max(4, width // 12)))

        for x in range(0, width, step):
            for z in range(0, depth, step):
                if candidates >= max_candidates:
                    return candidates

                surface_y = max(1, min(height - 2, ground_level + 1))
                base = world.getBlockId(x, surface_y, z)
                if base != 0:
                    continue

                env = self.get_environment_for(x, surface_y, z)
                biome = self.biome_resolver.resolve(env)
                rule = self.rules.get_rules(biome.name)

                below = world.getBlockId(x, surface_y - 1, z)
                if below not in (blocks.grass.blockID, blocks.dirt.blockID, blocks.sand.blockID):
                    continue

                if rule.tree_density > 0.0:
                    seeded = abs(self.seed_source.noise(x + 13, surface_y + 7, z + 21))
                    if seeded < rule.tree_density * 0.24 and world.getBlockId(x, surface_y, z) == 0:
                        if world.growTrees(x, surface_y, z):
                            candidates += 1
                            continue

                if rule.grass_density > 0.0:
                    seeded = abs(self.seed_source.noise(x + 31, surface_y + 11, z + 17))
                    if seeded < rule.grass_density * 0.3:
                        world.setBlockWithNotify(x, surface_y, z, blocks.grass.blockID)
                        candidates += 1
                        continue

                if rule.flower_density > 0.0:
                    seeded = abs(self.seed_source.noise(x + 41, surface_y + 13, z + 9))
                    if seeded < rule.flower_density * 0.22:
                        flower_id = blocks.plantYellow.blockID if seeded > 0.5 else blocks.plantRed.blockID
                        world.setBlockWithNotify(x, surface_y, z, flower_id)
                        candidates += 1
                        continue

                if rule.mushroom_density > 0.0 and below in (blocks.grass.blockID, blocks.dirt.blockID):
                    seeded = abs(self.seed_source.noise(x + 53, surface_y + 19, z + 27))
                    if seeded < rule.mushroom_density * 0.18:
                        mushroom_id = blocks.mushroomBrown.blockID if seeded > 0.5 else blocks.mushroomRed.blockID
                        world.setBlockWithNotify(x, surface_y, z, mushroom_id)
                        candidates += 1

        return candidates

    def apply_generation_population(self, world, *, max_candidates: int = 250,
                                   user_name: str = 'anonymous',
                                   population_version: int = 1):
        """Minimal generation-time vegetation hook for the legacy population stage.

        This intentionally runs once during world generation and only evaluates the
        local terrain that would normally be populated by the legacy generator. The
        vegetation system decides whether a biome should have trees, grass, or
        mushrooms, while the existing Indev APIs remain responsible for the actual
        placement checks and renderable block state.
        """
        if world is None:
            return 0

        width = getattr(world, 'width', 32)
        depth = getattr(world, 'length', 32)
        height = getattr(world, 'height', 64)
        seed = build_generation_seed(
            world=world,
            user_name=user_name,
            width=width,
            depth=depth,
            height=height,
            level_type=getattr(world, 'levelType', 0),
            population_version=population_version,
        )

        self.seed = seed
        self.seed_source = VerdantWorldSeed(seed)
        self.world_state = getattr(world, 'verdant_state', self.world_state)
        if self.world_state is None:
            from verdant.world.state import VerdantWorldState
            self.world_state = VerdantWorldState(world=world)
            self.world_state.metadata['seed'] = seed
            self.world_state.metadata['population_version'] = population_version
            world.verdant_state = self.world_state
        else:
            self.world_state.bind_world(world)
            self.world_state.metadata['seed'] = seed
            self.world_state.metadata['population_version'] = population_version

        self.climate_system = VerdantClimateSystem(world_state=self.world_state, seed=self.seed)
        self.biome_resolver = VerdantBiomeResolver()
        self.rules = VerdantVegetationRuleSet()
        self.initialized = True

        return self.populate_world(world, max_candidates=max_candidates)

    def update(self, context=None, delta_ticks: int = 1):
        return self
