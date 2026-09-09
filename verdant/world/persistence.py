"""Persistence boundary for VERDANT simulation state.

This deliberately avoids touching the legacy Minecraft save format. It keeps the
VERDANT data serialized separately so future world systems can evolve without
corrupting the original Indev save data.
"""

from __future__ import annotations

from typing import Any, Dict


class VerdantStatePersistence:
    """Minimal serialization layer for VERDANT simulation state."""

    VERSION = 1

    @staticmethod
    def serialize(state):
        return {
            'version': VerdantStatePersistence.VERSION,
            'state': state.to_dict(),
        }

    @staticmethod
    def deserialize(payload: Dict[str, Any]):
        from .state import VerdantWorldState

        if not payload:
            return VerdantWorldState()

        version = int(payload.get('version', 1))
        state_data = payload.get('state', {})
        state = VerdantWorldState.from_dict(state_data)
        state.simulation_version = version
        return state
