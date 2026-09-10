"""Theme definitions and active theme state management for Verdant."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from verdant.assets.paths import (
    CLASSIC_THEME_DIR,
    VERDANT_THEME_DIR,
    get_theme_directory,
)


class ThemeMode(str, Enum):
    """Supported theme modes.
    
    CLASSIC:
        Strictly preserves baseline legacy Minecraft Indev presentation.
        Uses 100% in-engine legacy fallback resources.
        Zero original asset overrides.
        
    VERDANT_ORIGINAL:
        Prioritizes original Verdant assets located under
        verdant/assets/themes/verdant/.
        Safely falls back to legacy resources when a replacement does not exist.
    """
    CLASSIC = "classic"
    VERDANT_ORIGINAL = "verdant_original"

    def __str__(self) -> str:
        return self.value


class ThemeManager:
    """Manages active theme state and fallback behavior."""

    _instance: Optional[ThemeManager] = None

    def __init__(self, initial_mode: ThemeMode = ThemeMode.VERDANT_ORIGINAL) -> None:
        self._mode: ThemeMode = initial_mode
        self._fallback_allowed: bool = True

    @classmethod
    def get_instance(cls) -> ThemeManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    @property
    def mode(self) -> ThemeMode:
        return self._mode

    def set_mode(self, mode: ThemeMode | str) -> None:
        if isinstance(mode, str):
            norm = mode.lower().strip()
            if norm in ("classic", "legacy"):
                self._mode = ThemeMode.CLASSIC
            elif norm in ("verdant", "verdant_original", "original"):
                self._mode = ThemeMode.VERDANT_ORIGINAL
            else:
                raise ValueError(f"Unknown theme mode: {mode}")
        elif isinstance(mode, ThemeMode):
            self._mode = mode
        else:
            raise TypeError(f"Invalid theme mode type: {type(mode)}")

    @property
    def is_classic(self) -> bool:
        return self._mode == ThemeMode.CLASSIC

    @property
    def is_verdant_original(self) -> bool:
        return self._mode == ThemeMode.VERDANT_ORIGINAL

    @property
    def fallback_allowed(self) -> bool:
        return self._fallback_allowed

    def set_fallback_allowed(self, allowed: bool) -> None:
        self._fallback_allowed = bool(allowed)

    def get_active_theme_dir(self) -> Path:
        if self._mode == ThemeMode.CLASSIC:
            return CLASSIC_THEME_DIR
        return VERDANT_THEME_DIR
