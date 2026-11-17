"""The swarm: a flock of fireflies and their occasional meeting point.

The one behaviour that makes this look like fireflies instead of dust is
the meeting point. Every so often the swarm picks a random spot in the
terminal and drifts towards it for a few seconds, then scatters again.
Real fireflies gather like that — or at least, that is what it looks like
from a porch at dusk, and that is good enough for a screensaver.
"""

from __future__ import annotations

import random
import time

from .firefly import Firefly
from .palette import RGB

# How long the swarm gathers at a meeting point, in seconds.
GATHER_MIN = 4.0
GATHER_MAX = 7.0

# How long it drifts freely between gatherings, in seconds.
ROAM_MIN = 3.0
ROAM_MAX = 8.0


class Swarm:
    """A group of fireflies moving around one terminal."""

    def __init__(self, count: int, width: int, height: int,
                 colors: list[RGB], seed: int | None = None) -> None:
        if count < 1:
            raise ValueError(f"swarm needs at least 1 firefly, got {count}")
        if width < 1 or height < 1:
            raise ValueError(f"terminal must be at least 1x1, got {width}x{height}")
        if not colors:
            raise ValueError("swarm needs at least one colour")
        self.rng = random.Random(seed)
        self.fireflies = [
            Firefly.random(width, height, colors, self.rng)
            for _ in range(count)
        ]
        self.width = width
        self.height = height
        # Where the swarm is gathering right now, or None while roaming.
        self.meeting_point: tuple[float, float] | None = None
        self._mode_until = time.monotonic() + self.rng.uniform(ROAM_MIN, ROAM_MAX)

    def __len__(self) -> int:
        return len(self.fireflies)

    def update(self, dt: float, width: int, height: int) -> None:
        """Advance the whole swarm by ``dt`` seconds."""
        self.width = width
        self.height = height
        now = time.monotonic()
        if now >= self._mode_until:
            if self.meeting_point is None:
                # Time to gather: pick a spot and head for it.
                self.meeting_point = (
                    self.rng.uniform(0, max(width - 1, 0)),
                    self.rng.uniform(0, max(height - 1, 0)),
                )
                self._mode_until = now + self.rng.uniform(GATHER_MIN, GATHER_MAX)
            else:
                # Gathering over: scatter and roam for a while.
                self.meeting_point = None
                self._mode_until = now + self.rng.uniform(ROAM_MIN, ROAM_MAX)
        for fly in self.fireflies:
            fly.update(dt, width, height, self.meeting_point, self.rng)

    def snapshot(self, t: float) -> list[tuple[int, int, float, RGB]]:
        """One frame of the swarm: (column, row, brightness, colour) per fly."""
        return [
            (int(fly.x), int(fly.y), fly.brightness(t), fly.color)
            for fly in self.fireflies
        ]
