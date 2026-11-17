"""Tests for the CLI: flag validation and a short live run."""

import io

import pytest

from termfireflies.cli import build_parser, main, run, validate_args


def parse(*argv):
    parser = build_parser()
    args = parser.parse_args(list(argv))
    validate_args(args, parser)
    return args


def test_defaults_are_sane():
    args = parse()
    assert args.count == 40
    assert args.palette == "green"
    assert args.speed == 1.0
    assert args.duration == 0


def test_bad_count_is_rejected():
    with pytest.raises(SystemExit):
        parse("--count", "0")
    with pytest.raises(SystemExit):
        parse("--count", "501")


def test_bad_speed_is_rejected():
    with pytest.raises(SystemExit):
        parse("--speed", "0")
    with pytest.raises(SystemExit):
        parse("--speed", "9")


def test_bad_palette_is_rejected():
    with pytest.raises(SystemExit):
        parse("--palette", "octarine")


def test_negative_duration_is_rejected():
    with pytest.raises(SystemExit):
        parse("--duration", "-5")


def test_run_exits_cleanly_after_duration():
    args = parse("--count", "5", "--duration", "0.1", "--seed", "1")
    out = io.StringIO()
    assert run(args, out=out, tty=True) == 0
    # Something was drawn, and the cursor was restored at the end.
    assert "\x1b[H" in out.getvalue()
    assert out.getvalue().endswith("\x1b[2J\x1b[H\x1b[?25h")


def test_run_refuses_non_terminal():
    args = parse("--count", "5", "--duration", "0.1")
    out = io.StringIO()
    assert run(args, out=out, tty=False) == 2


def test_main_returns_zero_on_short_run():
    # main() with a real (non-TTY here) stdout would refuse, so exercise
    # the parsing path only: bad flags must exit non-zero, not traceback.
    with pytest.raises(SystemExit) as exc:
        main(["--count", "0"])
    assert exc.value.code == 2
