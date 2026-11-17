"""One firefly: position, drift, and its blink cycle.

A firefly is deliberately dumb. It has a position, a slow velocity, and a
blink period. The swarm (see swarm.py) is what makes them look alive —
this module just moves one dot and decides how bright it is right now.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .palette import RGB

# Speed limit, in terminal cells per second. Faster than this and the
# fireflies stop looking like insects and start looking like a screensaver
# from 1998. (Okay, it *is* a screensaver. You know what I mean.)
MAX_SPEED = 6.0

# How much a firefly's heading can wander per second, in radians.
# Small values give lazy arcs; big values give jittery moths.
WANDER_STRENGTH = 0.9

# How strongly a firefly is pulled towards the swarm's meeting point.
ATTRACT_STRENGTH = 2.5


@dataclass
class Firefly:
    """A single firefly drifting around the terminal."""

    x: float
    y: float
    vx: float
    vy: float
    # Where in its blink cycle it starts, in turns (0..1).
    phase: float
    # Seconds per full blink cycle. Short = twitchy, long = lazy.
    blink_period: float
    color: RGB
    # Peak brightness, 0..1. Some fireflies are just dimmer than others.
    glow: float = 1.0

    @classmethod
    def random(cls, width: int, height: int, colors: list[RGB],
               rng: random.Random) -> "Firefly":
        """Spawn a firefly at a random spot with a random drift and blink."""
        angle = rng.uniform(0, 2 * math.pi)
        speed = rng.uniform(0.5, 2.5)
        return cls(
            x=rng.uniform(0, max(width - 1, 0)),
            y=rng.uniform(0, max(height - 1, 0)),
            vx=math.cos(angle) * speed,
            vy=math.sin(angle) * speed,
            phase=rng.uniform(0, 1),
            blink_period=rng.uniform(1.5, 6.0),
            color=rng.choice(colors),
            glow=rng.uniform(0.6, 1.0),
        )

    def brightness(self, t: float) -> float:
        """How bright this firefly is at time ``t`` (seconds), 0..1.

        A blink is a smooth pulse: dark, swelling to full glow, fading
        back to dark. Squaring the sine makes the bright flash short and
        the dark stretch long, which is how real fireflies read — mostly
        nothing, then a sudden wink.
        """
        cycle = (t / self.blink_period + self.phase) % 1.0
        pulse = math.sin(math.pi * cycle)
        return self.glow * pulse * pulse

    def update(self, dt: float, width: int, height: int,
               attract: tuple[float, float] | None,
               rng: random.Random) -> None:
        """Advance this firefly by ``dt`` seconds.

        The heading wanders a little every frame (random walk), and if the
        swarm has a meeting point, this firefly drifts gently towards it.
        Hitting a wall bounces it back in — fireflies never leave the
        terminal.
        """
        # Wander: rotate the heading by a small random amount.
        heading = math.atan2(self.vy, self.vx)
        heading += rng.uniform(-WANDER_STRENGTH, WANDER_STRENGTH) * dt
        speed = min(math.hypot(self.vx, self.vy), MAX_SPEED)
        self.vx = math.cos(heading) * speed
        self.vy = math.sin(heading) * speed

        # Drift towards the meeting point, if the swarm has one.
        if attract is not None:
            ax, ay = attract
            dx, dy = ax - self.x, ay - self.y
            dist = math.hypot(dx, dy)
            if dist > 1.0:
                pull = ATTRACT_STRENGTH * dt / dist
                self.vx += dx * pull
                self.vy += dy * pull
                # Re-clamp after the pull so nothing accelerates forever.
                speed = math.hypot(self.vx, self.vy)
                if speed > MAX_SPEED:
                    self.vx = self.vx / speed * MAX_SPEED
                    self.vy = self.vy / speed * MAX_SPEED

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Bounce off the walls. Clamp first so a fast firefly can't get
        # stuck outside the grid for a frame.
        if self.x < 0:
            self.x = 0
            self.vx = abs(self.vx)
        elif self.x > width - 1:
            self.x = width - 1
            self.vx = -abs(self.vx)
        if self.y < 0:
            self.y = 0
            self.vy = abs(self.vy)
        elif self.y > height - 1:
            self.y = height - 1
            self.vy = -abs(self.vy)
