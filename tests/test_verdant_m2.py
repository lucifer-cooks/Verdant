import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verdant.world.state import VerdantWorldState
from verdant.world.clock import VerdantSimulationClock
from verdant.world.queries import VerdantWorldQueryBoundary
from verdant.world.persistence import VerdantStatePersistence
from verdant.simulation.system import VerdantSystem
from verdant.simulation.manager import VerdantSimulationManager


class ExampleSystem(VerdantSystem):
    def __init__(self, name='example'):
        super().__init__(name=name)
        self.seen_tick = 0

    def update(self, context=None, delta_ticks: int = 1):
        self.seen_tick += int(delta_ticks)


def test_world_state_initializes():
    state = VerdantWorldState()
    assert state.simulation_version == 1
    assert state.current_season == 'spring'
    assert state.weather == 'clear'


def test_simulation_clock_advances():
    state = VerdantWorldState()
    clock = VerdantSimulationClock(state, simulation_speed=2)
    clock.advance(5)
    assert clock.elapsed_ticks == 10
    assert clock.get_current_season() == 'spring'


def test_manager_registers_and_updates_in_order():
    manager = VerdantSimulationManager()
    s1 = ExampleSystem('s1')
    s2 = ExampleSystem('s2')
    assert manager.register(s1) is True
    assert manager.register(s2) is True
    assert manager.register(s1) is False
    manager.initialize()
    manager.update(delta_ticks=3)
    assert s1.seen_tick == 3
    assert s2.seen_tick == 3


def test_persistence_roundtrip():
    state = VerdantWorldState(world_age_ticks=42, current_season='autumn', weather='rain')
    payload = VerdantStatePersistence.serialize(state)
    restored = VerdantStatePersistence.deserialize(payload)
    assert restored.world_age_ticks == 42
    assert restored.current_season == 'autumn'
    assert restored.weather == 'rain'


def test_queries_and_tick_hook_support():
    state = VerdantWorldState()
    clock = VerdantSimulationClock(state)
    query = VerdantWorldQueryBoundary()
    assert query.get_world_time() == 0
    clock.advance(10)
    assert clock.elapsed_ticks == 10
    assert query.snapshot(0, 0, 0)['world_time'] == 0
