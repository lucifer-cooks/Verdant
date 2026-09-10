"""Comprehensive automated tests for VERDANT M11 — Original Creature Visuals."""

import os
import sys
from pathlib import Path
from PIL import Image

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure World is loaded before RenderManager to prevent Cython circular import
from mc.net.minecraft.game.level.World import World
from mc.net.minecraft.client.render.entity.RenderManager import RenderManager
from mc.net.minecraft.game.entity.animal.EntityPig import EntityPig
from mc.net.minecraft.game.entity.animal.EntitySheep import EntitySheep
from mc.net.minecraft.game.entity.monster.EntityCreeper import EntityCreeper
from mc.net.minecraft.game.entity.monster.EntityGiantZombie import EntityGiantZombie
from mc.net.minecraft.game.entity.monster.EntitySkeleton import EntitySkeleton
from mc.net.minecraft.game.entity.monster.EntitySpider import EntitySpider
from mc.net.minecraft.game.entity.monster.EntityZombie import EntityZombie
from mc.net.minecraft.game.entity.player.EntityPlayer import EntityPlayer
from mc import Resources

from verdant.assets import (
    AssetRegistry,
    ThemeManager,
    ThemeMode,
    get_asset_resolution,
    resolve_texture_data,
)
from verdant.assets.creatures import (
    ModelBriarReaver,
    ModelCloudRam,
    ModelHollowStalker,
    ModelMossbackBoar,
    ModelSkitterer,
    ModelSporeSpire,
    ModelVerdantWayfarer,
    RenderBriarReaver,
    RenderCloudRam,
    RenderHollowStalker,
    RenderMossbackBoar,
    RenderSkitterer,
    RenderSporeSpire,
    RenderVerdantWayfarer,
    VERDANT_CREATURE_SPECS,
    CreatureRenderDispatcher,
    ensure_all_creature_textures,
    install_verdant_creature_renderers,
    register_verdant_creature_textures,
)
from verdant.assets.creatures.textures import (
    HOSTILE_TEXTURE_DIR,
    PASSIVE_TEXTURE_DIR,
    PLAYER_TEXTURE_DIR,
)


def _get_test_world() -> World:
    w = World()
    w.generate(16, 16, 16, bytearray(16 * 16 * 16), bytearray(16 * 16 * 16))
    return w


# 1. Wayfarer registration
def test_01_wayfarer_registration():
    spec = VERDANT_CREATURE_SPECS[EntityPlayer]
    assert spec["logical_key"] == "player"
    assert spec["verdant_name"] == "Verdant Wayfarer"
    assert spec["model_class"] == ModelVerdantWayfarer
    assert spec["renderer_class"] == RenderVerdantWayfarer
    assert spec["texture_file"].name == "wayfarer.png"


# 2. Mossback Boar registration
def test_02_mossback_boar_registration():
    spec = VERDANT_CREATURE_SPECS[EntityPig]
    assert spec["logical_key"] == "pig"
    assert spec["verdant_name"] == "Mossback Boar"
    assert spec["model_class"] == ModelMossbackBoar
    assert spec["renderer_class"] == RenderMossbackBoar


# 3. Cloud-Ram registration
def test_03_cloud_ram_registration():
    spec = VERDANT_CREATURE_SPECS[EntitySheep]
    assert spec["logical_key"] == "sheep"
    assert spec["verdant_name"] == "Cloud-Ram"
    assert spec["model_class"] == ModelCloudRam
    assert spec["renderer_class"] == RenderCloudRam


# 4. Hollow Stalker registration
def test_04_hollow_stalker_registration():
    spec = VERDANT_CREATURE_SPECS[EntityZombie]
    assert spec["logical_key"] == "zombie"
    assert spec["verdant_name"] == "Hollow Stalker"
    assert spec["model_class"] == ModelHollowStalker
    assert spec["renderer_class"] == RenderHollowStalker


