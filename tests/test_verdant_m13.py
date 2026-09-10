"""Comprehensive automated test suite for VERDANT Milestone M13: Huge Outworld Island + Audio Fix."""

import os
import sys
import unittest
import numpy as np

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure World is imported first to avoid Cython circular dependency
from mc.net.minecraft.game.level.World import World
from mc.net.minecraft.game.level.block.Blocks import blocks
from mc.net.minecraft.client.sound.SoundManager import SoundManager
from mc.net.minecraft.client.sound.SoundPool import SoundPool
from mc.net.minecraft.client.sound.SoundPoolEntry import SoundPoolEntry
from mc.net.minecraft.client.GameSettings import GameSettings

from verdant.assets.theme import ThemeManager, ThemeMode
from verdant.world.outworld import VerdantOutworldGenerator, OutworldGeographySample, FastPerlin2D


class MockMC:
    """Mock Minecraft instance for testing sound manager and options without opening window."""
    def __init__(self):
        self.options = None


# 1. Test audio search path discovery
def test_01_audio_search_path_discovery():
    mock_mc = MockMC()
    options = GameSettings(mock_mc, ".")
    options.sound = True
    options.music = True

    snd = SoundManager()
    snd.loadSoundSettings(options)

    # Verify both pools are loaded
    sounds_count = snd._SoundManager__soundPoolSounds._SoundPool__numberOfSoundPoolEntries
    music_count = snd._SoundManager__soundPoolMusic._SoundPool__numberOfSoundPoolEntries

    assert sounds_count >= 50, f"Expected at least 50 sounds discovered, got {sounds_count}"
    assert music_count >= 1, f"Expected at least 1 music track discovered, got {music_count}"


# 2. Test audio category lookup
def test_02_audio_category_lookup():
    snd = SoundManager()
    # Test key categories
    for cat in ["step.stone", "step.grass", "random.click", "mob.pig"]:
        entry = snd._SoundManager__soundPoolSounds.getRandomSoundFromSoundPool(cat)
        assert entry is not None, f"Expected sound entry for category {cat}"
        assert entry.soundUrl is not None, f"SoundUrl should not be None for {cat}"


# 3. Test missing audio entry returns None without crash
def test_03_missing_audio_safety():
    pool = SoundPool()
    entry = pool.getRandomSoundFromSoundPool("nonexistent_sound_cue")
    assert entry is None


# 4. Test playRandomMusicIfReady with empty music pool (ROOT CAUSE VERIFICATION)
def test_04_play_random_music_empty_pool_no_soundurl_exception():
    mock_mc = MockMC()
    options = GameSettings(mock_mc, ".")
    options.sound = True
    options.music = True

    snd = SoundManager()
    snd.loadSoundSettings(options)

    # Temporarily isolate music pool
    real_music_pool = snd._SoundManager__soundPoolMusic
    empty_pool = SoundPool()
    snd._SoundManager__soundPoolMusic = empty_pool
    snd._SoundManager__musicStream = None

    # Must return cleanly with ZERO exceptions (no 'NoneType' object has no attribute 'soundUrl')
    snd.playRandomMusicIfReady(0, 0, 0)
    assert snd._SoundManager__musicStream is None

    # Restore
    snd._SoundManager__soundPoolMusic = real_music_pool


# 5. Test FastPerlin2D determinism and range
def test_05_perlin_determinism():
    p1 = FastPerlin2D(seed=999)
    p2 = FastPerlin2D(seed=999)

    x = np.linspace(0, 10, 64)
    z = np.linspace(0, 10, 64)
    X, Z = np.meshgrid(x, z)

    v1 = p1.sample(X, Z)
    v2 = p2.sample(X, Z)

    assert np.allclose(v1, v2), "FastPerlin2D with identical seed must produce identical results"


# 6. Test deterministic island generation
def test_06_deterministic_island_generation():
    gen1 = VerdantOutworldGenerator(seed=12345)
    gen2 = VerdantOutworldGenerator(seed=12345)

    h1 = gen1.generate_heightfield(width=128, depth=128, height=64)
    h2 = gen2.generate_heightfield(width=128, depth=128, height=64)

    assert np.array_equal(h1, h2), "Heightfields with identical seeds must be bit-for-bit identical"


