"""Unit and integration tests for VERDANT M10 — Original Asset Redirection Foundation."""

import os
import sys
import tempfile
import struct
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mc import Resources
from verdant.assets import (
    ASSETS_DIR,
    CLASSIC_THEME_DIR,
    THEMES_DIR,
    VERDANT_THEME_DIR,
    AssetRegistry,
    AssetResolutionResult,
    AudioRedirectionManager,
    ThemeManager,
    ThemeMode,
    TextureRedirectionManager,
    ValidationResult,
    dump_asset_report,
    ensure_asset_directories,
    format_asset_resolution,
    get_asset_resolution,
    is_power_of_two,
    resolve_audio_file,
    resolve_texture_data,
    validate_atlas,
    validate_audio_file,
    validate_texture_file,
)


def _create_dummy_png(path: Path, width: int = 256, height: int = 256, has_alpha: bool = True):
    """Helper to write a valid minimalist PNG file header for testing validation without PIL."""
    # 8-byte signature + IHDR chunk
    # IHDR: 4-byte len (13), 4-byte type (IHDR), 13 bytes data, 4 bytes CRC
    sig = b"\x89PNG\r\n\x1a\n"
    color_type = 6 if has_alpha else 2  # 6 = RGBA, 2 = RGB
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    ihdr_chunk = struct.pack(">I", 13) + b"IHDR" + ihdr_data + b"\x00\x00\x00\x00"
    # Minimal IEND chunk
    iend_chunk = struct.pack(">I", 0) + b"IEND" + b"\x00\x00\x00\x00"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(sig + ihdr_chunk + iend_chunk)


