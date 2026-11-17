"""Tests for one firefly: movement, bouncing, blinking."""

import math
import random

import pytest

from termfireflies.firefly import MAX_SPEED, Firefly
from termfireflies.palette import get_palette


def make_fly(**overrides):
    defaults = dict(
        x=10.0, y=5.0, vx=1.0, vy=0.0,
        phase=0.0, blink_period=2.0,
        color=(190, 255, 120), glow=1.0,
    )
    defaults.update(overrides)
    return Firefly(**defaults)


def test_brightness_pulses_between_dark_and_full():
    fly = make_fly(phase=0.0, blink_period=2.0, glow=1.0)
    assert fly.brightness(0.0) == pytest.approx(0.0, abs=1e-9)
    assert fly.brightness(1.0) == pytest.approx(1.0, abs=1e-9)  # peak mid-cycle
    assert fly.brightness(2.0) == pytest.approx(0.0, abs=1e-9)  # back to dark
    # Glow caps the peak: a dim firefly never flashes at full brightness.
    dim = make_fly(glow=0.5)
    assert dim.brightness(1.0) == pytest.approx(0.5, abs=1e-9)


def test_brightness_never_leaves_0_to_1():
    rng = random.Random(7)
    fly = Firefly.random(80, 24, get_palette("green"), rng)
    for step in range(200):
        b = fly.brightness(step * 0.13)
        assert 0.0 <= b <= 1.0


def test_update_moves_by_velocity():
    fly = make_fly(x=10.0, y=5.0, vx=2.0, vy=0.0)
    fly.update(0.1, 80, 24, None, random.Random(1))
    # Heading wanders a little, so x moves roughly 0.2, y barely moves.
    assert fly.x == pytest.approx(10.2, abs=0.05)
    assert abs(fly.y - 5.0) < 0.05


def test_update_bounces_off_walls():
    fly = make_fly(x=0.1, y=5.0, vx=-2.0, vy=0.0)
    fly.update(1.0, 80, 24, None, random.Random(1))
    assert fly.x >= 0
    assert fly.vx > 0  # now heading back into the terminal
    fly = make_fly(x=79.9, y=5.0, vx=2.0, vy=0.0)
    fly.update(1.0, 80, 24, None, random.Random(1))
    assert fly.x <= 79
    assert fly.vx < 0


def test_update_never_exceeds_max_speed():
    rng = random.Random(3)
    fly = make_fly(vx=100.0, vy=100.0)
    for _ in range(50):
        fly.update(0.1, 80, 24, (40.0, 12.0), rng)
    assert math.hypot(fly.vx, fly.vy) <= MAX_SPEED + 1e-9


def test_attract_pulls_towards_point():
    rng = random.Random(5)
    fly = make_fly(x=10.0, y=12.0, vx=0.0, vy=0.0)
    start_x = fly.x
    for _ in range(20):
        fly.update(0.1, 80, 24, (70.0, 12.0), rng)
    assert fly.x > start_x  # drifted right, towards the meeting point


def test_random_spawn_stays_in_bounds():
    rng = random.Random(42)
    for _ in range(100):
        fly = Firefly.random(80, 24, get_palette("amber"), rng)
        assert 0 <= fly.x < 80
        assert 0 <= fly.y < 24
        assert 1.5 <= fly.blink_period <= 6.0
        assert 0.6 <= fly.glow <= 1.0
