"""Tests for the swarm: size, gathering, snapshots, seeds."""

import pytest

from termfireflies.palette import get_palette
from termfireflies.swarm import Swarm


def test_swarm_has_the_requested_count():
    swarm = Swarm(25, 80, 24, get_palette("green"), seed=1)
    assert len(swarm) == 25


def test_swarm_rejects_bad_inputs():
    with pytest.raises(ValueError):
        Swarm(0, 80, 24, get_palette("green"))
    with pytest.raises(ValueError):
        Swarm(5, 0, 24, get_palette("green"))
    with pytest.raises(ValueError):
        Swarm(5, 80, 24, [])


def test_update_keeps_every_firefly_in_bounds():
    swarm = Swarm(60, 80, 24, get_palette("blue"), seed=2)
    for _ in range(200):
        swarm.update(0.05, 80, 24)
    for fly in swarm.fireflies:
        assert 0 <= fly.x < 80
        assert 0 <= fly.y < 24


def test_update_survives_a_resize():
    swarm = Swarm(10, 80, 24, get_palette("green"), seed=3)
    swarm.update(0.1, 40, 10)  # terminal shrank
    for fly in swarm.fireflies:
        assert 0 <= fly.x < 40
        assert 0 <= fly.y < 10


def test_same_seed_same_swarm():
    a = Swarm(10, 80, 24, get_palette("green"), seed=99)
    b = Swarm(10, 80, 24, get_palette("green"), seed=99)
    for fly_a, fly_b in zip(a.fireflies, b.fireflies):
        assert (fly_a.x, fly_a.y) == (fly_b.x, fly_b.y)
        assert fly_a.color == fly_b.color
        assert fly_a.blink_period == fly_b.blink_period


def test_snapshot_shape_and_ranges():
    swarm = Swarm(5, 80, 24, get_palette("fire"), seed=4)
    frame = swarm.snapshot(t=1.0)
    assert len(frame) == 5
    for x, y, brightness, color in frame:
        assert isinstance(x, int) and isinstance(y, int)
        assert 0 <= x < 80 and 0 <= y < 24
        assert 0.0 <= brightness <= 1.0
        assert len(color) == 3
