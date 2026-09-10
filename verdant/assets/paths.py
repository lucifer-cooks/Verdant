"""Filesystem paths and directory structure definitions for Verdant assets."""

from __future__ import annotations

import os
from pathlib import Path

# Base directories
ASSETS_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
PROJECT_ROOT = ASSETS_DIR.parent.parent
THEMES_DIR = ASSETS_DIR / "themes"
CLASSIC_THEME_DIR = THEMES_DIR / "classic"
VERDANT_THEME_DIR = THEMES_DIR / "verdant"

# Legacy engine asset locations (read-only fallbacks)
LEGACY_RESOURCES_DIR = PROJECT_ROOT / "mc" / "resources"
LEGACY_NEWSOUND_DIR = LEGACY_RESOURCES_DIR / "newsound"
LEGACY_MUSIC_DIR = LEGACY_RESOURCES_DIR / "music"


def ensure_asset_directories() -> None:
    """Ensure asset and theme directory trees exist without creating dummy art."""
    THEMES_DIR.mkdir(parents=True, exist_ok=True)
    CLASSIC_THEME_DIR.mkdir(parents=True, exist_ok=True)
    VERDANT_THEME_DIR.mkdir(parents=True, exist_ok=True)
    
    # Subdirectories for original Verdant assets
    for sub in ("textures", "audio", "entities", "gui", "font"):
        (VERDANT_THEME_DIR / sub).mkdir(parents=True, exist_ok=True)


def get_theme_directory(theme_name: str) -> Path:
    """Return the Path directory for a named theme."""
    norm = str(theme_name).lower().strip()
    if norm in ("classic", "legacy"):
        return CLASSIC_THEME_DIR
    elif norm in ("verdant", "verdant_original", "original"):
        return VERDANT_THEME_DIR
    else:
        custom_dir = THEMES_DIR / norm
        return custom_dir
