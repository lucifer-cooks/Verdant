"""Deterministic Procedural Continental Sandbox World Generator for VERDANT.

Generates a continuous, non-island Minecraft-style sandbox survival world:
- Boundless continental generation (no radial island masks or forced ocean boundaries)
- Low-frequency continental noise: deep oceans, shallow seas, coastal shelves, large land masses, and offshore islands
- Biomes: Plains, Forests, Dense Forests, Deserts (with sand dunes), Swamps, Rivers, Lakes, Hills, Mountain Ranges, Valleys, and Alpine Snow
- Subterranean 3D procedural caves carved through stone strata
- Balanced mineral ores: Coal, Iron, Gold, Diamond
- Chunk-based deterministic vegetation decoration (eliminates 75,000-candidate global scanning)
- Shaded flora and zero orphan-item physics lag
- Full integration with VERDANT M2-M12 ecosystems and persistent seed architecture.
"""

from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Ensure World is loaded first to prevent Cython circular import
from mc.net.minecraft.game.level.World import World
from mc.net.minecraft.game.level.block.Blocks import blocks
from mc.net.minecraft.game.level.MobSpawner import MobSpawner
from mc.JavaUtils import Random, getMillis

from verdant.environment.seed import VerdantWorldSeed

_WORLD_SEEDS: Dict[int, int] = {}


def get_world_seed(world: Any) -> Optional[int]:
    """Retrieve persistent seed associated with a World instance."""
    if world is None:
        return None
    if id(world) in _WORLD_SEEDS:
        return _WORLD_SEEDS[id(world)]
    if hasattr(world, "verdant_state") and world.verdant_state is not None:
        return world.verdant_state.metadata.get("seed")
    return None


def set_world_seed(world: Any, seed: int) -> None:
    """Associate a persistent world seed with a World instance."""
    if world is None:
        return
    _WORLD_SEEDS[id(world)] = int(seed)
    if hasattr(world, "verdant_state") and world.verdant_state is not None:
        world.verdant_state.metadata["seed"] = int(seed)


@dataclass(frozen=True)
class OutworldGeographySample:
    """Geographic sample at world coordinate (x, z) for Outworld and parallel Inworld mapping."""

    x: float
    z: float
    is_land: bool
    continentalness: float
    elevation: float
    mountain_factor: float
    biome: str
    zone: str


class FastPerlin2D:
    """Deterministic, vectorized 2D Perlin noise generator in numpy."""

    def __init__(self, seed: int = 42) -> None:
        rng = np.random.default_rng(seed)
        p = np.arange(256, dtype=np.int32)
        rng.shuffle(p)
        self.perm = np.tile(p, 4)
        angles = 2.0 * np.pi * np.arange(16) / 16.0
        self.gx = np.cos(angles)
        self.gy = np.sin(angles)

    def sample(self, x: np.ndarray, z: np.ndarray) -> np.ndarray:
        """Sample 2D gradient noise over numpy arrays x and z."""
        xi = np.floor(x).astype(np.int32) & 255
        zi = np.floor(z).astype(np.int32) & 255
        xf = x - np.floor(x)
        zf = z - np.floor(z)

        # Smooth cubic fade curve
        u = xf * xf * xf * (xf * (xf * 6.0 - 15.0) + 10.0)
        v = zf * zf * zf * (zf * (zf * 6.0 - 15.0) + 10.0)

        p0 = self.perm[xi] + zi
        p1 = self.perm[xi + 1] + zi

        g00 = self.perm[p0] & 15
        g10 = self.perm[p1] & 15
        g01 = self.perm[p0 + 1] & 15
        g11 = self.perm[p1 + 1] & 15

        d00 = self.gx[g00] * xf + self.gy[g00] * zf
        d10 = self.gx[g10] * (xf - 1.0) + self.gy[g10] * zf
        d01 = self.gx[g01] * xf + self.gy[g01] * (zf - 1.0)
        d11 = self.gx[g11] * (xf - 1.0) + self.gy[g11] * (zf - 1.0)

        x0 = d00 * (1.0 - u) + d10 * u
        x1 = d01 * (1.0 - u) + d11 * u
        return (x0 * (1.0 - v) + x1 * v) * 1.4142


