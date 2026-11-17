"""Command line entry point: parse flags, run the animation loop.

Kept thin on purpose — all the behaviour lives in firefly.py, swarm.py
and renderer.py so it can be tested without a terminal attached.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import shutil
import signal
import sys
import time
from types import FrameType
from typing import TextIO

from . import __version__
from .palette import DEFAULT_PALETTE, get_palette, list_palettes
from .renderer import render
from .swarm import Swarm

# Frames per second. 30 is smooth enough for drifting dots and light
# enough that a slow SSH session does not fall behind.
TARGET_FPS = 30

# A terminal smaller than this is not worth animating in.
MIN_WIDTH = 20
MIN_HEIGHT = 5

# Hard ceiling on fireflies: beyond this the frame is just a wall of
# dots, and rendering gets slow on weak terminals.
MAX_FIREFLIES = 500

# Ctrl-C should stop the show cleanly (cursor back, screen cleared),
# not print a traceback over the animation.
_EXIT_SIGNALS = (signal.SIGINT, signal.SIGTERM)


class TerminalTooSmallError(Exception):
    """Raised when the terminal is too small to animate in."""


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="termfireflies",
        description="Fireflies drifting, blinking and swarming in your terminal.",
    )
    parser.add_argument(
        "-n", "--count", type=int, default=40,
        help="how many fireflies (1-500, default 40)",
    )
    parser.add_argument(
        "-s", "--speed", type=float, default=1.0,
        help="drift speed multiplier, 0.1-5 (default 1)",
    )
    parser.add_argument(
        "-p", "--palette", default=DEFAULT_PALETTE,
        help=f"colour palette: {', '.join(list_palettes())} (default green)",
    )
    parser.add_argument(
        "-d", "--duration", type=float, default=0,
        help="stop after this many seconds (0 = run until you press q or Ctrl-C)",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="seed the random generator for a repeatable swarm",
    )
    parser.add_argument(
        "--no-color", action="store_true",
        help="plain characters, no colour (for terminals without truecolor)",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )
    return parser


def validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    """Check the parsed flags and bail out with a human message if bad."""
    if not 1 <= args.count <= MAX_FIREFLIES:
        parser.error(f"--count must be between 1 and {MAX_FIREFLIES}, got {args.count}")
    if not 0.1 <= args.speed <= 5.0:
        parser.error(f"--speed must be between 0.1 and 5, got {args.speed}")
    if args.duration < 0:
        parser.error(f"--duration cannot be negative, got {args.duration}")
    try:
        get_palette(args.palette)
    except ValueError as exc:
        parser.error(str(exc))


@contextlib.contextmanager
def _raw_terminal():
    """Put stdin into raw mode so a single 'q' quits, if possible.

    Best-effort only: if stdin is not a TTY (or termios is missing, e.g.
    on Windows), this quietly does nothing and quitting falls back to
    Ctrl-C.
    """
    try:
        import termios
        import tty
    except ImportError:
        yield
        return
    if not sys.stdin.isatty():
        yield
        return
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _quit_requested() -> bool:
    """True if the user pressed 'q' (non-blocking, raw mode only)."""
    try:
        import select
    except ImportError:
        return False
    if not sys.stdin.isatty():
        return False
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    if not ready:
        return False
    key = os.read(sys.stdin.fileno(), 1)
    return key in (b"q", b"Q", b"\x03")  # q, Q, or Ctrl-C


def run(args: argparse.Namespace, out: TextIO | None = None,
        tty: bool | None = None) -> int:
    """Run the animation. Returns an exit code (0 = clean stop)."""
    out = out if out is not None else sys.stdout
    is_tty = tty if tty is not None else out.isatty()
    if not is_tty:
        print("termfireflies needs a terminal — pipe it nowhere, just run it.",
              file=sys.stderr)
        return 2

    size = shutil.get_terminal_size()
    if size.columns < MIN_WIDTH or size.lines < MIN_HEIGHT:
        print(
            f"termfireflies needs at least a {MIN_WIDTH}x{MIN_HEIGHT} terminal, "
            f"yours is {size.columns}x{size.lines}.",
            file=sys.stderr,
        )
        return 2

    colors = get_palette(args.palette)
    swarm = Swarm(args.count, size.columns, size.lines, colors, seed=args.seed)
    start = time.monotonic()
    frame_interval = 1.0 / TARGET_FPS

    # Hide the cursor and clear the screen; everything is restored in
    # the finally, even on Ctrl-C.
    out.write("\x1b[?25l\x1b[2J")
    out.flush()
    stop = False

    def _handle_signal(signum: int, frame: FrameType | None) -> None:
        nonlocal stop
        stop = True

    old_handlers = {}
    for sig in _EXIT_SIGNALS:
        try:
            old_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, _handle_signal)
        except (ValueError, OSError):
            # Not the main thread, or signal unavailable — the loop's
            # KeyboardInterrupt fallback still covers Ctrl-C.
            pass

    try:
        with _raw_terminal():
            while not stop:
                now = time.monotonic()
                elapsed = now - start
                if args.duration and elapsed >= args.duration:
                    break
                size = shutil.get_terminal_size()
                swarm.update(frame_interval * args.speed, size.columns, size.lines)
                frame = render(
                    swarm.snapshot(elapsed),
                    size.columns, size.lines,
                    use_color=not args.no_color,
                )
                out.write("\x1b[H" + frame)
                out.flush()
                if _quit_requested():
                    break
                # Sleep off the rest of the frame budget.
                spent = time.monotonic() - now
                if spent < frame_interval:
                    time.sleep(frame_interval - spent)
    except KeyboardInterrupt:
        pass
    finally:
        for sig, handler in old_handlers.items():
            try:
                signal.signal(sig, handler)
            except (ValueError, OSError):
                pass
        out.write("\x1b[2J\x1b[H\x1b[?25h")
        out.flush()
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: parse, validate, run."""
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_args(args, parser)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