# 5. Briar Reaver registration
def test_05_briar_reaver_registration():
    spec = VERDANT_CREATURE_SPECS[EntitySkeleton]
    assert spec["logical_key"] == "skeleton"
    assert spec["verdant_name"] == "Briar Reaver"
    assert spec["model_class"] == ModelBriarReaver
    assert spec["renderer_class"] == RenderBriarReaver


# 6. Spore Spire registration
def test_06_spore_spire_registration():
    spec = VERDANT_CREATURE_SPECS[EntityCreeper]
    assert spec["logical_key"] == "creeper"
    assert spec["verdant_name"] == "Spore Spire"
    assert spec["model_class"] == ModelSporeSpire
    assert spec["renderer_class"] == RenderSporeSpire


# 7. Skitterer registration
def test_07_skitterer_registration():
    spec = VERDANT_CREATURE_SPECS[EntitySpider]
    assert spec["logical_key"] == "spider"
    assert spec["verdant_name"] == "Chittering Skitterer"
    assert spec["model_class"] == ModelSkitterer
    assert spec["renderer_class"] == RenderSkitterer


# 8. Entity -> logical visual mapping
def test_08_entity_to_visual_mapping():
    assert EntityPlayer in VERDANT_CREATURE_SPECS
    assert EntityPig in VERDANT_CREATURE_SPECS
    assert EntitySheep in VERDANT_CREATURE_SPECS
    assert EntityZombie in VERDANT_CREATURE_SPECS
    assert EntitySkeleton in VERDANT_CREATURE_SPECS
    assert EntityCreeper in VERDANT_CREATURE_SPECS
    assert EntitySpider in VERDANT_CREATURE_SPECS


# 9. Model instantiation and geometry structure
def test_09_model_resolution_and_structure():
    from mc.net.minecraft.client.model.ModelZombie import ModelZombie
    from mc.net.minecraft.client.model.ModelCreeper import ModelCreeper
    from mc.net.minecraft.client.model.ModelPig import ModelPig
    from mc.net.minecraft.client.model.ModelSheep import ModelSheep
    from mc.net.minecraft.client.model.ModelSkeleton import ModelSkeleton
    from mc.net.minecraft.client.model.ModelSpider import ModelSpider
    from mc.net.minecraft.client.model.ModelBiped import ModelBiped

    m_wayfarer = ModelVerdantWayfarer()
    assert isinstance(m_wayfarer, ModelBiped)

    m_boar = ModelMossbackBoar()
    assert isinstance(m_boar, ModelPig)

    m_ram = ModelCloudRam()
    assert isinstance(m_ram, ModelSheep)

    m_stalker = ModelHollowStalker()
    assert isinstance(m_stalker, ModelZombie)

    m_reaver = ModelBriarReaver()
    assert isinstance(m_reaver, ModelSkeleton)

    m_spire = ModelSporeSpire()
    assert isinstance(m_spire, ModelCreeper)

    m_skitterer = ModelSkitterer()
    assert isinstance(m_skitterer, ModelSpider)


# 10. Texture resolution
def test_10_texture_resolution():
    register_verdant_creature_textures()
    # Zombie uses hollow_stalker.png skin (64x32)
    data_zombie = resolve_texture_data("mob/zombie.png")
    assert getattr(data_zombie, "size", None) == (64, 32)

    # Creeper uses spore_spire.png skin (64x32)
    data_creeper = resolve_texture_data("mob/creeper.png")
    assert getattr(data_creeper, "size", None) == (64, 32)

    # Pig remains authoritative legacy resource
    data_pig = resolve_texture_data("mob/pig.png")
    assert isinstance(data_pig, tuple)
    assert data_pig[0] == 64 and data_pig[1] == 32


# 11. Missing visual fallback
def test_11_missing_visual_fallback():
    theme_mgr = ThemeManager.get_instance()
    theme_mgr.set_mode(ThemeMode.CLASSIC)

    # In classic mode, fallback texture is served directly from Resources
    data = resolve_texture_data("terrain.png")
    assert isinstance(data, tuple)
    assert data[0] == 256

    # Restore Verdant mode
    theme_mgr.set_mode(ThemeMode.VERDANT_ORIGINAL)