class VerdantOutworldGenerator:
    """Procedural generator for classic continental Minecraft-style sandbox worlds.

    NO island masks, NO radial boundaries, NO forced ocean edges.
    Features vast continents, oceans, biomes, mountain chains, caves, rivers, and ores.
    """

    DEFAULT_WIDTH: int = 512
    DEFAULT_DEPTH: int = 512
    DEFAULT_HEIGHT: int = 64
    SEA_LEVEL: int = 24
    GROUND_LEVEL: int = 22

    def __init__(self, gui_loading: Any = None, seed: Optional[int] = None) -> None:
        self._gui_loading = gui_loading
        self.seed = int(seed if seed is not None else 10842)

        # Deterministic continental and terrain noise generators
        self._p_continent = FastPerlin2D(seed=self.seed + 101)
        self._p_continent_detail = FastPerlin2D(seed=self.seed + 102)
        self._p_warp = FastPerlin2D(seed=self.seed + 202)
        self._p_warp_fine = FastPerlin2D(seed=self.seed + 203)
        self._p_lowland = FastPerlin2D(seed=self.seed + 303)
        self._p_hills = FastPerlin2D(seed=self.seed + 304)
        self._p_ridge_main = FastPerlin2D(seed=self.seed + 404)
        self._p_ridge_cross = FastPerlin2D(seed=self.seed + 505)
        self._p_valley = FastPerlin2D(seed=self.seed + 606)
        self._p_temperature = FastPerlin2D(seed=self.seed + 707)
        self._p_moisture = FastPerlin2D(seed=self.seed + 808)
        self._p_dune = FastPerlin2D(seed=self.seed + 809)
        self._p_river = FastPerlin2D(seed=self.seed + 810)
        self._p_cave1 = FastPerlin2D(seed=self.seed + 909)
        self._p_cave2 = FastPerlin2D(seed=self.seed + 910)

    def _display_progress(self, message: str) -> None:
        if self._gui_loading and hasattr(self._gui_loading, "displayProgressMessage"):
            try:
                self._gui_loading.displayProgressMessage(message)
            except Exception:
                pass

    def _display_string(self, message: str) -> None:
        if self._gui_loading and hasattr(self._gui_loading, "displayLoadingString"):
            try:
                self._gui_loading.displayLoadingString(message)
            except Exception:
                pass

    def sample_geography(self, x: float, z: float, width: int = 512, depth: int = 512, height: int = 64) -> OutworldGeographySample:
        """Sample geography at coordinate (x, z) for Outworld and parallel Inworld mapping."""
        sea_level = self.SEA_LEVEL if height == 64 else height // 2

        arr_x = np.array([x], dtype=np.float32)
        arr_z = np.array([z], dtype=np.float32)

        # 1. Continental Noise Layer (No radial formulas!)
        c_macro = float(self._p_continent.sample(arr_x * 0.0022, arr_z * 0.0022)[0])
        c_detail = float(self._p_continent_detail.sample(arr_x * 0.0055, arr_z * 0.0055)[0])
        w1 = float(self._p_warp.sample(arr_x * 0.004, arr_z * 0.004)[0]) * 0.15
        continentalness = c_macro * 0.75 + c_detail * 0.25 + w1

        # 2. Elevation based on continentalness
        lowland = (
            float(self._p_lowland.sample(arr_x * 0.008, arr_z * 0.008)[0]) * 4.5
            + float(self._p_hills.sample(arr_x * 0.018, arr_z * 0.018)[0]) * 2.5
        )

        # Mountains on high continental massifs
        m1 = max(0.0, min(1.0, 1.0 - abs(float(self._p_ridge_main.sample(arr_x * 0.0065, arr_z * 0.0065)[0]))))
        m2 = max(0.0, min(1.0, 1.0 - abs(float(self._p_ridge_cross.sample(arr_x * 0.008 + 1.2, arr_z * 0.008 - 0.8)[0]))))
        m_combined = max(m1, m2 * 0.88)

        highland_envelope = max(0.0, min(1.0, (continentalness - 0.08) * 3.5))
        v1 = max(0.0, min(1.0, (1.0 - abs(float(self._p_valley.sample(arr_x * 0.007, arr_z * 0.007)[0]))) * 2.0 - 0.3))
        mountain_relief = float(height - sea_level - 4)
        ridge_elevation = (m_combined ** 1.22) * (mountain_relief * 1.18) + highland_envelope * 5.0
        mountain_elevation = max(0.0, (ridge_elevation - v1 * 6.5) * highland_envelope)

        if continentalness < -0.05:
            # Ocean floor
            ocean_depth = 12.0 + float(self._p_lowland.sample(arr_x * 0.012, arr_z * 0.012)[0]) * 3.5
            t = max(0.0, min(1.0, (continentalness + 0.35) / 0.30))
            elevation = ocean_depth * (1.0 - t) + (sea_level - 1.0) * t
        else:
            # Continental land
            elevation = sea_level + 2.0 + lowland + mountain_elevation

        elevation = max(3.0, min(float(height - 3), elevation))
        is_land = elevation >= sea_level

        # Biome determination
        temp = float(self._p_temperature.sample(arr_x * 0.003, arr_z * 0.003)[0])
        moist = float(self._p_moisture.sample(arr_x * 0.003 + 500.0, arr_z * 0.003 + 500.0)[0])

        if not is_land:
            biome = "DEEP_OCEAN" if elevation < sea_level - 6.0 else "SHALLOW_OCEAN"
            zone = "OCEAN"
        elif elevation <= sea_level + 2.0:
            biome = "BEACH"
            zone = "COAST"
        elif elevation >= 54.0:
            biome = "ALPINE_SNOW"
            zone = "ALPINE_PEAK"
        elif elevation >= 44.0:
            biome = "MOUNTAIN"
            zone = "MOUNTAIN_RIDGE"
        elif moist < -0.18:
            biome = "DESERT"
            zone = "LOWLAND_PLAINS"
        elif moist > 0.35:
            biome = "DENSE_FOREST"
            zone = "LOWLAND_PLAINS"
        elif moist > 0.12:
            biome = "FOREST"
            zone = "LOWLAND_PLAINS"
        elif temp > 0.15 and moist > 0.0 and elevation <= sea_level + 5.0:
            biome = "SWAMP"
            zone = "LOWLAND_PLAINS"
        else:
            biome = "PLAINS"
            zone = "LOWLAND_PLAINS"

        return OutworldGeographySample(
            x=x,
            z=z,
            is_land=is_land,
            continentalness=continentalness,
            elevation=elevation,
            mountain_factor=highland_envelope,
            biome=biome,
            zone=zone,
        )

    def generate_heightfield(self, width: int = 512, depth: int = 512, height: int = 64) -> np.ndarray:
        """Compute the continuous 2D heightfield with procedural continents, oceans, and relief."""
        sea_level = self.SEA_LEVEL if height == 64 else height // 2

        x_coords = np.arange(width, dtype=np.float32)
        z_coords = np.arange(depth, dtype=np.float32)
        X, Z = np.meshgrid(x_coords, z_coords)

        # 1. Low-Frequency Continental Noise Layer (Vast landmasses and oceans)
        c_macro = self._p_continent.sample(X * 0.0022, Z * 0.0022)
        c_detail = self._p_continent_detail.sample(X * 0.0055, Z * 0.0055)
        w1 = self._p_warp.sample(X * 0.004, Z * 0.004) * 0.15
        w2 = self._p_warp_fine.sample(X * 0.008, Z * 0.008) * 0.08
        continentalness = c_macro * 0.72 + c_detail * 0.28 + w1 + w2

        # 2. Continental Shelf / Land-Water transition (Smooth step from shelf to ocean)
        # continentalness >= -0.02 is land; < -0.02 is ocean
        shelf_t = np.clip((continentalness - (-0.18)) / 0.20, 0.0, 1.0)
        shelf_t = shelf_t * shelf_t * (3.0 - 2.0 * shelf_t)

        # 3. Lowland rolling plains & hills
        lowland = (
            self._p_lowland.sample(X * 0.008, Z * 0.008) * 4.8
            + self._p_hills.sample(X * 0.018, Z * 0.018) * 2.6
        )

        # 4. Mountain Chains (Ridged multifractal spines across continental interiors)
        m_spine1 = np.clip(1.0 - np.abs(self._p_ridge_main.sample(X * 0.0065, Z * 0.0065)), 0.0, 1.0)
        m_spine2 = np.clip(1.0 - np.abs(self._p_ridge_cross.sample(X * 0.008 + 1.2, Z * 0.008 - 0.8)), 0.0, 1.0)
        m_combined = np.maximum(m_spine1, m_spine2 * 0.88)

        # Highland massifs form on thick continental crust
        highland_envelope = np.clip((continentalness - 0.06) * 3.5, 0.0, 1.0)

        # Valleys cutting through mountain ranges
        v1 = np.clip((1.0 - np.abs(self._p_valley.sample(X * 0.007, Z * 0.007))) * 2.0 - 0.3, 0.0, 1.0)
        valleys = v1

        # Mountain relief (reaches soaring peaks Y >= 58..61)
        max_mountain_relief = float(height - sea_level - 4)
        ridge_elevation = (m_combined ** 1.22) * (max_mountain_relief * 1.18) + highland_envelope * 5.0
        mountain_elevation = np.maximum(0.0, (ridge_elevation - valleys * 6.5) * highland_envelope)

        # 5. Sand dune ripples in desert zones
        moist = self._p_moisture.sample(X * 0.003 + 500.0, Z * 0.003 + 500.0)
        dune_intensity = np.clip((-moist - 0.18) * 4.0, 0.0, 1.0)
        dunes = (np.sin(X * 0.07 + Z * 0.04) * 1.5 + self._p_dune.sample(X * 0.03, Z * 0.03) * 1.2) * dune_intensity

        # 6. Combined land elevation
        land_elevation = sea_level + 2.0 + lowland + mountain_elevation + dunes

        # River channels cutting through lowlands to ocean
        r_val = np.abs(self._p_river.sample(X * 0.007, Z * 0.007))
        river_channel = np.clip((0.032 - r_val) / 0.032, 0.0, 1.0) * np.clip(1.0 - highland_envelope * 1.6, 0.0, 1.0)
        land_elevation -= river_channel * 5.5

        # 7. Ocean floor
        ocean_floor = 11.0 + self._p_lowland.sample(X * 0.012, Z * 0.012) * 3.8

        # 8. Continuous blended heightmap across continents and oceans
        heightmap = ocean_floor * (1.0 - shelf_t) + land_elevation * shelf_t
        heightmap = np.clip(np.round(heightmap), 3, height - 3).astype(np.int32)

        return heightmap

    def populate_voxels(self, heightmap: np.ndarray, width: int = 512, depth: int = 512, height: int = 64) -> bytearray:
        """Populate the 3D voxel grid: strata, biomes, sand dunes, caves, and ores."""
        sea_level = self.SEA_LEVEL if height == 64 else height // 2
        b_arr = np.zeros((height, depth, width), dtype=np.uint8)
        Y = np.arange(height, dtype=np.int32)[:, None, None]

        x_coords = np.arange(width, dtype=np.float32)
        z_coords = np.arange(depth, dtype=np.float32)
        X, Z = np.meshgrid(x_coords, z_coords)
        temp = self._p_temperature.sample(X * 0.003, Z * 0.003)
        moist = self._p_moisture.sample(X * 0.003 + 500.0, Z * 0.003 + 500.0)

        # 1. Bedrock floor (impermeable bottom)
        b_arr[0, :, :] = blocks.bedrock.blockID

        # 2. Ocean water column (up to sea_level)
        water_mask = (Y > heightmap) & (Y <= sea_level)
        b_arr[water_mask] = blocks.waterStill.blockID

        # 3. Subterranean solid stone
        stone_mask = (Y > 0) & (Y <= heightmap - 4)
        b_arr[stone_mask] = blocks.stone.blockID

        # 4. Biome identification masks
        is_desert = (moist < -0.18) & (heightmap >= sea_level + 2) & (heightmap < 44)
        is_beach = (heightmap >= sea_level - 1) & (heightmap <= sea_level + 2) & (~is_desert)
        is_swamp = (temp > 0.15) & (moist > 0.0) & (heightmap >= sea_level) & (heightmap <= sea_level + 4)
        is_alpine = (heightmap >= 48) | ((temp < 0.0) & (heightmap >= 40)) | ((temp < -0.15) & (heightmap >= 36))
        is_mountain = (heightmap >= 44) & (~is_alpine)

        # Subsurface dirt in temperate lowlands/swamps
        dirt_mask = (Y > heightmap - 4) & (Y <= heightmap) & (heightmap >= sea_level) & (heightmap < 44) & (~is_desert) & (~is_beach)
        b_arr[dirt_mask] = blocks.dirt.blockID

        # Subsurface sand in deserts and beaches
        sand_sub_mask = (Y > heightmap - 4) & (Y <= heightmap) & (is_desert | is_beach)
        b_arr[sand_sub_mask] = blocks.sand.blockID

        # 5. Surface layer
        # Grass on temperate plains, forests, and swamps
        grass_mask = (Y == heightmap) & (heightmap >= sea_level) & (heightmap < 44) & (~is_desert) & (~is_beach)
        b_arr[grass_mask] = blocks.grass.blockID

        # Sand on deserts and beaches
        sand_surf_mask = (Y == heightmap) & (is_desert | is_beach)
        b_arr[sand_surf_mask] = blocks.sand.blockID

        # 6. Mountain granite cliffs
        rock_mask = (Y >= heightmap - 3) & (Y <= heightmap) & is_mountain
        b_arr[rock_mask] = blocks.stone.blockID

        # 7. Alpine snow summits (clothWhite = 36) on cold high peaks
        snow_mask = (Y == heightmap) & is_alpine
        b_arr[snow_mask] = blocks.clothWhite.blockID

        deep_snow_mask = (Y == heightmap - 1) & is_alpine
        b_arr[deep_snow_mask] = blocks.clothWhite.blockID

        summit_snow_mask = (Y == heightmap - 2) & (is_alpine & (heightmap >= 46))
        b_arr[summit_snow_mask] = blocks.clothWhite.blockID

        # 8. Underwater ocean bed gravel
        ocean_bed_mask = (Y >= heightmap - 2) & (Y <= heightmap) & (heightmap < sea_level - 1)
        b_arr[ocean_bed_mask] = blocks.gravel.blockID

        # 9. Procedural subterranean 3D caves
        self._carve_caves(b_arr, X, Z, heightmap, width, depth, height)

        # 10. Mineral ore distribution
        self._populate_ores(b_arr, width, depth, height, sea_level)

        return bytearray(b_arr.tobytes())

    def _carve_caves(self, b_arr: np.ndarray, X: np.ndarray, Z: np.ndarray, heightmap: np.ndarray, width: int, depth: int, height: int) -> None:
        """Carve subterranean cavern systems into deep stone layers."""
        max_cave_y = min(36, height - 8)
        for y in range(6, max_cave_y, 3):
            c1 = self._p_cave1.sample(X * 0.024 + y * 0.04, Z * 0.024)
            c2 = self._p_cave2.sample(X * 0.024, Z * 0.024 + y * 0.04)
            cave_cross = (c1 * c1 + c2 * c2 < 0.016)
            for dy in range(3):
                cy = y + dy
                if cy < max_cave_y:
                    can_carve = (cy < heightmap - 4) & (b_arr[cy, :, :] == blocks.stone.blockID) & cave_cross
                    b_arr[cy, :, :][can_carve] = 0

    def _populate_ores(self, b_arr: np.ndarray, width: int, depth: int, height: int, sea_level: int) -> None:
        """Seed ore deposits into the stone layers across the world."""
        rng = np.random.default_rng(self.seed + 999)

        def _place_ore(ore_id: int, count: int, cluster_radius: int, max_y: int, min_y: int = 2) -> None:
            xs = rng.integers(3, width - 3, size=count)
            zs = rng.integers(3, depth - 3, size=count)
            ys = rng.integers(min_y, max(min_y + 1, max_y), size=count)
            for i in range(count):
                cx, cy, cz = int(xs[i]), int(ys[i]), int(zs[i])
                x0, x1 = max(0, cx - cluster_radius), min(width, cx + cluster_radius + 1)
                y0, y1 = max(1, cy - cluster_radius), min(height, cy + cluster_radius + 1)
                z0, z1 = max(0, cz - cluster_radius), min(depth, cz + cluster_radius + 1)
                sub = b_arr[y0:y1, z0:z1, x0:x1]
                mask = (sub == blocks.stone.blockID) & (rng.random(sub.shape) < 0.55)
                sub[mask] = ore_id

        _place_ore(blocks.oreCoal.blockID, count=1400, cluster_radius=2, max_y=height - 8, min_y=4)
        _place_ore(blocks.oreIron.blockID, count=1000, cluster_radius=2, max_y=int(sea_level * 1.4), min_y=4)
        _place_ore(blocks.oreGold.blockID, count=600, cluster_radius=1, max_y=int(sea_level * 0.85), min_y=3)
        _place_ore(blocks.oreDiamond.blockID, count=750, cluster_radius=1, max_y=int(sea_level * 0.55), min_y=2)

    def _populate_flora_chunk_based(self, world: World, heightmap: np.ndarray, width: int, depth: int, height: int) -> Tuple[int, int, int]:
        """Decorate vegetation chunk-by-chunk (16x16) rather than scanning the entire world.

        Runs in O(chunks) time, guarantees uniform natural density, and prevents daylight mushroom dropping.
        """
        sea_level = self.SEA_LEVEL if height == 64 else height // 2
        chunks_x = width // 16
        chunks_z = depth // 16

        trees_planted = 0
        flowers_planted = 0
        mushrooms_planted = 0

        for cz in range(chunks_z):
            for cx in range(chunks_x):
                # Deterministic chunk RNG
                chunk_seed = (self.seed + cx * 341873128712 + cz * 132897987541) & 0xFFFFFFFF
                rng = np.random.default_rng(chunk_seed)

                center_x = cx * 16 + 8
                center_z = cz * 16 + 8
                center_y = int(heightmap[center_z, center_x])

                # Ocean / deep water check
                if center_y < sea_level:
                    continue

                arr_x = np.array([float(center_x)], dtype=np.float32)
                arr_z = np.array([float(center_z)], dtype=np.float32)
                moist = float(self._p_moisture.sample(arr_x * 0.003 + 500.0, arr_z * 0.003 + 500.0)[0])

                # Biome tree quota
                if center_y >= 44:
                    num_trees = 1 if rng.random() < 0.25 else 0
                    num_flowers = 0
                elif moist < -0.18:
                    # Desert
                    num_trees = 0
                    num_flowers = 0
                elif moist > 0.35:
                    # Dense Forest
                    num_trees = int(rng.integers(18, 28))
                    num_flowers = int(rng.integers(6, 12))
                elif moist > 0.12:
                    # Standard Forest
                    num_trees = int(rng.integers(10, 18))
                    num_flowers = int(rng.integers(8, 16))
                else:
                    # Plains
                    num_trees = int(rng.integers(3, 7))
                    num_flowers = int(rng.integers(14, 26))

                chunk_x0 = cx * 16
                chunk_z0 = cz * 16
                grown_trees: List[Tuple[int, int, int]] = []

                # Plant trees with bounded retry attempts
                tree_attempts = 0
                max_tree_attempts = num_trees * 3
                trees_in_chunk = 0
                while trees_in_chunk < num_trees and tree_attempts < max_tree_attempts:
                    tree_attempts += 1
                    tx = chunk_x0 + int(rng.integers(1, 15))
                    tz = chunk_z0 + int(rng.integers(1, 15))
                    ty = int(heightmap[tz, tx])

                    if ty <= sea_level + 1 or ty >= 44:
                        continue
                    if world.getBlockId(tx, ty, tz) != blocks.grass.blockID:
                        continue
                    if world.getBlockId(tx, ty + 1, tz) != 0:
                        continue

                    if world.growTrees(tx, ty + 1, tz):
                        trees_planted += 1
                        trees_in_chunk += 1
                        grown_trees.append((tx, ty, tz))

                # Plant flowers with bounded retry attempts
                flower_attempts = 0
                max_flower_attempts = num_flowers * 3
                flowers_in_chunk = 0
                while flowers_in_chunk < num_flowers and flower_attempts < max_flower_attempts:
                    flower_attempts += 1
                    fx = chunk_x0 + int(rng.integers(1, 15))
                    fz = chunk_z0 + int(rng.integers(1, 15))
                    fy = int(heightmap[fz, fx])

                    if fy <= sea_level + 1 or fy >= 44:
                        continue
                    if world.getBlockId(fx, fy, fz) not in (blocks.grass.blockID, blocks.dirt.blockID):
                        continue
                    if world.getBlockId(fx, fy + 1, fz) != 0:
                        continue

                    f_id = blocks.plantYellow.blockID if rng.random() < 0.55 else blocks.plantRed.blockID
                    world.setBlock(fx, fy + 1, fz, f_id)
                    flowers_planted += 1
                    flowers_in_chunk += 1

                # Plant shaded mushrooms under tree canopies
                for tx, ty, tz in grown_trees:
                    for dx in (-1, 0, 1):
                        for dz in (-1, 0, 1):
                            if dx == 0 and dz == 0:
                                continue
                            mx = tx + dx
                            mz = tz + dz
                            if mx < 0 or mx >= width or mz < 0 or mz >= depth:
                                continue
                            my = int(heightmap[mz, mx])
                            if world.getBlockId(mx, my, mz) not in (blocks.grass.blockID, blocks.dirt.blockID):
                                continue
                            if world.getBlockId(mx, my + 1, mz) != 0:
                                continue

                            # Physical overhead leaf/wood canopy check
                            has_cover = any(
                                world.getBlockId(mx, my + 1 + dy, mz) in (blocks.leaves.blockID, blocks.wood.blockID)
                                for dy in range(1, 7)
                            )
                            if has_cover and rng.random() < 0.40:
                                m_id = blocks.mushroomBrown.blockID if rng.random() < 0.65 else blocks.mushroomRed.blockID
                                world.setBlock(mx, my + 1, mz, m_id)
                                mushrooms_planted += 1

        return trees_planted, flowers_planted, mushrooms_planted

    def find_safe_spawn(self, heightmap: np.ndarray, width: int = 512, depth: int = 512, height: int = 64) -> Tuple[int, int, int]:
        """Find a safe, pleasant continental starting location."""
        sea_level = self.SEA_LEVEL if height == 64 else height // 2
        rng = np.random.default_rng(self.seed + 777)

        cx = width // 2
        cz = depth // 2
        search_radius = width // 3

        best_spawn: Optional[Tuple[int, int, int]] = None
        best_score = float("-inf")

        for _ in range(1000):
            x = int(cx + rng.integers(-search_radius, search_radius))
            z = int(cz + rng.integers(-search_radius, search_radius))
            if x < 10 or x >= width - 10 or z < 10 or z >= depth - 10:
                continue
            h = int(heightmap[z, x])

            # Must be comfortably above water level on dry land
            if h < sea_level + 2 or h > sea_level + 12:
                continue

            # Local gradient: must be relatively flat
            sub = heightmap[max(0, z - 1): min(depth, z + 2), max(0, x - 1): min(width, x + 2)]
            if np.max(sub) - np.min(sub) > 1:
                continue

            dist_center = math.sqrt((x - cx) ** 2 + (z - cz) ** 2)
            score = 100.0 - dist_center * 0.1 - abs(h - (sea_level + 4)) * 2.5
            if score > best_score:
                best_score = score
                best_spawn = (x, h + 1, z)

        if best_spawn is None:
            # Fallback search for any walkable land
            for r in range(10, width // 2, 8):
                for angle in np.linspace(0, 2 * np.pi, 16):
                    fx = int(cx + r * np.cos(angle))
                    fz = int(cz + r * np.sin(angle))
                    if 0 <= fx < width and 0 <= fz < depth:
                        fh = int(heightmap[fz, fx])
                        if fh > sea_level + 1:
                            return (fx, fh + 1, fz)
            best_spawn = (cx, sea_level + 4, cz)

        return best_spawn

    def generate(self, user_name: Any = "anonymous", width: int = 512, depth: int = 512, height: int = 64) -> World:
        """Generate the complete authoritative World instance for the Outworld."""
        if isinstance(user_name, int):
            width, depth, height = user_name, width, depth
            user_name = "anonymous"

        self._display_progress("Generating Outworld Continent")

        sea_level = self.SEA_LEVEL if height == 64 else height // 2
        ground_level = self.GROUND_LEVEL if height == 64 else sea_level - 2

        # 1. Raising & shaping terrain
        self._display_string("Shaping continental terrain..")
        heightmap = self.generate_heightfield(width=width, depth=depth, height=height)

        # 2. Voxel block population
        self._display_string("Populating strata & biomes..")
        voxel_bytes = self.populate_voxels(heightmap, width=width, depth=depth, height=height)

        # 3. Create authoritative World instance
        self._display_string("Assembling world..")
        world = World()
        set_world_seed(world, self.seed)
        world.waterLevel = sea_level
        world.groundLevel = ground_level
        world.cloudHeight = height + 2
        world.skyColor = 0x99CCFF
        world.fogColor = 0xFFFFFF
        world.cloudColor = 0xFFFFFF
        world.createTime = getMillis()
        world.authorName = str(user_name)
        world.name = "Outworld"

        world.generate(width, height, depth, voxel_bytes, None)

        # 4. Safe spawn placement
        self._display_string("Selecting starting point..")
        sx, sy, sz = self.find_safe_spawn(heightmap, width=width, depth=depth, height=height)
        world.xSpawn = sx
        world.ySpawn = sy
        world.zSpawn = sz
        world.rotSpawn = 0.0

        # 5. Native flora population via chunk decorator
        self._display_string("Decorating vegetation..")
        self._populate_flora_chunk_based(world, heightmap, width, depth, height)

        # Clear comfortable 3x3 air clearing around spawn
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                for dy in range(0, 4):
                    world.setBlock(sx + dx, sy + dy, sz + dz, 0)

        # 6. Ecosystem integration (VERDANT M2-M12)
        try:
            from verdant.vegetation.system import VerdantVegetationSystem
            from verdant.world.state import VerdantWorldState

            world.verdant_state = getattr(world, "verdant_state", None)
            if world.verdant_state is None:
                world.verdant_state = VerdantWorldState(world=world)
                world.verdant_state.metadata["seed"] = self.seed

            vegetation_sys = VerdantVegetationSystem(world_state=world.verdant_state, seed=self.seed)
            vegetation_sys.apply_generation_population(world, max_candidates=1000, user_name=user_name, population_version=1)
            world.verdant_vegetation = vegetation_sys
        except Exception:
            pass

        # 7. World lighting calculation
        self._display_string("Calculating sunlight..")
        try:
            for _ in range(120):
                world.updateLighting()
        except Exception:
            pass

        # 8. Initial fauna spawning
        self._display_string("Settling creatures..")
        try:
            spawner = MobSpawner(world)
            for _ in range(80):
                spawner.performSpawning()
        except Exception:
            pass

        # 9. Clean up any orphan dropped items before handing world to player
        try:
            from mc.net.minecraft.game.entity.misc.EntityItem import EntityItem
            if hasattr(world, 'entityMap') and hasattr(world.entityMap, 'all'):
                for ent in list(world.entityMap.all):
                    if isinstance(ent, EntityItem):
                        ent.setEntityDead()
            world.updateEntities()
        except Exception:
            pass

        return world
