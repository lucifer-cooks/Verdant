"""Central mapping and dispatch for Verdant creature identities and renderers."""

from __future__ import annotations

try:
    import mc.net.minecraft.client.render.RenderGlobal
except Exception:
    pass

from typing import Any, Dict, Optional, Type

from mc.net.minecraft.game.entity.animal.EntityPig import EntityPig
from mc.net.minecraft.game.entity.animal.EntitySheep import EntitySheep
from mc.net.minecraft.game.entity.monster.EntityCreeper import EntityCreeper
from mc.net.minecraft.game.entity.monster.EntityGiantZombie import EntityGiantZombie
from mc.net.minecraft.game.entity.monster.EntitySkeleton import EntitySkeleton
from mc.net.minecraft.game.entity.monster.EntitySpider import EntitySpider
from mc.net.minecraft.game.entity.monster.EntityZombie import EntityZombie
from mc.net.minecraft.game.entity.player.EntityPlayer import EntityPlayer

from verdant.assets.creatures.models import (
    ModelBriarReaver,
    ModelCloudRam,
    ModelHollowStalker,
    ModelMossbackBoar,
    ModelSkitterer,
    ModelSporeSpire,
    ModelVerdantWayfarer,
)
from verdant.assets.creatures.renderers import (
    RenderBriarReaver,
    RenderCloudRam,
    RenderHollowStalker,
    RenderMossbackBoar,
    RenderSkitterer,
    RenderSporeSpire,
    RenderVerdantWayfarer,
)
from verdant.assets.creatures.textures import (
    HOSTILE_TEXTURE_DIR,
    PASSIVE_TEXTURE_DIR,
    PLAYER_TEXTURE_DIR,
    ensure_all_creature_textures,
)
from verdant.assets.registry import AssetRegistry
from verdant.assets.theme import ThemeManager, ThemeMode

# Central registry data structure mapping entity gameplay classes to Verdant visual specifications
VERDANT_CREATURE_SPECS: Dict[Type, Dict[str, Any]] = {
    EntityPlayer: {
        "logical_key": "player",
        "verdant_name": "Verdant Wayfarer",
        "category": "player",
        "model_class": ModelVerdantWayfarer,
        "renderer_class": RenderVerdantWayfarer,
        "texture_file": PLAYER_TEXTURE_DIR / "wayfarer.png",
        "legacy_texture": "char.png",
    },
    EntityPig: {
        "logical_key": "pig",
        "verdant_name": "Mossback Boar",
        "category": "passive",
        "model_class": ModelMossbackBoar,
        "renderer_class": RenderMossbackBoar,
        "texture_file": PASSIVE_TEXTURE_DIR / "mossback_boar.png",
        "legacy_texture": "mob/pig.png",
    },
    EntitySheep: {
        "logical_key": "sheep",
        "verdant_name": "Cloud-Ram",
        "category": "passive",
        "model_class": ModelCloudRam,
        "renderer_class": RenderCloudRam,
        "texture_file": PASSIVE_TEXTURE_DIR / "cloud_ram.png",
        "legacy_texture": "mob/sheep.png",
    },
    EntityZombie: {
        "logical_key": "zombie",
        "verdant_name": "Hollow Stalker",
        "category": "hostile",
        "model_class": ModelHollowStalker,
        "renderer_class": RenderHollowStalker,
        "texture_file": HOSTILE_TEXTURE_DIR / "hollow_stalker.png",
        "legacy_texture": "mob/zombie.png",
    },
    EntitySkeleton: {
        "logical_key": "skeleton",
        "verdant_name": "Briar Reaver",
        "category": "hostile",
        "model_class": ModelBriarReaver,
        "renderer_class": RenderBriarReaver,
        "texture_file": HOSTILE_TEXTURE_DIR / "briar_reaver.png",
        "legacy_texture": "mob/skeleton.png",
    },
    EntityCreeper: {
        "logical_key": "creeper",
        "verdant_name": "Spore Spire",
        "category": "hostile",
        "model_class": ModelSporeSpire,
        "renderer_class": RenderSporeSpire,
        "texture_file": HOSTILE_TEXTURE_DIR / "spore_spire.png",
        "legacy_texture": "mob/creeper.png",
    },
    EntitySpider: {
        "logical_key": "spider",
        "verdant_name": "Chittering Skitterer",
        "category": "hostile",
        "model_class": ModelSkitterer,
        "renderer_class": RenderSkitterer,
        "texture_file": HOSTILE_TEXTURE_DIR / "skitterer.png",
        "legacy_texture": "mob/spider.png",
    },
    EntityGiantZombie: {
        "logical_key": "giant_zombie",
        "verdant_name": "Colossal Stalker",
        "category": "hostile",
        "model_class": ModelHollowStalker,
        "renderer_class": RenderHollowStalker,
        "texture_file": HOSTILE_TEXTURE_DIR / "hollow_stalker.png",
        "legacy_texture": "mob/zombie.png",
    },
}


def register_verdant_creature_textures() -> None:
    """Register creature textures into the M10 AssetRegistry.
    
    Zombie and Creeper use the user's custom skins (hollow_stalker.png and spore_spire.png).
    Other mobs remain with their authoritative original Indev textures.
    """
    ensure_all_creature_textures()
    registry = AssetRegistry.get_instance()

    for entity_cls in (EntityZombie, EntityCreeper, EntityGiantZombie):
        spec = VERDANT_CREATURE_SPECS[entity_cls]
        tex_path = spec["texture_file"]
        leg_tex = spec["legacy_texture"]
        if tex_path.is_file():
            registry.register_asset("textures", leg_tex, tex_path)
            registry.register_asset("textures", spec["logical_key"], tex_path)


class CreatureRenderDispatcher:
    """Dispatches between original Verdant renderers and legacy engine fallbacks."""

    _instance: Optional[CreatureRenderDispatcher] = None

    def __init__(self) -> None:
        self._legacy_render_cache: Dict[Any, Dict[Type, Any]] = {}
        self._verdant_render_cache: Dict[Any, Dict[Type, Any]] = {}

    @classmethod
    def get_instance(cls) -> CreatureRenderDispatcher:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def install(self, render_manager: Any) -> None:
        """Install Verdant creature renderers into a RenderManager instance."""
        theme_mgr = ThemeManager.get_instance()

        # Cache original legacy renderers if not already cached
        render_map = getattr(render_manager, "_RenderManager__entityRenderMap", None)
        if render_map is None:
            return

        rm_id = id(render_manager)
        if rm_id not in self._legacy_render_cache:
            self._legacy_render_cache[rm_id] = dict(render_map)

        # Make sure textures are registered
        register_verdant_creature_textures()

        if theme_mgr.is_classic:
            # Restore legacy renderers
            for ent_cls, render_obj in self._legacy_render_cache[rm_id].items():
                render_map[ent_cls] = render_obj
            return

        # Theme is VERDANT_ORIGINAL: instantiate and install Verdant renderers
        if rm_id not in self._verdant_render_cache:
            self._verdant_render_cache[rm_id] = {}
            for ent_cls, spec in VERDANT_CREATURE_SPECS.items():
                try:
                    renderer_inst = spec["renderer_class"]()
                    renderer_inst.setRenderManager(render_manager)
                    self._verdant_render_cache[rm_id][ent_cls] = renderer_inst
                except Exception:
                    pass

        for ent_cls, renderer_inst in self._verdant_render_cache[rm_id].items():
            render_map[ent_cls] = renderer_inst


def install_verdant_creature_renderers(render_manager: Any) -> None:
    """Convenience function called during RenderManager initialization."""
    CreatureRenderDispatcher.get_instance().install(render_manager)
