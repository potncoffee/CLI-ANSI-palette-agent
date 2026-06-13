#!/usr/bin/env python3
"""Terminal Color Spectrums — full 256-color relationship reference.

Renders every chromatic color of the xterm-256 palette (the 210 non-gray
members of the 6x6x6 cube) organized by color-relationship spectrum:

  1. The 12 hue families (monochromatic spectrums), darkest -> lightest
  2. Full analogous spectrum (all 210, sorted by exact hue angle)
  3. Rainbow spectrum (all 210: families in wheel order, dark -> light
     within each family — brightness groups stay together, the way a
     rainbow chart usually reads)
  4. Complementary pairings   (6 lines: family + opposite family)
  5. Triadic sets             (4 lines: three families 120 deg apart)
  6. Tetradic squares         (3 lines: four families 90 deg apart)
  7. Split-complementary sets (12 lines: base + complement's flanks)
  8. Continuous bands — the borderless view. The 30-color pure-hue ring
     stacked over itself rotated by each relationship angle, so every
     COLUMN is a true relation at every wheel position (no family bins).
     Chunked sheet-music style: the program breaks lines to fit the
     window and reprints all rows per chunk, so vertical adjacency
     survives any terminal width. Pass --width=N to override detection.
  9. Full-spectrum continuous bands — section 8 extended to ALL 210
     chromatic colors. Base row = the rainbow spectrum (section 3
     order); partner rows rotate each color's hue by the relationship
     angle while PRESERVING its saturation and value, so dark shades
     pair with dark shades and pastels with pastels. Rotations by
     multiples of 60 deg are exact on the cube lattice (180 deg is
     max+min-channel; +/-120 deg are channel permutations); other
     angles snap to the nearest cube color. Guarantees every chromatic
     color appears in every relationship band.

Coverage note: the 12 families PARTITION the 210 chromatic colors — every
color belongs to exactly one family, so every relationship section covers
all 210 across its lines. A single line only ever shows its named families;
boundary colors (a pink at ~345 deg, an aqua at ~165 deg) live in their
assigned family only, which can read as "missing" from a neighboring line.

Each color renders as a 3-cell tile: its slot number in black text on its
own background color, so tiles touch seamlessly. Use any slot number with:

  foreground:  \\033[38;5;{N}m      background:  \\033[48;5;{N}m

Slot math (the cube):  slot = 16 + 36r + 6g + b   for r,g,b in 0..5
Channel strides:       +36 = red, +6 = green, +1 = blue
Pure-hue rainbow ring: start 196, walk strides +6,-36,+1,-6,+36,-1 (5 steps each)
Grays (excluded here): cube diagonal 16/59/102/145/188/231 + ramp 232-255

Usage:
  python3 terminal_color_spectrums.py [selectors] [--smart] [--width=N] [--page=N]

No selectors renders everything. Selectors are section numbers (1-9) and/or
names, combinable in any mix ("complementary triadic", "1 9", "rainbow comp"):

  families | fam            section 1
  analogous | ana           section 2 + analogous rows of bands 8 and 9
  rainbow                   section 3
  complementary | comp      section 4 + complementary rows of bands 8 and 9
  triadic | tri             section 5 + triadic rows of bands 8 and 9
  tetradic | tetra          section 6 + tetradic rows of bands 8 and 9
  split | split-comp        section 7 + split-comp rows of bands 8 and 9
  bands | ring              section 8 in full
  fullbands | full          section 9 in full
  --list                    print this selector table and exit

Flags:
  --smart      white tile text on dark colors (default: all black)
  --width=N    chunk bands to N columns (default: terminal width)
  --page=N     print only chunk N of the output (opt-in; see below)
  --budget=N   byte budget per --page chunk (default 20000)

Viewing the output:
  A bare run ALWAYS prints the whole reference. In a real terminal it scrolls
  and renders in color; in Claude Code you see all of it by expanding the tool
  output (Ctrl-O). The "Output too large" notice only limits what loads into an
  AGENT's context window -- it does not stop a human from seeing the full
  output. --page=N is therefore strictly opt-in: it exists only so an agent can
  pull one measured chunk into its own context when it needs to read specific
  values. It is never required to view the colors. For a focused look, a
  selector (e.g. `complementary`, `triadic`, `bands`) is the better tool.
"""

import colorsys
import contextlib
import io
import shutil
import sys

SMART_TEXT = "--smart" in sys.argv

