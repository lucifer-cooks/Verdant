"""Deterministic simulation clock for VERDANT.

This layer advances from the existing game tick lifecycle and is intentionally
not a second game loop. It exposes VERDANT time without duplicating the legacy
world logic.
"""

from __future__ import annotations

from verdant.simulation.system import VerdantSystem


class VerdantSimulationClock(VerdantSystem):
    """Small deterministic tick-driven clock for VERDANT worlds."""

    SEASONS = ('spring', 'summer', 'autumn', 'winter')

    def __init__(self, world_state=None, *, name='verdant_clock', simulation_speed: int = 1, seed: int = 0):
        super().__init__(name=name)
        self.world_state = world_state
        self.simulation_speed = max(1, int(simulation_speed))
        self.seed = int(seed)
        self.elapsed_ticks = 0
        self.day = 0
        self.season_index = 0
        self.last_legacy_world_time = 0

    def initialize(self, context=None):
        self.initialized = True
        return self

    def update(self, context=None, delta_ticks: int = 1):
        self.advance(delta_ticks)
        return self.elapsed_ticks

    def advance(self, delta_ticks: int = 1):
        """Advance by a deterministic integer number of VERDANT ticks."""
        delta = max(0, int(delta_ticks))
        self.elapsed_ticks += delta * self.simulation_speed
        self.day = self.elapsed_ticks // 24000
        self.season_index = self.day % len(self.SEASONS)

        if self.world_state is not None:
            self.world_state.world_age_ticks = self.elapsed_ticks
            self.world_state.elapsed_simulation_ticks = self.elapsed_ticks
            self.world_state.current_season = self.SEASONS[self.season_index]

        return self.elapsed_ticks

    def set_world_state(self, world_state):
        self.world_state = world_state
        return self

    def get_day_phase(self):
        return self.elapsed_ticks % 24000

    def get_current_season(self):
        return self.SEASONS[self.season_index % len(self.SEASONS)]

    def snapshot(self):
        return {
            'elapsed_ticks': self.elapsed_ticks,
            'day': self.day,
            'season': self.get_current_season(),
            'seed': self.seed,
            'simulation_speed': self.simulation_speed,
        }
