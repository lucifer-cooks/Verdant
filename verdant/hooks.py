"""No-op integration hooks for future VERDANT systems.

The legacy game must keep working exactly as baseline. These hooks are designed
so future VERDANT modules can plug into legacy lifecycle points without changing
current gameplay behavior.
"""

from __future__ import annotations


class VerdantHooks:
    """Minimal safe extension edge for legacy lifecycle events.

    Every method is intentionally passive in M1. Future milestones can override or
    extend these hooks without editing the baseline engine directly.
    """

    @staticmethod
    def on_game_startup(mc):
        return None

    @staticmethod
    def before_world_generation(mc, size, shape, level_type, theme):
        return None

    @staticmethod
    def after_world_generation(mc, world):
        return None

    @staticmethod
    def before_world_tick(world):
        return None

    @staticmethod
    def after_world_tick(world):
        return None

    @staticmethod
    def before_entity_update(world, entity):
        return None

    @staticmethod
    def after_entity_update(world, entity):
        return None

    @staticmethod
    def before_render(mc, alpha):
        return None

    @staticmethod
    def after_render(mc, alpha):
        return None

    @staticmethod
    def before_world_change(mc, world):
        return None

    @staticmethod
    def after_world_change(mc, world):
        return None

    @staticmethod
    def before_save(world, file_path):
        return None

    @staticmethod
    def after_save(world, file_path):
        return None

    @staticmethod
    def before_load(world, file_path):
        return None

    @staticmethod
    def after_load(world, file_path):
        return None
