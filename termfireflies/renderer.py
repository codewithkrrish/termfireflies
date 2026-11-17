"""Turn a swarm snapshot into one frame of terminal text.

Rendering is a grid problem: several fireflies can land on the same cell,
so the brightest one wins that cell. Brightness picks the glyph (a dim
firefly is a dot, a full flash is a star) and scales the colour, so a
fading firefly actually looks like it is fading instead of blinking out.
"""

from __future__ import annotations

from .palette import RGB

# Fireflies dimmer than this are invisible — drawing them would just be
# noise, and a real firefly spends most of its cycle dark anyway.
MIN_VISIBLE_BRIGHTNESS = 0.06

# Glyphs from faintest to brightest. Plain ASCII on purpose: some
# terminals mangle unicode, and a screensaver should not depend on fonts.
_GLYPHS = ".,*oO@"


def glyph_for_brightness(brightness: float) -> str:
    """Pick the character for a firefly at this brightness (0..1)."""
    clamped = max(0.0, min(1.0, brightness))
    index = int(clamped * len(_GLYPHS))
    if index >= len(_GLYPHS):
        index = len(_GLYPHS) - 1
    return _GLYPHS[index]


def _dim(color: RGB, brightness: float) -> RGB:
    """Scale a colour down by brightness, keeping a faint glow at the bottom."""
    factor = 0.25 + 0.75 * max(0.0, min(1.0, brightness))
    return (
        int(color[0] * factor),
        int(color[1] * factor),
        int(color[2] * factor),
    )


def render(frame: list[tuple[int, int, float, RGB]], width: int,
           height: int, use_color: bool = True) -> str:
    """Render one frame as a string of ``height`` lines.

    ``frame`` is a snapshot from :meth:`swarm.Swarm.snapshot`. Cells with
    no firefly are spaces. When two fireflies share a cell, the brighter
    one wins. The result has no trailing newline — the caller owns cursor
    movement.
    """
    if width < 1 or height < 1:
        raise ValueError(f"cannot render a {width}x{height} frame")

    # Brightest firefly per cell.
    cells: dict[tuple[int, int], tuple[float, RGB]] = {}
    for x, y, brightness, color in frame:
        if brightness < MIN_VISIBLE_BRIGHTNESS:
            continue
        if not (0 <= x < width and 0 <= y < height):
            continue
        current = cells.get((x, y))
        if current is None or brightness > current[0]:
            cells[(x, y)] = (brightness, color)

    lines: list[str] = []
    for row in range(height):
        parts: list[str] = []
        for col in range(width):
            cell = cells.get((col, row))
            if cell is None:
                parts.append(" ")
                continue
            brightness, color = cell
            glyph = glyph_for_brightness(brightness)
            if use_color:
                r, g, b = _dim(color, brightness)
                parts.append(f"\x1b[38;2;{r};{g};{b}m{glyph}\x1b[0m")
            else:
                parts.append(glyph)
        lines.append("".join(parts).rstrip())
    return "\n".join(lines)
