"""Ordered deterministic system manager for VERDANT simulation systems."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class VerdantSimulationManager:
    """Lightweight ordered system registry and tick controller."""

    def __init__(self, context=None):
        self.context = context
        self.systems: List[Any] = []
        self.system_order: Dict[str, int] = {}

    def register(self, system):
        if system is None:
            return False

        name = getattr(system, 'name', system.__class__.__name__)
        for existing in self.systems:
            existing_name = getattr(existing, 'name', existing.__class__.__name__)
            if existing_name == name:
                return False

        self.systems.append(system)
        self.system_order[name] = len(self.systems) - 1
        return True

    def initialize(self, context=None):
        active_context = context or self.context
        for system in self.systems:
            system.initialize(active_context)
        return self

    def update(self, context=None, delta_ticks: int = 1):
        active_context = context or self.context
        for system in self.systems:
            system.update(active_context, delta_ticks=delta_ticks)
        return self

    def shutdown(self, context=None):
        active_context = context or self.context
        for system in self.systems:
            system.shutdown(active_context)
        self.systems.clear()
        self.system_order.clear()
        return self

    def snapshot(self):
        return {
            'registered_systems': [
                getattr(system, 'name', system.__class__.__name__)
                for system in self.systems
            ],
            'count': len(self.systems),
        }
