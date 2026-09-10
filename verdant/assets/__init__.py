"""Verdant Original Asset Redirection and Presentation Architecture (M10)."""

from verdant.assets.paths import (
    ASSETS_DIR,
    CLASSIC_THEME_DIR,
    THEMES_DIR,
    VERDANT_THEME_DIR,
    ensure_asset_directories,
    get_theme_directory,
)
from verdant.assets.theme import (
    ThemeManager,
    ThemeMode,
)
from verdant.assets.validation import (
    ValidationResult,
    is_power_of_two,
    validate_atlas,
    validate_audio_file,
    validate_texture_file,
)
from verdant.assets.registry import (
    AssetRegistry,
    AssetResolutionResult,
)
from verdant.assets.textures import (
    TextureRedirectionManager,
    resolve_texture_data,
)
from verdant.assets.audio import (
    AudioRedirectionManager,
    resolve_audio_file,
)
from verdant.assets.debug import (
    dump_asset_report,
    format_asset_resolution,
    get_asset_resolution,
)

__all__ = [
    "ASSETS_DIR",
    "CLASSIC_THEME_DIR",
    "THEMES_DIR",
    "VERDANT_THEME_DIR",
    "ensure_asset_directories",
    "get_theme_directory",
    "ThemeManager",
    "ThemeMode",
    "ValidationResult",
    "is_power_of_two",
    "validate_atlas",
    "validate_audio_file",
    "validate_texture_file",
    "AssetRegistry",
    "AssetResolutionResult",
    "TextureRedirectionManager",
    "resolve_texture_data",
    "AudioRedirectionManager",
    "resolve_audio_file",
    "dump_asset_report",
    "format_asset_resolution",
    "get_asset_resolution",
]
