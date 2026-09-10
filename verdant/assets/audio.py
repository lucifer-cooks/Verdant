"""Audio resolution and redirection layer for Verdant."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from verdant.assets.paths import (
    LEGACY_MUSIC_DIR,
    LEGACY_NEWSOUND_DIR,
    VERDANT_THEME_DIR,
)
from verdant.assets.registry import AssetRegistry, AssetResolutionResult


class AudioRedirectionManager:
    """Manages audio cue resolution between original Verdant audio and legacy sound pools."""

    _instance: Optional[AudioRedirectionManager] = None

    def __init__(self, registry: Optional[AssetRegistry] = None) -> None:
        self._registry = registry or AssetRegistry.get_instance()
        self._stats = {
            "total_requests": 0,
            "verdant_served": 0,
            "fallback_served": 0,
        }
        self._last_resolutions: Dict[str, AssetResolutionResult] = {}

    @classmethod
    def get_instance(cls) -> AudioRedirectionManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    @property
    def stats(self) -> Dict[str, int]:
        return dict(self._stats)

    def resolve_audio_file(self, cue_or_relpath: str) -> Optional[Path]:
        """Resolve a sound cue or relative sound path to an absolute filesystem Path."""
        self._stats["total_requests"] += 1
        res = self._registry.resolve_audio(cue_or_relpath)
        self._last_resolutions[cue_or_relpath] = res

        if not res.is_fallback and res.resolved_source is not None:
            if isinstance(res.resolved_source, Path) and res.resolved_source.is_file():
                self._stats["verdant_served"] += 1
                return res.resolved_source
            elif isinstance(res.resolved_source, str):
                p = Path(res.resolved_source)
                if p.is_file():
                    self._stats["verdant_served"] += 1
                    return p

        # Fallback to legacy newsound or music directories
        self._stats["fallback_served"] += 1
        rel = str(res.resolved_source or cue_or_relpath).replace("\\", "/")
        if rel.startswith("music/"):
            candidate = LEGACY_MUSIC_DIR / rel[6:]
        else:
            candidate = LEGACY_NEWSOUND_DIR / rel

        if candidate.is_file():
            return candidate

        return None

    def discover_original_sound_files(self) -> List[Tuple[str, Path]]:
        """Discover all original audio files provided under the active theme directory."""
        active_theme_dir = self._registry._theme_mgr.get_active_theme_dir()
        audio_dir = active_theme_dir / "audio"
        discovered: List[Tuple[str, Path]] = []
        if not audio_dir.is_dir():
            return discovered

        for root, _, files in os.walk(audio_dir):
            for file_name in files:
                if file_name.lower().endswith(".ogg"):
                    full_path = Path(root) / file_name
                    rel_name = full_path.relative_to(audio_dir).as_posix()
                    sound_key = os.path.splitext(rel_name)[0].replace("/", ".")
                    discovered.append((sound_key, full_path))
        return discovered


def resolve_audio_file(cue_or_relpath: str) -> Optional[Path]:
    """Convenience functional interface for resolving audio files."""
    return AudioRedirectionManager.get_instance().resolve_audio_file(cue_or_relpath)