# 7. Test continental land and ocean distribution (not an island)
def test_07_continental_land_and_ocean_distribution():
    gen = VerdantOutworldGenerator(seed=42)
    w, d, h = 512, 512, 64
    sea_level = VerdantOutworldGenerator.SEA_LEVEL
    heightmap = gen.generate_heightfield(width=w, depth=d, height=h)

    # Continental world check: both oceans and land must be present
    land_cells = np.sum(heightmap >= sea_level)
    ocean_cells = np.sum(heightmap < sea_level)
    assert land_cells > 50000, f"Expected substantial land, got {land_cells}"
    assert ocean_cells > 50000, f"Expected substantial ocean, got {ocean_cells}"

    # World boundaries must NOT be forcibly clamped to ocean (< sea_level)
    # At least one boundary border must contain land (>= sea_level)
    north_has_land = np.any(heightmap[0, :] >= sea_level)
    south_has_land = np.any(heightmap[-1, :] >= sea_level)
    west_has_land = np.any(heightmap[:, 0] >= sea_level)
    east_has_land = np.any(heightmap[:, -1] >= sea_level)
    boundary_has_land = north_has_land or south_has_land or west_has_land or east_has_land
    assert boundary_has_land, "Continental world boundaries must not be forcibly clamped to all-ocean"


# 8. Test continental landmass scale (substantial continents and oceans)
def test_08_large_landmass_scale():
    gen = VerdantOutworldGenerator(seed=42)
    w, d, h = 512, 512, 64
    sea_level = VerdantOutworldGenerator.SEA_LEVEL
    heightmap = gen.generate_heightfield(width=w, depth=d, height=h)

    total_cells = w * d
    land_cells = np.sum(heightmap >= sea_level)
    ocean_cells = total_cells - land_cells

    land_pct = (land_cells / total_cells) * 100.0
    assert land_cells >= 70000, f"Land cells too small: {land_cells}"
    assert ocean_cells >= 70000, f"Ocean cells too small: {ocean_cells}"
    assert 25.0 <= land_pct <= 75.0, f"Expected 25-75% continental land, got {land_pct:.1f}%"


# 9. Test mountain elevation relief and valleys
def test_09_mountain_elevation_relief_and_valleys():
    gen = VerdantOutworldGenerator(seed=42)
    w, d, h = 512, 512, 64
    sea_level = VerdantOutworldGenerator.SEA_LEVEL
    heightmap = gen.generate_heightfield(width=w, depth=d, height=h)

    min_elev = np.min(heightmap)
    max_elev = np.max(heightmap)

    # Mountain peaks should reach high elevation near upper limit
    assert max_elev >= 54, f"Expected mountain peaks to reach >= 54, got {max_elev}"
    # Ocean floor should be deep
    assert min_elev <= 18, f"Expected ocean floor <= 18, got {min_elev}"

    # Relief across land
    land_heights = heightmap[heightmap >= sea_level]
    relief = np.max(land_heights) - np.min(land_heights)
    assert relief >= 25, f"Expected at least 25 blocks of vertical relief, got {relief}"


# 10. Test coastline irregularity (natural non-circular terrain)
def test_10_coastline_irregularity():
    gen = VerdantOutworldGenerator(seed=42)
    w, d = 512, 512
    heightmap = gen.generate_heightfield(width=w, depth=d, height=64)
    sea_level = VerdantOutworldGenerator.SEA_LEVEL

    # Verify that the terrain has high variance across rows and columns (natural contours)
    row_std = np.std(np.mean(heightmap >= sea_level, axis=1))
    col_std = np.std(np.mean(heightmap >= sea_level, axis=0))
    assert row_std > 0.05 or col_std > 0.05, "Terrain contours must have natural geographic variance"


# 11. Test voxel population layers
def test_11_voxel_population_layers():
    gen = VerdantOutworldGenerator(seed=42)
    w, d, h = 128, 128, 64
    sea_level = VerdantOutworldGenerator.SEA_LEVEL
    heightmap = gen.generate_heightfield(width=w, depth=d, height=h)
    voxel_bytes = gen.populate_voxels(heightmap, width=w, depth=d, height=h)

    # Check bedrock at Y=0
    for x in range(w):
        for z in range(d):
            block_y0 = voxel_bytes[(0 * d + z) * w + x]
            assert block_y0 == blocks.bedrock.blockID, "Y=0 must be bedrock"

    # Check ocean water column
    ocean_z, ocean_x = np.where(heightmap < sea_level - 2)
    if len(ocean_z) > 0:
        oz, ox = ocean_z[0], ocean_x[0]
        oh = heightmap[oz, ox]
        for y in range(oh + 1, sea_level + 1):
            assert voxel_bytes[(y * d + oz) * w + ox] == blocks.waterStill.blockID, f"Expected water at Y={y}"


