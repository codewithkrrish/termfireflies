# termfireflies

Fireflies drifting, blinking and swarming in your terminal. Zero dependencies, pure Python, one command.

I built this because I kept opening those "relaxing screensaver" tabs and closing them ten seconds later — a browser tab is a weird place to watch fireflies. The terminal is already open all day, so the fireflies may as well live there.

```
termfireflies
```

```
        .                    *
                  o
     *                        .        O
              .      *
                        o              .
   .           *             .
                      O
```

(Real ones move, blink, and drift together towards a spot every few seconds — the still frame above does not do it justice.)

## Install

```bash
pip install git+https://github.com/codewithkrrish/termfireflies.git
```

Python 3.9 or newer, no other dependencies. Then run:

```bash
termfireflies
```

Press `q` or `Ctrl-C` to stop. Your cursor and screen are restored on exit.

## Usage

```bash
termfireflies                      # 40 green fireflies, default drift
termfireflies -n 120 -p amber      # a big amber swarm
termfireflies -p fire -s 2         # fast embers
termfireflies -p rainbow -d 30     # 30 seconds, then stop on its own
termfireflies --seed 42            # the same swarm every time
termfireflies --no-color           # plain characters, no colour codes
```

| Flag | What it does | Default |
| --- | --- | --- |
| `-n, --count` | How many fireflies (1–500) | 40 |
| `-s, --speed` | Drift speed multiplier (0.1–5) | 1 |
| `-p, --palette` | Colour palette (see below) | green |
| `-d, --duration` | Stop after N seconds (0 = run forever) | 0 |
| `--seed` | Seed for a repeatable swarm | — |
| `--no-color` | Plain characters, no ANSI colour | off |

## Palettes

`green` (classic summer evening), `amber` (porch light), `blue` (cold night), `fire` (campfire embers), `violet`, `rainbow` (a mixed swarm).

```bash
termfireflies -p blue
```

## How it works

Each firefly is a tiny state machine: a position, a slow velocity that wanders a little every frame, and a blink cycle — a smooth pulse that spends most of its time dark and flashes bright for a moment, the way real fireflies read. Every few seconds the swarm picks a random meeting point and drifts towards it, then scatters again. That gathering is the one behaviour that makes it look alive instead of like dust.

Rendering is a grid: if two fireflies land on the same cell, the brighter one wins it. Brightness picks the glyph (`.` up to `@`) and scales the colour, so a fading firefly actually looks like it is fading.

## Project structure

```
termfireflies/
  __init__.py     version
  __main__.py     python -m termfireflies
  cli.py          flags, animation loop, terminal setup/teardown
  firefly.py      one firefly: drift, bounce, blink
  swarm.py        the flock and its meeting point
  palette.py      colour palettes
  renderer.py     snapshot -> one frame of terminal text
tests/
  test_firefly.py test_swarm.py test_renderer.py test_cli.py
```

## Limitations — honest ones

- Needs a terminal that understands ANSI escape codes and truecolor for the full effect. On a plain terminal, `--no-color` still works, it just looks flatter.
- It draws at 30 frames per second. Over a slow SSH link it can feel laggy — fewer fireflies (`-n 20`) help a lot.
- The blink pattern is a smooth sine pulse, not a real firefly's species-specific flash code. If you are a firefly researcher, I apologise.
- `q` to quit only works when stdin is a terminal. Anywhere else, use `Ctrl-C`.

## Running the tests

```bash
pip install pytest
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).

## Author

Krrish — [github.com/codewithkrrish](https://github.com/codewithkrrish) · [instagram.com/krrishx.ai](https://www.instagram.com/krrishx.ai)
