"""Tests for palettes and the renderer."""

import pytest

from termfireflies.palette import DEFAULT_PALETTE, get_palette, list_palettes
from termfireflies.renderer import glyph_for_brightness, render


def test_get_palette_is_case_insensitive():
    assert get_palette("GREEN") == get_palette("green")
    assert get_palette("Green") == get_palette("green")


def test_get_palette_rejects_unknown_names():
    with pytest.raises(ValueError, match="unknown palette"):
        get_palette("octarine")
    with pytest.raises(ValueError, match="unknown palette"):
        get_palette("")


def test_list_palettes_includes_default():
    assert DEFAULT_PALETTE in list_palettes()
    assert len(list_palettes()) >= 4


def test_glyph_progression():
    assert glyph_for_brightness(0.0) == "."
    assert glyph_for_brightness(1.0) == "@"
    # Brighter means a "heavier" glyph, never the other way round.
    glyphs = [glyph_for_brightness(b / 10) for b in range(11)]
    assert glyphs == sorted(glyphs, key=".,*oO@".index)


def test_render_dimensions():
    frame = [(2, 1, 0.9, (255, 255, 255))]
    out = render(frame, 5, 3)
    lines = out.split("\n")
    assert len(lines) == 3
    # ANSI codes make lines long; strip them to check the visible width.
    import re
    visible = [re.sub(r"\x1b\[[0-9;]*m", "", line) for line in lines]
    assert all(len(line) <= 5 for line in visible)
    assert visible[1][2] == "@"  # brightest glyph at the firefly's cell


def test_render_skips_dim_fireflies():
    frame = [(1, 0, 0.01, (255, 255, 255))]
    assert render(frame, 5, 3, use_color=False).split("\n")[0].strip() == ""


def test_render_brightest_wins_a_shared_cell():
    frame = [
        (2, 1, 0.3, (255, 0, 0)),
        (2, 1, 0.9, (0, 255, 0)),
    ]
    out = render(frame, 5, 3, use_color=False)
    assert out.split("\n")[1][2] == "@"


def test_render_ignores_out_of_bounds_fireflies():
    frame = [(99, 99, 1.0, (255, 255, 255)), (-1, 0, 1.0, (255, 255, 255))]
    out = render(frame, 5, 3, use_color=False)
    assert out.strip() == ""


def test_render_rejects_zero_size():
    with pytest.raises(ValueError):
        render([], 0, 10)
    with pytest.raises(ValueError):
        render([], 10, 0)


def test_render_no_color_has_no_escape_codes():
    frame = [(1, 1, 0.8, (255, 255, 0))]
    assert "\x1b" not in render(frame, 5, 3, use_color=False)