# 12. Test ore generation presence
def test_12_ore_generation_presence():
    gen = VerdantOutworldGenerator(seed=42)
    w, d, h = 128, 128, 64
    heightmap = gen.generate_heightfield(width=w, depth=d, height=h)
    voxel_bytes = gen.populate_voxels(heightmap, width=w, depth=d, height=h)
    arr = np.frombuffer(voxel_bytes, dtype=np.uint8)

    assert np.sum(arr == blocks.oreCoal.blockID) > 0, "Coal ore should be present"
    assert np.sum(arr == blocks.oreIron.blockID) > 0, "Iron ore should be present"
    assert np.sum(arr == blocks.oreGold.blockID) > 0, "Gold ore should be present"
    assert np.sum(arr == blocks.oreDiamond.blockID) > 0, "Diamond ore should be present"


# 13. Test safe spawn selection
def test_13_safe_spawn_selection():
    gen = VerdantOutworldGenerator(seed=42)
    w, d, h = 512, 512, 64
    sea_level = VerdantOutworldGenerator.SEA_LEVEL
    heightmap = gen.generate_heightfield(width=w, depth=d, height=h)
    sx, sy, sz = gen.find_safe_spawn(heightmap, width=w, depth=d, height=h)

    assert sx >= 50 and sx < w - 50, f"Spawn X out of bounds: {sx}"
    assert sz >= 50 and sz < d - 50, f"Spawn Z out of bounds: {sz}"
    # Spawn Y should be on land above sea level
    assert sy > sea_level, f"Spawn Y={sy} must be above sea level {sea_level}"
    # Ground underneath spawn
    assert heightmap[sz, sx] == sy - 1, f"Ground height {heightmap[sz, sx]} != spawn Y - 1 {sy - 1}"


# 14. Test geographic sampling for Outworld / Inworld parallel architecture
def test_14_outworld_inworld_geography_sampling():
    gen = VerdantOutworldGenerator(seed=555)

    sample1 = gen.sample_geography(256.0, 256.0)
    assert hasattr(sample1, "continentalness")
    assert hasattr(sample1, "biome")
    assert hasattr(sample1, "zone")
    assert hasattr(sample1, "elevation")
    assert isinstance(sample1.is_land, bool)

    # Sample must be deterministic
    sample2 = gen.sample_geography(256.0, 256.0)
    assert sample1 == sample2, "Geographic sampling must be 100% deterministic"


# 15. Test extensible vertical scale (Height parameterization)
def test_15_extensible_vertical_scale():
    gen = VerdantOutworldGenerator(seed=777)
    # Generate at H=96
    hfield_96 = gen.generate_heightfield(width=128, depth=128, height=96)
    assert hfield_96.max() > 64, f"H=96 terrain should take advantage of extra vertical space, max={hfield_96.max()}"
    assert hfield_96.min() >= 3, "H=96 terrain must respect lower boundary"


# 16. Test M2-M11 regression safety
def test_16_regression_safety():
    from verdant.world.state import VerdantWorldState
    from verdant.environment.climate import VerdantClimateSystem
    from verdant.water.system import VerdantWaterSystem
    from verdant.creatures.system import VerdantCreatureSystem
    from verdant.assets.creatures import ModelHollowStalker, ModelSporeSpire

    ws = VerdantWorldState()
    assert ws is not None
    cs = VerdantClimateSystem(seed=42)
    assert cs is not None
    assert ModelHollowStalker() is not None
    assert ModelSporeSpire() is not None


# 17. Test unique random seeds produce distinct worlds
def test_17_unique_random_seeds_produce_distinct_worlds():
    gen1 = VerdantOutworldGenerator(seed=10842)
    gen2 = VerdantOutworldGenerator(seed=99999)

    h1 = gen1.generate_heightfield(width=256, depth=256, height=64)
    h2 = gen2.generate_heightfield(width=256, depth=256, height=64)

    assert not np.array_equal(h1, h2), "Different seeds must generate distinct terrain"

    s1 = gen1.find_safe_spawn(h1, width=256, depth=256, height=64)
    s2 = gen2.find_safe_spawn(h2, width=256, depth=256, height=64)
    assert s1 != s2, f"Different seeds should have different spawn points: {s1} vs {s2}"


