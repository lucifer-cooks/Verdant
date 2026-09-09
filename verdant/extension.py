"""Central VERDANT runtime entry point for the extension layer.

This class is intentionally minimal and passive in M1. It defines the future
contract for integrating VERDANT systems with the legacy game world lifecycle.
"""

from __future__ import annotations

from .config import VERDANT_CONFIG
from .hooks import VerdantHooks


class VerdantGameExtension:
    """Small runtime shell for future VERDANT subsystems."""

    def __init__(self, name='VERDANT', enabled=True):
        self.name = name
        self.enabled = enabled and VERDANT_CONFIG['enabled']
        self.safe_mode = VERDANT_CONFIG['safe_mode']

    def bootstrap(self, minecraft=None):
        if not self.enabled:
            return None
        VerdantHooks.on_game_startup(minecraft)
        return self

    def attach_to_world(self, world):
        if not self.enabled or world is None:
            return None
        return world

    def attach_to_render(self, minecraft, alpha):
        if not self.enabled:
            return None
        VerdantHooks.before_render(minecraft, alpha)
        VerdantHooks.after_render(minecraft, alpha)
        return None


def create_verdant_extension(enabled=True):
    return VerdantGameExtension('VERDANT', enabled=enabled)