WIDTH = next((int(a.split("=", 1)[1]) for a in sys.argv
              if a.startswith("--width=")), None)
if WIDTH is None:
    WIDTH = shutil.get_terminal_size((100, 24)).columns

# --- optional output paging ------------------------------------------------
# A bare run ALWAYS prints the whole reference: a real terminal scrolls it, and
# Claude Code shows the full thing when you expand the tool output (Ctrl-O). The
# "Output too large" notice only limits what loads into an AGENT's context
# window, not what a human can see. Paging is therefore strictly OPT-IN, for the
# rare case where an agent wants to pull one measured chunk into its own context.
BUDGET = next((int(a.split("=", 1)[1]) for a in sys.argv
               if a.startswith("--budget=")), 20000)
PAGE = next((int(a.split("=", 1)[1]) for a in sys.argv
             if a.startswith("--page=")), 1)
WANT_PAGE = any(a.startswith("--page=") for a in sys.argv)

# xterm's actual RGB values for cube levels 0..5
LEVELS = [0, 95, 135, 175, 215, 255]

FAMILY_NAMES = ["red", "orange", "yellow", "chartreuse", "green", "spring",
                "cyan", "azure", "blue", "violet", "magenta", "rose"]


def coords(n):
    i = n - 16
    return i // 36, (i % 36) // 6, i % 6


def rgb(n):
    r, g, b = coords(n)
    return LEVELS[r], LEVELS[g], LEVELS[b]


def luminance(n):
    r, g, b = rgb(n)
    return 0.30 * r + 0.59 * g + 0.11 * b


def hue(n):
    r, g, b = rgb(n)
    h, _, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return h * 360


def tile(n):
    fg = 15 if SMART_TEXT and luminance(n) < 90 else 0
    return f"\033[48;5;{n}m\033[38;5;{fg}m{n:>3}\033[0m"


def line(slots, indent="   "):
    print(indent + "".join(tile(n) for n in slots))


def header(text):
    print(f"\n  {text}\n")


# ---- bin the 210 chromatic colors into 12 hue families (30 deg bins) ----
families = [[] for _ in range(12)]
for n in range(16, 232):
    r, g, b = coords(n)
    if r == g == b:
        continue                       # gray diagonal: no hue
    families[round(hue(n) / 30) % 12].append(n)
for fam in families:
    fam.sort(key=luminance)            # darkest shade -> lightest tint


def sec1_families():
    header("1. THE 12 HUE FAMILIES (monochromatic) — dark -> light, 30-deg bins")
    for i, name in enumerate(FAMILY_NAMES):
        print(f"   {name:>10} ({i * 30:>3} deg)")
        line(families[i], indent="   ")


def sec2_analogous():
    header("2. FULL ANALOGOUS SPECTRUM — all 210 chromatic colors by hue angle")
    everything = sorted(
        (n for fam in families for n in fam),
        key=lambda n: (hue(n), luminance(n)),
    )
    line(everything)


def sec3_rainbow():
    header("3. RAINBOW SPECTRUM — families in wheel order, dark -> light within each")
    line([n for fam in families for n in fam])


def sec4_complementary():
    header("4. COMPLEMENTARY — each family followed by its 180-deg opposite")
    for i in range(6):
        print(f"   {FAMILY_NAMES[i]} / {FAMILY_NAMES[i + 6]}")
        line(families[i] + families[i + 6], indent="   ")


def sec5_triadic():
    header("5. TRIADIC — three families 120 deg apart (offsets 0/4/8)")
    for i in range(4):
        names = " / ".join(FAMILY_NAMES[(i + 4 * k) % 12] for k in range(3))
        print(f"   {names}")
        line([n for k in range(3) for n in families[(i + 4 * k) % 12]], indent="   ")


def sec6_tetradic():
    header("6. TETRADIC — four families in a square (offsets 0/3/6/9)")
    for i in range(3):
        names = " / ".join(FAMILY_NAMES[(i + 3 * k) % 12] for k in range(4))
        print(f"   {names}")
        line([n for k in range(4) for n in families[(i + 3 * k) % 12]], indent="   ")


def sec7_split():
    header("7. SPLIT-COMPLEMENTARY — base family + complement's flanks (0/+150/+210 deg)")
    for i in range(12):
        names = " / ".join(FAMILY_NAMES[(i + o) % 12] for o in (0, 5, 7))
        print(f"   {names}")
        line([n for o in (0, 5, 7) for n in families[(i + o) % 12]], indent="   ")