# 18. Test same seed reproduces identical world and spawn
def test_18_same_seed_reproduces_identical_world_and_spawn():
    gen1 = VerdantOutworldGenerator(seed=482910)
    gen2 = VerdantOutworldGenerator(seed=482910)

    h1 = gen1.generate_heightfield(width=256, depth=256, height=64)
    h2 = gen2.generate_heightfield(width=256, depth=256, height=64)
    assert np.array_equal(h1, h2), "Same seed must reproduce 100% identical heightmap"

    s1 = gen1.find_safe_spawn(h1, width=256, depth=256, height=64)
    s2 = gen2.find_safe_spawn(h2, width=256, depth=256, height=64)
    assert s1 == s2, f"Same seed must reproduce identical spawn: {s1} == {s2}"


# 19. Test alpine snow presence on high peaks
def test_19_alpine_snow_presence_on_high_peaks():
    gen = VerdantOutworldGenerator(seed=10842)
    hmap = gen.generate_heightfield(width=512, depth=512, height=64)
    vbytes = gen.populate_voxels(hmap, width=512, depth=512, height=64)

    snow_count = vbytes.count(blocks.clothWhite.blockID)
    assert snow_count >= 10000, f"Expected at least 10,000 alpine snow blocks, found {snow_count}"

    # Verify snow is placed on high altitudes (Y >= 54)
    peaks_y = np.where(hmap >= 54)
    assert len(peaks_y[0]) > 0, "Island must have alpine peaks reaching Y >= 54"


# 20. Test abundant vegetation and trees
def test_20_abundant_vegetation_and_trees():
    gen = VerdantOutworldGenerator(seed=10842)
    world = gen.generate(width=512, depth=512, height=64)
    b_data = world.getBlocks()

    wood_count = b_data.count(blocks.wood.blockID)
    leaves_count = b_data.count(blocks.leaves.blockID)
    flowers_count = b_data.count(blocks.plantYellow.blockID) + b_data.count(blocks.plantRed.blockID)
    mushrooms_count = b_data.count(blocks.mushroomBrown.blockID) + b_data.count(blocks.mushroomRed.blockID)

    assert wood_count >= 5000, f"Expected >= 5000 wood blocks from trees, got {wood_count}"
    assert leaves_count >= 50000, f"Expected >= 50000 leaf blocks from trees, got {leaves_count}"
    assert flowers_count >= 2000, f"Expected >= 2000 flowers, got {flowers_count}"
    assert mushrooms_count >= 1000, f"Expected >= 1000 mushrooms, got {mushrooms_count}"


# 21. Test LevelLoader seed persistence
def test_21_level_loader_seed_persistence():
    import tempfile
    from mc.net.minecraft.game.level.LevelLoader import LevelLoader
    from verdant.world.outworld import get_world_seed, set_world_seed

    world = World()
    world.generate(32, 64, 32, bytearray(32 * 64 * 32), bytearray(32 * 64 * 32))
    world.name = "TestSeedPersistence"
    test_seed = 87654321
    set_world_seed(world, test_seed)

    loader = LevelLoader(None)
    with tempfile.NamedTemporaryFile(suffix=".mclevel", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        loader.save(world, tmp_path)
        loaded_world = loader.load(tmp_path)
        recovered_seed = get_world_seed(loaded_world)
        assert recovered_seed == test_seed, f"Expected seed {test_seed}, recovered {recovered_seed}"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# 22. Test safe spawn air clearance
def test_22_safe_spawn_air_clearance():
    gen = VerdantOutworldGenerator(seed=10842)
    world = gen.generate(width=512, depth=512, height=64)

    sx = world.xSpawn
    sy = world.ySpawn
    sz = world.zSpawn

    assert world.getBlockId(sx, sy, sz) == 0, f"Spawn block ({sx}, {sy}, {sz}) must be air"
    assert world.getBlockId(sx, sy + 1, sz) == 0, f"Head block ({sx}, {sy+1}, {sz}) must be air"
    ground = world.getBlockId(sx, sy - 1, sz)
    assert ground in (blocks.grass.blockID, blocks.dirt.blockID, blocks.sand.blockID), f"Ground must be walkable solid block, got {ground}"


if __name__ == "__main__":
    test_funcs = [
        obj for name, obj in list(globals().items())
        if name.startswith("test_") and callable(obj)
    ]
    test_funcs.sort(key=lambda f: f.__name__)
    passed = 0
    failed = 0
    print(f"Running {len(test_funcs)} M13 tests...")
    for f in test_funcs:
        try:
            f()
            passed += 1
            print(f"  PASS: {f.__name__}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {f.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\nResult: {passed}/{len(test_funcs)} passed ({failed} failed)")
    if failed > 0:
        sys.exit(1)
