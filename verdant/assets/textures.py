"""Texture resolution and redirection layer for Verdant."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

try:
    from PIL import Image
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

from mc import Resources
from verdant.assets.registry import AssetRegistry, AssetResolutionResult


class TextureRedirectionManager:
    """Manages texture resolution between original Verdant assets and legacy engine resources."""

    _instance: Optional[TextureRedirectionManager] = None

    def __init__(self, registry: Optional[AssetRegistry] = None) -> None:
        self._registry = registry or AssetRegistry.get_instance()
        self._stats = {
            "total_requests": 0,
            "verdant_served": 0,
            "fallback_served": 0,
            "failed_requests": 0,
        }
        self._last_resolutions: Dict[str, AssetResolutionResult] = {}

    @classmethod
    def get_instance(cls) -> TextureRedirectionManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    @property
    def stats(self) -> Dict[str, int]:
        return dict(self._stats)

    def get_last_resolution(self, resource_name: str) -> Optional[AssetResolutionResult]:
        return self._last_resolutions.get(resource_name)

    def resolve_texture_data(self, resource_name: str) -> Any:
        """Resolve raw texture data (tuple or Image) for a requested resource name.
        
        If an original Verdant asset is active and found:
            - If registered as an in-memory tuple/object, return it.
            - If registered as a file path, load it via PIL (or custom loader) and return it.
        Otherwise:
            - Safely fall back to legacy Resources.textures[resource_name].
        """
        self._stats["total_requests"] += 1
        
        # Clean prefix modifiers if present (e.g. '##' or '%%')
        clean_name = resource_name
        if clean_name.startswith("##") or clean_name.startswith("%%"):
            clean_name = clean_name[2:]

        res = self._registry.resolve_texture(clean_name)
        self._last_resolutions[resource_name] = res

        if not res.is_fallback and res.resolved_source is not None:
            source = res.resolved_source
            # If in-memory tuple or image
            if isinstance(source, tuple) or (hasattr(source, "width") and hasattr(source, "getdata")):
                self._stats["verdant_served"] += 1
                return source

            # If filesystem path to an image file
            if isinstance(source, (str, Path)):
                path = Path(source)
                if path.is_file() and _HAS_PIL:
                    try:
                        img = Image.open(path).convert("RGBA")
                        # If a 64x64 skin has an empty bottom half, crop to 64x32 to match Indev UV coordinates
                        if img.size == (64, 64):
                            bottom_has_content = any(img.getpixel((x, y))[3] > 0 for y in range(32, 64) for x in range(64))
                            if not bottom_has_content:
                                img = img.crop((0, 0, 64, 32))
                        self._stats["verdant_served"] += 1
                        return img
                    except Exception:
                        pass  # Fall back on loader exception

        # Fallback path: return legacy embedded texture from Resources
        if clean_name in Resources.textures:
            self._stats["fallback_served"] += 1
            return Resources.textures[clean_name]

        self._stats["failed_requests"] += 1
        raise KeyError(f"Texture resource '{resource_name}' could not be resolved from Verdant or legacy engine.")


def resolve_texture_data(resource_name: str) -> Any:
    """Convenience functional interface for resolving texture data."""
    return TextureRedirectionManager.get_instance().resolve_texture_data(resource_name)