# ---- 8. continuous bands: ring stacked over rotated ring, no family bins ----
# The 30-color pure-hue ring, walked by cube strides from 196 (12 deg/step).
RING = [196]
for stride, steps in [(6, 5), (-36, 5), (1, 5), (-6, 5), (36, 5), (-1, 4)]:
    for _ in range(steps):
        RING.append(RING[-1] + stride)

LABEL_W = 7                                  # left gutter for row labels


def band(title, rows):
    """rows: list of (label, ring offset). Sheet-music chunking: break the
    ring to fit WIDTH and reprint every row per chunk, so each printed
    column stays a true relation regardless of terminal width."""
    per = max(1, (WIDTH - LABEL_W - 3) // 3)   # tiles per chunk
    print(f"   {title}")
    for start in range(0, len(RING), per):
        idxs = range(start, min(start + per, len(RING)))
        for label, off in rows:
            tiles = "".join(tile(RING[(i + off) % len(RING)]) for i in idxs)
            print(f"   {label:>{LABEL_W}} {tiles}")
        print()


RING_BANDS = [
    ("analogous", "analogous (each column: a hue with its 24-deg neighbors)",
     [("-24deg", -2), ("base", 0), ("+24deg", 2)]),
    ("complementary", "complementary (each column: a hue over its opposite)",
     [("base", 0), ("+180", 15)]),
    ("triadic", "triadic (each column: an equilateral triangle)",
     [("base", 0), ("+120", 10), ("+240", 20)]),
    ("tetradic", "tetradic rectangle (each column: two complementary pairs)",
     [("base", 0), ("+60", 5), ("+180", 15), ("+240", 20)]),
    ("split-complementary",
     "split-complementary (each column: a hue + its opposite's flanks)",
     [("base", 0), ("+156", 13), ("+204", 17)]),
]


def sec8_bands(only=None):
    chosen = [b for b in RING_BANDS if only is None or b[0] in only]
    if not chosen:
        return
    header("8. CONTINUOUS BANDS — column = related hues at every wheel position "
           "(no family borders)")
    for _, title, rows in chosen:
        band(title, rows)


# ---- 9. full-spectrum bands: all 210 colors, partners preserve sat/value ----
def rotate(n, deg):
    """Rotate a cube color's hue by deg, preserving saturation and value.

    Multiples of 60 deg use exact lattice operations in level space
    (+/-120 = channel permutation, 180 = max+min-channel, 60/300 their
    compositions). These are BIJECTIONS on the 210 chromatic colors, so
    every such partner row contains all 210 colors exactly once. Other
    angles rotate true-RGB hue and snap to the nearest cube color."""
    deg %= 360
    r, g, b = coords(n)
    if deg % 60 == 0:
        for _ in range(deg // 120):            # 120-deg steps: permutation
            r, g, b = b, r, g
        if deg % 120 == 60:                    # odd 60: one more 240 + reflect
            r, g, b = g, b, r                  # (240 then 180 below = +60)
            mx, mn = max(r, g, b), min(r, g, b)
            r, g, b = mx + mn - r, mx + mn - g, mx + mn - b
        elif deg == 180:
            mx, mn = max(r, g, b), min(r, g, b)
            r, g, b = mx + mn - r, mx + mn - g, mx + mn - b
        return 16 + 36 * r + 6 * g + b
    rr, gg, bb = rgb(n)
    h, s, v = colorsys.rgb_to_hsv(rr / 255, gg / 255, bb / 255)
    rot = colorsys.hsv_to_rgb((h + deg / 360) % 1.0, s, v)
    lv = [min(range(6), key=lambda i, c=c: abs(LEVELS[i] - c * 255)) for c in rot]
    if lv[0] == lv[1] == lv[2]:                # never collapse a relation to gray
        lv[rot.index(max(rot))] = min(5, lv[rot.index(max(rot))] + 1)
    return 16 + 36 * lv[0] + 6 * lv[1] + lv[2]


SPECTRUM = [n for fam in families for n in fam]    # rainbow order, all 210


def full_band(title, rows):
    per = max(1, (WIDTH - LABEL_W - 3) // 3)
    print(f"   {title}")
    for start in range(0, len(SPECTRUM), per):
        chunk = SPECTRUM[start:start + per]
        for label, deg in rows:
            tiles = "".join(tile(n if deg == 0 else rotate(n, deg)) for n in chunk)
            print(f"   {label:>{LABEL_W}} {tiles}")
        print()


FULL_BANDS = [
    ("analogous", "analogous", [("-24deg", -24), ("base", 0), ("+24deg", 24)]),
    ("complementary", "complementary", [("base", 0), ("+180", 180)]),
    ("triadic", "triadic", [("base", 0), ("+120", 120), ("+240", 240)]),
    ("tetradic", "tetradic rectangle",
     [("base", 0), ("+60", 60), ("+180", 180), ("+240", 240)]),
    ("split-complementary", "split-complementary",
     [("base", 0), ("+156", 156), ("+204", 204)]),
]


def sec9_fullbands(only=None):
    chosen = [b for b in FULL_BANDS if only is None or b[0] in only]
    if not chosen:
        return
    header("9. FULL-SPECTRUM CONTINUOUS BANDS — all 210 colors over their rotated "
           "partners (saturation + value preserved)")
    for _, title, rows in chosen:
        full_band(title, rows)


# ---- selector parsing ----
# A relationship name selects its family-chart section AND its rows in both
# band sections; a number selects one whole section.
RELATIONSHIPS = {
    "analogous": (2, "analogous"), "ana": (2, "analogous"),
    "complementary": (4, "complementary"), "comp": (4, "complementary"),
    "triadic": (5, "triadic"), "tri": (5, "triadic"),
    "tetradic": (6, "tetradic"), "tetra": (6, "tetradic"),
    "split": (7, "split-complementary"), "split-comp": (7, "split-complementary"),
    "split-complementary": (7, "split-complementary"),
}
SECTION_NAMES = {"families": 1, "fam": 1, "rainbow": 3,
                 "bands": 8, "ring": 8, "fullbands": 9, "full": 9}


def parse_selectors(args):
    tokens = [t for a in args if not a.startswith("--") for t in a.split(",") if t]
    if not tokens:
        return set(range(1, 10)), None, None     # everything, all bands
    sections, band_sel = set(), set()
    for t in (t.lower() for t in tokens):
        if t.isdigit() and 1 <= int(t) <= 9:
            sections.add(int(t))
        elif t in RELATIONSHIPS:
            sec, key = RELATIONSHIPS[t]
            sections.add(sec)
            band_sel.add(key)
        elif t in SECTION_NAMES:
            sections.add(SECTION_NAMES[t])
        else:
            sys.exit(f"unknown selector: {t!r} — run with --list for options")
    only8 = None if 8 in sections else (band_sel or set())
    only9 = None if 9 in sections else (band_sel or set())
    if band_sel:
        sections.update((8, 9))
    return sections, only8, only9


if "--list" in sys.argv:
    print(__doc__[__doc__.index("No selectors"):])
    sys.exit(0)

selected, only8, only9 = parse_selectors(sys.argv[1:])

# Render into a buffer first so we can measure it and page if an agent host
# would otherwise truncate the output. Capturing (vs. printing live) leaves the
# bytes identical, so a real terminal sees exactly what it always did.
_buf = io.StringIO()
with contextlib.redirect_stdout(_buf):
    if 1 in selected: sec1_families()
    if 2 in selected: sec2_analogous()
    if 3 in selected: sec3_rainbow()
    if 4 in selected: sec4_complementary()
    if 5 in selected: sec5_triadic()
    if 6 in selected: sec6_tetradic()
    if 7 in selected: sec7_split()
    if 8 in selected: sec8_bands(only8)
    if 9 in selected: sec9_fullbands(only9)
    print()

_output = _buf.getvalue()


def _paginate(text, budget):
    """Split into pages each <= budget bytes, breaking only between whole
    lines so a colored row is never cut mid-escape-sequence."""
    pages, cur, size = [], [], 0
    for ln in text.splitlines(keepends=True):
        lb = len(ln.encode())
        if cur and size + lb > budget:
            pages.append("".join(cur))
            cur, size = [], 0
        cur.append(ln)
        size += lb
    if cur:
        pages.append("".join(cur))
    return pages or [""]


if not WANT_PAGE:
    sys.stdout.write(_output)            # default, every time: the whole thing
else:
    pages = _paginate(_output, BUDGET)
    k = len(pages)
    p = min(max(PAGE, 1), k)
    sys.stdout.write(pages[p - 1])
    nxt = p + 1 if p < k else 1
    sys.stdout.write(
        f"\n  [chunk {p}/{k} of a {len(_output.encode()) // 1024} KB render — "
        f"--page={nxt} for the next chunk, or drop --page to print it all at "
        f"once.]\n")
