"""Base abstraction for future VERDANT simulation systems."""

from __future__ import annotations


class VerdantSystem:
    """Minimal lifecycle interface for future simulation subsystems."""

    def __init__(self, name=None):
        self.name = name or self.__class__.__name__
        self.initialized = False

    def initialize(self, context=None):
        self.initialized = True
        return self

    def update(self, context=None, delta_ticks: int = 1):
        return None

    def shutdown(self, context=None):
        self.initialized = False
        return self