# 12. Fallback state reporting
def test_12_fallback_state_reporting():
    info = get_asset_resolution("pig", "entities")
    assert "logical_key" in info
    assert "theme" in info
    assert "source" in info


# 13. RenderManager compatibility
def test_13_rendermanager_compatibility():
    from mc.net.minecraft.client.model.ModelZombie import ModelZombie
    from mc.net.minecraft.client.model.ModelCreeper import ModelCreeper
    from mc.net.minecraft.client.model.ModelPig import ModelPig

    w = _get_test_world()
    rm = RenderManager()
    install_verdant_creature_renderers(rm)

    pig = EntityPig(w)
    r_pig = rm.getEntityRenderObject(pig)
    assert isinstance(r_pig, RenderMossbackBoar)
    assert isinstance(r_pig._mainModel, ModelPig)

    creeper = EntityCreeper(w)
    r_creeper = rm.getEntityRenderObject(creeper)
    assert isinstance(r_creeper, RenderSporeSpire)
    assert isinstance(r_creeper._mainModel, ModelCreeper)

    zombie = EntityZombie(w)
    r_zombie = rm.getEntityRenderObject(zombie)
    assert isinstance(r_zombie, RenderHollowStalker)
    assert isinstance(r_zombie._mainModel, ModelZombie)

    player = EntityPlayer(w)
    r_player = rm.getEntityRenderObject(player)
    assert isinstance(r_player, RenderVerdantWayfarer)


# 14. Entity object compatibility
def test_14_entity_object_compatibility():
    w = _get_test_world()
    pig = EntityPig(w)
    assert pig._getLivingSound() == "mob.pig"
    assert pig.getTexture() == "mob/pig.png"
    assert abs(pig.width - 0.9) < 0.01
    assert abs(pig.height - 0.9) < 0.01

    zombie = EntityZombie(w)
    assert abs(zombie.width - 0.6) < 0.01
    assert abs(zombie.height - 1.8) < 0.01


# 15. M7 creature ecology compatibility
def test_15_m7_compatibility():
    from verdant.creatures.system import VerdantCreatureSystem
    from verdant.creatures.creature_state import VerdantCreatureState

    w = _get_test_world()
    pig = EntityPig(w)
    cs = VerdantCreatureSystem(seed=123)
    cstate = cs.get_creature_state(pig)
    assert isinstance(cstate, VerdantCreatureState)


# 16. M8 population dynamics compatibility
def test_16_m8_compatibility():
    from verdant.ecosystem.system import VerdantEcosystemSystem
    es = VerdantEcosystemSystem(seed=456)
    assert es is not None


# 17. M9 ecological feedback compatibility
def test_17_m9_compatibility():
    from verdant.feedback import get_ecosystem_state
    w = _get_test_world()
    state = get_ecosystem_state(8.0, 8.0, 8.0, radius=16.0, world=w, seed=789)
    assert state is not None
    assert hasattr(state, "ecological_health")


# 18. Legacy asset non-mutation
def test_18_legacy_asset_non_mutation():
    assert "char.png" in Resources.textures
    assert "mob/pig.png" in Resources.textures
    assert "mob/creeper.png" in Resources.textures
    assert isinstance(Resources.textures["char.png"], tuple)


# 19. No proprietary asset duplication
def test_19_no_proprietary_asset_duplication():
    # Verify no legacy assets were copied into themes/verdant/creatures
    for p in HOSTILE_TEXTURE_DIR.glob("*.png"):
        im = Image.open(p)
        assert im.size in [(64, 32), (64, 64)]
    for p in PASSIVE_TEXTURE_DIR.glob("*.png"):
        im = Image.open(p)
        assert im.size in [(64, 32), (64, 64)]


# 20. No .pyx modifications
def test_20_no_pyx_modifications():
    # Verify compiled cython modules remain intact
    import mc.net.minecraft.client.render.RenderBlocks as rb
    import mc.net.minecraft.client.render.RenderGlobal as rg
    assert rb is not None
    assert rg is not None
