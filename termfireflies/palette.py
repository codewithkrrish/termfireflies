"""Colour palettes for the fireflies.

Each palette is a list of RGB triples. A firefly picks one colour when it
is born and keeps it for life — that is what makes a swarm look like one
species instead of a bag of random LEDs.
"""

from __future__ import annotations

RGB = tuple[int, int, int]

PALETTES: dict[str, list[RGB]] = {
    # The classic: warm summer-evening green.
    "green": [
        (190, 255, 120),
        (150, 255, 80),
        (220, 255, 170),
        (120, 220, 60),
    ],
    # Porch-light amber.
    "amber": [
        (255, 200, 90),
        (255, 170, 40),
        (255, 220, 150),
        (230, 140, 30),
    ],
    # Cold blue, for night-owl terminals.
    "blue": [
        (140, 200, 255),
        (90, 160, 255),
        (180, 220, 255),
        (100, 120, 255),
    ],
    # Embers rising off a campfire.
    "fire": [
        (255, 120, 60),
        (255, 180, 80),
        (255, 90, 40),
        (255, 220, 120),
    ],
    # Soft violet, a little dreamy.
    "violet": [
        (200, 150, 255),
        (170, 110, 255),
        (230, 190, 255),
        (150, 90, 230),
    ],
    # One of each — a mixed swarm.
    "rainbow": [
        (255, 120, 120),
        (255, 200, 90),
        (150, 255, 120),
        (120, 200, 255),
        (210, 140, 255),
        (255, 150, 200),
    ],
}

DEFAULT_PALETTE = "green"


def get_palette(name: str) -> list[RGB]:
    """Return the colours for ``name`` (case-insensitive).

    Raises:
        ValueError: if there is no palette by that name.
    """
    try:
        return list(PALETTES[name.lower()])
    except KeyError:
        raise ValueError(
            f"unknown palette {name!r}; pick one of: {', '.join(sorted(PALETTES))}"
        ) from None


def list_palettes() -> list[str]:
    """Return the available palette names, sorted."""
    return sorted(PALETTES)
