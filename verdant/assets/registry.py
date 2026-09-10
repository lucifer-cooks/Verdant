"""Central asset registry for Verdant.

Maps logical asset keys to original Verdant assets or legacy engine fallbacks.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from verdant.assets.paths import (
    CLASSIC_THEME_DIR,
    LEGACY_MUSIC_DIR,
    LEGACY_NEWSOUND_DIR,
    VERDANT_THEME_DIR,
    get_theme_directory,
)
from verdant.assets.theme import ThemeManager, ThemeMode
from verdant.assets.validation import (
    ValidationResult,
    validate_atlas,
    validate_audio_file,
    validate_texture_file,
)


@dataclass
class AssetResolutionResult:
    """Result of an asset resolution query."""
    logical_key: str
    category: str
    theme: ThemeMode
    resolved_source: Optional[Union[Path, str, Tuple[int, int, Any]]]
    is_fallback: bool
    is_valid: bool
    details: Dict[str, Any] = field(default_factory=dict)

    def describe(self) -> str:
        source_desc = str(self.resolved_source) if self.resolved_source is not None else "None"
        return (
            f"AssetResolutionResult(key='{self.logical_key}', category='{self.category}', "
            f"theme='{self.theme.value}', source='{source_desc}', fallback={self.is_fallback}, "
            f"valid={self.is_valid})"
        )


class AssetRegistry:
    """Central registry resolving logical asset keys to filesystem paths or in-memory sources."""

    _instance: Optional[AssetRegistry] = None

    # Canonical mappings of logical texture keys to legacy resource names
    DEFAULT_TEXTURE_MAPPINGS = {
        "terrain": "terrain.png",
        "items": "gui/items.png",
        "gui": "gui/gui.png",
        "icons": "gui/icons.png",
        "player": "char.png",
        "water": "water.png",
        "particles": "particles.png",
        "clouds": "clouds.png",
        "shadow": "shadow.png",
        "font1": "default.png1",
        "font2": "default.png2",
        "container": "gui/container.png",
        "crafting": "gui/crafting.png",
        "furnace": "gui/furnace.png",
    }

    # Canonical mappings of logical block names to block IDs
    BLOCK_MAPPINGS = {
        "stone": 1,
        "grass": 2,
        "dirt": 3,
        "cobblestone": 4,
        "planks": 5,
        "sapling": 6,
        "bedrock": 7,
        "water_flowing": 8,
        "water_still": 9,
        "lava_flowing": 10,
        "lava_still": 11,
        "sand": 12,
        "gravel": 13,
        "gold_ore": 14,
        "iron_ore": 15,
        "coal_ore": 16,
        "log": 17,
        "wood": 17,
        "leaves": 18,
        "sponge": 19,
        "glass": 20,
        "cloth": 35,
        "flower_yellow": 37,
        "rose": 38,
        "mushroom_brown": 39,
        "mushroom_red": 40,
        "gold_block": 41,
        "iron_block": 42,
        "slab": 44,
        "brick": 45,
        "tnt": 46,
        "bookshelf": 47,
        "mossy_cobblestone": 48,
        "obsidian": 49,
        "torch": 50,
        "fire": 51,
        "chest": 54,
        "gear": 55,
        "diamond_ore": 56,
        "diamond_block": 57,
        "workbench": 58,
        "crops": 59,
        "farmland": 60,
        "furnace_idle": 61,
        "furnace_active": 62,
    }

    # Canonical mappings of logical entity names to legacy texture and mob keys
    ENTITY_MAPPINGS = {
        "player": {"legacy_texture": "char.png", "legacy_class": "EntityPlayer"},
        "pig": {"legacy_texture": "mob/pig.png", "legacy_class": "EntityPig", "category": "passive_animals"},
        "sheep": {"legacy_texture": "mob/sheep.png", "legacy_class": "EntitySheep", "category": "passive_animals"},
        "sheep_fur": {"legacy_texture": "mob/sheep_fur.png", "legacy_class": "ModelSheepFur", "category": "passive_animals"},
        "zombie": {"legacy_texture": "mob/zombie.png", "legacy_class": "EntityZombie", "category": "hostile_creatures"},
        "skeleton": {"legacy_texture": "mob/skeleton.png", "legacy_class": "EntitySkeleton", "category": "hostile_creatures"},
        "spider": {"legacy_texture": "mob/spider.png", "legacy_class": "EntitySpider", "category": "hostile_creatures"},
        "creeper": {"legacy_texture": "mob/creeper.png", "legacy_class": "EntityCreeper", "category": "hostile_creatures"},
        "giant_zombie": {"legacy_texture": "mob/zombie.png", "legacy_class": "EntityGiantZombie", "category": "hostile_creatures"},
    }

    # Canonical mappings of logical audio cues to legacy sound files/keys
    AUDIO_MAPPINGS = {
        "step.grass": "step/grass1.ogg",
        "step.stone": "step/stone1.ogg",
        "step.wood": "step/wood1.ogg",
        "step.gravel": "step/gravel1.ogg",
        "step.sand": "step/sand1.ogg",
        "water.splash": "random/splash.ogg",
        "water.ambient": "liquid/water.ogg",
        "lava.ambient": "liquid/lava.ogg",
        "fire.ambient": "fire/fire.ogg",
        "fire.ignite": "fire/ignite.ogg",
        "ui.click": "random/click.ogg",
        "random.explode": "random/explode.ogg",
        "random.fuse": "random/fuse.ogg",
        "random.hurt": "random/hurt.ogg",
        "random.bow": "random/bow.ogg",
        "random.pop": "random/pop.ogg",
        "mob.pig": "mob/pig1.ogg",
        "mob.pigdeath": "mob/pigdeath.ogg",
        "mob.sheep": "mob/sheep1.ogg",
        "music.calm1": "music/calm1.ogg",
        "music.calm2": "music/calm2.ogg",
        "music.calm3": "music/calm3.ogg",
    }

    def __init__(self, theme_manager: Optional[ThemeManager] = None) -> None:
        self._theme_mgr = theme_manager or ThemeManager.get_instance()
        # In-memory registrations: category -> { logical_key: source }
        self._custom_registrations: Dict[str, Dict[str, Any]] = {
            "textures": {},
            "audio": {},
            "entities": {},
            "blocks": {},
            "fonts": {},
        }
        self._resolution_cache: Dict[Tuple[str, str, ThemeMode], AssetResolutionResult] = {}

    @classmethod
    def get_instance(cls) -> AssetRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def clear_cache(self) -> None:
        self._resolution_cache.clear()

    def register_asset(self, category: str, logical_key: str, source: Any) -> None:
        """Register a custom asset source directly into memory."""
        cat = category.lower().strip()
        if cat not in self._custom_registrations:
            self._custom_registrations[cat] = {}
        self._custom_registrations[cat][logical_key] = source
        self.clear_cache()

    def unregister_asset(self, category: str, logical_key: str) -> None:
        cat = category.lower().strip()
        if cat in self._custom_registrations:
            self._custom_registrations[cat].pop(logical_key, None)
        self.clear_cache()

    def resolve_texture(self, key_or_legacy_name: str) -> AssetResolutionResult:
        """Resolve a texture asset by logical key or legacy resource name."""
        norm_key = key_or_legacy_name.strip()
        
        # Reverse map legacy name if passed
        logical_key = norm_key
        for lk, leg_name in self.DEFAULT_TEXTURE_MAPPINGS.items():
            if norm_key == leg_name or norm_key == lk:
                logical_key = lk
                break

        legacy_name = self.DEFAULT_TEXTURE_MAPPINGS.get(logical_key, norm_key)
        return self._resolve_with_fallback(
            category="textures",
            logical_key=logical_key,
            legacy_fallback=legacy_name,
            theme_subfolder="textures",
            file_extension=".png",
            validator=validate_atlas if logical_key in ("terrain", "items") else validate_texture_file,
        )

    def resolve_audio(self, audio_key_or_name: str) -> AssetResolutionResult:
        """Resolve an audio cue by logical key or relative file path."""
        norm_key = audio_key_or_name.strip().replace("\\", "/")
        logical_key = norm_key
        
        # Reverse lookup
        for lk, leg_file in self.AUDIO_MAPPINGS.items():
            if norm_key == leg_file or norm_key == lk:
                logical_key = lk
                break

        legacy_file = self.AUDIO_MAPPINGS.get(logical_key, norm_key)
        if not legacy_file.endswith(".ogg"):
            legacy_file += ".ogg"

        return self._resolve_with_fallback(
            category="audio",
            logical_key=logical_key,
            legacy_fallback=legacy_file,
            theme_subfolder="audio",
            file_extension=".ogg",
            validator=validate_audio_file,
        )

    def resolve_entity_visual(self, entity_key_or_class_name: str) -> AssetResolutionResult:
        """Resolve entity visual identity."""
        norm = entity_key_or_class_name.strip()
        logical_key = norm
        for lk, data in self.ENTITY_MAPPINGS.items():
            if norm == data.get("legacy_class") or norm == data.get("legacy_texture") or norm == lk:
                logical_key = lk
                break

        data = self.ENTITY_MAPPINGS.get(logical_key, {"legacy_texture": f"mob/{logical_key}.png"})
        legacy_tex = data.get("legacy_texture", f"mob/{logical_key}.png")

        return self._resolve_with_fallback(
            category="entities",
            logical_key=logical_key,
            legacy_fallback=legacy_tex,
            theme_subfolder="entities",
            file_extension=".png",
            validator=validate_texture_file,
        )

    def resolve_block_visual(self, block_name_or_id: Union[str, int]) -> AssetResolutionResult:
        """Resolve block visual identity."""
        logical_key = str(block_name_or_id)
        if isinstance(block_name_or_id, int):
            for name, bid in self.BLOCK_MAPPINGS.items():
                if bid == block_name_or_id:
                    logical_key = name
                    break
        else:
            norm = str(block_name_or_id).lower().strip()
            if norm in self.BLOCK_MAPPINGS:
                logical_key = norm

        # Block visual defaults to terrain atlas with metadata
        return self._resolve_with_fallback(
            category="blocks",
            logical_key=logical_key,
            legacy_fallback="terrain.png",
            theme_subfolder="blocks",
            file_extension=".png",
            validator=validate_texture_file,
        )

    def _resolve_with_fallback(
        self,
        category: str,
        logical_key: str,
        legacy_fallback: str,
        theme_subfolder: str,
        file_extension: str,
        validator: Optional[Callable[..., ValidationResult]] = None,
    ) -> AssetResolutionResult:
        theme = self._theme_mgr.mode
        cache_key = (category, logical_key, theme)
        if cache_key in self._resolution_cache:
            return self._resolution_cache[cache_key]

        # 1. In CLASSIC theme mode: strictly legacy fallback
        if theme == ThemeMode.CLASSIC:
            res = AssetResolutionResult(
                logical_key=logical_key,
                category=category,
                theme=theme,
                resolved_source=legacy_fallback,
                is_fallback=True,
                is_valid=True,
                details={"mode": "classic_strict_fallback"},
            )
            self._resolution_cache[cache_key] = res
            return res

        # 2. In VERDANT_ORIGINAL mode: check in-memory custom registration first
        if category in self._custom_registrations and logical_key in self._custom_registrations[category]:
            source = self._custom_registrations[category][logical_key]
            res = AssetResolutionResult(
                logical_key=logical_key,
                category=category,
                theme=theme,
                resolved_source=source,
                is_fallback=False,
                is_valid=True,
                details={"mode": "in_memory_override"},
            )
            self._resolution_cache[cache_key] = res
            return res

        # 3. Check for original asset file under theme directory
        theme_dir = self._theme_mgr.get_active_theme_dir()
        candidate_file = theme_dir / theme_subfolder / f"{logical_key}{file_extension}"
        if candidate_file.is_file():
            is_valid = True
            v_details = {}
            if validator is not None:
                val_res = validator(candidate_file)
                is_valid = val_res.is_valid
                v_details = val_res.details

            res = AssetResolutionResult(
                logical_key=logical_key,
                category=category,
                theme=theme,
                resolved_source=candidate_file,
                is_fallback=False,
                is_valid=is_valid,
                details=v_details,
            )
            self._resolution_cache[cache_key] = res
            return res

        # 4. Safe fallback to legacy asset
        if self._theme_mgr.fallback_allowed:
            res = AssetResolutionResult(
                logical_key=logical_key,
                category=category,
                theme=theme,
                resolved_source=legacy_fallback,
                is_fallback=True,
                is_valid=True,
                details={"mode": "verdant_missing_asset_fallback"},
            )
            self._resolution_cache[cache_key] = res
            return res

        # 5. Unresolved (if fallback explicitly disallowed)
        res = AssetResolutionResult(
            logical_key=logical_key,
            category=category,
            theme=theme,
            resolved_source=None,
            is_fallback=False,
            is_valid=False,
            details={"mode": "unresolved_no_fallback"},
        )
        self._resolution_cache[cache_key] = res
        return res