def _create_dummy_ogg(path: Path):
    """Helper to write a valid minimalist OGG file header for testing validation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00" + b"\x00" * 30)


# 1. Asset registry creation
def test_01_asset_registry_creation():
    registry = AssetRegistry()
    assert registry is not None
    assert "terrain" in registry.DEFAULT_TEXTURE_MAPPINGS
    assert "items" in registry.DEFAULT_TEXTURE_MAPPINGS
    assert "player" in registry.ENTITY_MAPPINGS
    assert "stone" in registry.BLOCK_MAPPINGS


# 2. Logical asset resolution
def test_02_logical_asset_resolution():
    theme_mgr = ThemeManager(ThemeMode.VERDANT_ORIGINAL)
    registry = AssetRegistry(theme_mgr)

    res_terrain = registry.resolve_texture("terrain")
    assert isinstance(res_terrain, AssetResolutionResult)
    assert res_terrain.logical_key == "terrain"
    assert res_terrain.category == "textures"

    res_player = registry.resolve_texture("player")
    assert res_player.logical_key == "player"


# 3. Classic mode (Strict Legacy Fallback)
def test_03_classic_mode_strict_fallback():
    theme_mgr = ThemeManager(ThemeMode.CLASSIC)
    registry = AssetRegistry(theme_mgr)

    # In classic mode, terrain always resolves to legacy fallback terrain.png
    res = registry.resolve_texture("terrain")
    assert res.is_fallback is True
    assert res.resolved_source == "terrain.png"
    assert res.theme == ThemeMode.CLASSIC

    res_items = registry.resolve_texture("items")
    assert res_items.is_fallback is True
    assert res_items.resolved_source == "gui/items.png"


# 4. Verdant mode (Theme setting and active directory)
def test_04_verdant_mode_active():
    theme_mgr = ThemeManager(ThemeMode.VERDANT_ORIGINAL)
    assert theme_mgr.is_verdant_original is True
    assert theme_mgr.is_classic is False
    assert theme_mgr.get_active_theme_dir() == VERDANT_THEME_DIR

    theme_mgr.set_mode(ThemeMode.CLASSIC)
    assert theme_mgr.is_classic is True
    assert theme_mgr.get_active_theme_dir() == CLASSIC_THEME_DIR


# 5. Missing-asset fallback
def test_05_missing_asset_fallback():
    theme_mgr = ThemeManager(ThemeMode.VERDANT_ORIGINAL)
    registry = AssetRegistry(theme_mgr)

    # When no original asset exists in verdant directory, falls back to legacy resource
    res = registry.resolve_texture("terrain")
    assert res.is_fallback is True
    assert res.resolved_source == "terrain.png"
    assert res.is_valid is True

    # Audio missing asset fallback
    res_audio = registry.resolve_audio("step.grass")
    assert res_audio.is_fallback is True
    assert res_audio.resolved_source == "step/grass1.ogg"


# 6. Existing-asset selection (Custom in-memory or registered asset)
def test_06_existing_asset_selection():
    theme_mgr = ThemeManager(ThemeMode.VERDANT_ORIGINAL)
    registry = AssetRegistry(theme_mgr)

    custom_texture_tuple = (256, 256, [255] * (256 * 256 * 4))
    registry.register_asset("textures", "terrain", custom_texture_tuple)

    res = registry.resolve_texture("terrain")
    assert res.is_fallback is False
    assert res.resolved_source == custom_texture_tuple
    assert res.is_valid is True

    # Clean up
    registry.unregister_asset("textures", "terrain")
    res_after = registry.resolve_texture("terrain")
    assert res_after.is_fallback is True


# 7. Texture validation (Dimensions, power of two, format)
def test_07_texture_validation():
    with tempfile.TemporaryDirectory() as tmpdir:
        valid_png = Path(tmpdir) / "test_valid.png"
        _create_dummy_png(valid_png, 64, 64, has_alpha=True)

        val_valid = validate_texture_file(valid_png, require_power_of_two=True)
        assert val_valid.is_valid is True
        assert val_valid.details["width"] == 64
        assert val_valid.details["height"] == 64

        # Non-power-of-two
        invalid_png = Path(tmpdir) / "test_invalid.png"
        _create_dummy_png(invalid_png, 50, 50, has_alpha=False)
        val_invalid = validate_texture_file(invalid_png, require_power_of_two=True)
        assert val_invalid.is_valid is False
        assert any("powers of two" in err for err in val_invalid.errors)


# 8. Atlas dimension validation (256x256, 16x16 tile grid)
def test_08_atlas_dimension_validation():
    with tempfile.TemporaryDirectory() as tmpdir:
        atlas_path = Path(tmpdir) / "terrain.png"
        _create_dummy_png(atlas_path, 256, 256, has_alpha=True)

        val_atlas = validate_atlas(atlas_path, expected_tiles_per_axis=16, recommended_dimension=256)
        assert val_atlas.is_valid is True
        assert val_atlas.details["tiles_per_axis"] == 16
        assert val_atlas.details["tile_size"] == 16

        bad_atlas = Path(tmpdir) / "bad_terrain.png"
        _create_dummy_png(bad_atlas, 128, 128, has_alpha=True)
        val_bad = validate_atlas(bad_atlas, recommended_dimension=256)
        assert val_bad.is_valid is False


# 9. Audio resolution and validation
def test_09_audio_resolution_and_validation():
    theme_mgr = ThemeManager(ThemeMode.VERDANT_ORIGINAL)
    registry = AssetRegistry(theme_mgr)

    res = registry.resolve_audio("step.stone")
    assert res.logical_key == "step.stone"
    assert res.category == "audio"
    assert res.resolved_source == "step/stone1.ogg"
    assert res.is_fallback is True

    with tempfile.TemporaryDirectory() as tmpdir:
        ogg_path = Path(tmpdir) / "sound.ogg"
        _create_dummy_ogg(ogg_path)
        val_ogg = validate_audio_file(ogg_path)
        assert val_ogg.is_valid is True

        txt_path = Path(tmpdir) / "sound.txt"
        with open(txt_path, "w") as f:
            f.write("not an ogg")
        val_txt = validate_audio_file(txt_path)
        assert val_txt.is_valid is False


# 10. Entity visual mapping
def test_10_entity_visual_mapping():
    registry = AssetRegistry.get_instance()
    
    # Resolving via entity class name
    res_pig = registry.resolve_entity_visual("EntityPig")
    assert res_pig.logical_key == "pig"
    assert res_pig.category == "entities"
    assert res_pig.resolved_source == "mob/pig.png"

    # Resolving via logical name
    res_creeper = registry.resolve_entity_visual("creeper")
    assert res_creeper.logical_key == "creeper"
    assert res_creeper.resolved_source == "mob/creeper.png"

    res_player = registry.resolve_entity_visual("player")
    assert res_player.resolved_source == "char.png"


# 11. Block visual mapping
def test_11_block_visual_mapping():
    registry = AssetRegistry.get_instance()

    # Resolving via block ID
    res_grass = registry.resolve_block_visual(2)  # Block ID 2 = grass
    assert res_grass.logical_key == "grass"
    assert res_grass.resolved_source == "terrain.png"

    # Resolving via block name
    res_stone = registry.resolve_block_visual("stone")
    assert res_stone.logical_key == "stone"
    assert res_stone.resolved_source == "terrain.png"


# 12. Debug resolution information
def test_12_debug_resolution_information():
    info = get_asset_resolution("terrain", "textures")
    assert info["logical_key"] == "terrain"
    assert info["category"] == "textures"
    assert "theme" in info
    assert "source" in info
    assert "fallback" in info
    assert "valid" in info

    formatted = format_asset_resolution("terrain", "textures")
    assert "asset = terrain (textures)" in formatted
    assert "theme =" in formatted

    report = dump_asset_report()
    assert len(report) > 0
    assert any(item["logical_key"] == "terrain" for item in report)
    assert any(item["logical_key"] == "pig" for item in report)


# 13. Deterministic resolution
def test_13_deterministic_resolution():
    registry = AssetRegistry.get_instance()
    res1 = registry.resolve_texture("terrain")
    res2 = registry.resolve_texture("terrain")
    assert res1.logical_key == res2.logical_key
    assert res1.resolved_source == res2.resolved_source
    assert res1.is_fallback == res2.is_fallback
    assert res1.is_valid == res2.is_valid


# 14. No mutation of legacy resources
def test_14_no_mutation_of_legacy_resources():
    # Verify Resources.textures remains intact and identical to baseline
    assert "terrain.png" in Resources.textures
    assert "char.png" in Resources.textures
    assert "gui/items.png" in Resources.textures
    
    terrain_tex = Resources.textures["terrain.png"]
    assert isinstance(terrain_tex, tuple)
    assert terrain_tex[0] == 256
    assert terrain_tex[1] == 256
    assert len(terrain_tex[2]) == 256 * 256 * 4


# 15. M2-M9 compatibility
def test_15_m2_m9_compatibility():
    from verdant.world.state import VerdantWorldState
    from verdant.environment.climate import VerdantClimateSystem
    from verdant.water.system import VerdantWaterSystem
    from verdant.feedback import get_ecosystem_state

    ws = VerdantWorldState()
    assert ws is not None

    clim = VerdantClimateSystem(seed=123)
    c_val = clim.get_environment(0, 64, 0)
    assert c_val is not None

    # Resolving texture data through texture redirection manager
    data = resolve_texture_data("terrain.png")
    assert data is not None
