# Terminal Color Spectrums

**Color theory for places that have no color picker.** A single, dependency-free
Python script that renders the xterm-256 palette as *color-relationship spectrums* —
complementary, triadic, tetradic, split-complementary, analogous, and full hue
families — so you can design harmonious color schemes for terminals, TUIs, prompts,
log output, and other text/ASCII surfaces by reading slot numbers straight off the
swatch.

It is the color wheel's *relationships* without the wheel: a wheel is a GUI object
you have to look at, and a terminal can't draw one. So instead every relationship is
laid out as flat, labeled, parseable rows of solid color blocks, each block printing
its own ANSI slot number in-place. You read a column or a row, you get the numbers,
you use them.

```
\033[48;5;196m  ← background = color 196 (pure red)
\033[38;5;51m   ← foreground = color 51  (its complement, cyan)
```

## Why it's built AI-forward

Picking colors has always been a *visual* task — color wheels, hex pickers, eyedroppers.
None of that exists for an LLM agent working in a CLI framework: it can't see a wheel,
and it can't sample a pixel. This tool is designed so an agent can do real color design
from text alone:

- **The output is the API.** Every color is emitted as its integer slot number inside
  its own swatch, in labeled rows and aligned columns. An agent reads the rendered text
  and selects a palette by number — no image, no pixels, no vision model required.
- **Selectors keep it context-window-friendly.** Ask for exactly the relationship you
  need (`complementary`, `triadic`, …) and you get a compact block instead of the whole
  ~150 KB reference, so it fits in a model's context.
- **The math is documented so an agent can skip the tool entirely.** The cube formula
  and the rotation rules (below) let a model *compute* a color's complement or triad
  directly, deterministically, without running anything.
- **It ships as an agent skill.** [`SKILL.md`](./SKILL.md) is a drop-in
  [Claude Code](https://docs.anthropic.com/claude-code) / agent-framework skill manifest:
  describe-when-to-use metadata plus a quick-reference table, so an agent loads the
  capability on demand.

Humans designing a kanban board, a shell prompt, a syntax theme, or ASCII art get the
same benefit from the other direction: legible, copy-pasteable, relationship-organized
swatches with the codes right there.

## Install / run

No dependencies beyond Python 3 (uses only the standard library).

```bash
python3 terminal_color_spectrums.py [selectors] [--smart] [--width=N] [--page=N | --all]
```

With no selectors it renders everything (≈150 KB — pipe it through a pager). For an
in-terminal or in-context look at one idea, pass a selector.

## Selectors

Mix freely, space- or comma-separated. A **relationship name** pulls the whole concept:
its family chart *and* its rows in both continuous-band sections. A **number** selects
one section outright.

| Selector | Renders |
|---|---|
| `families` · `fam` | §1 — the 12 hue families, dark → light |
| `analogous` · `ana` | §2 + the analogous rows of the band sections |
| `rainbow` | §3 — families in wheel order, brightness grouped |
| `complementary` · `comp` | §4 + the complementary band rows |
| `triadic` · `tri` | §5 + the triadic band rows |
| `tetradic` · `tetra` | §6 + the tetradic band rows |
| `split` · `split-comp` | §7 + the split-complementary band rows |
| `bands` · `ring` | §8 — pure-hue continuous bands, in full |
| `fullbands` · `full` | §9 — full-spectrum continuous bands, in full |
| `1`–`9` | any section by number |
| `--list` | print the selector table and exit |

```bash
python3 terminal_color_spectrums.py complementary       # everything complementary
python3 terminal_color_spectrums.py triadic,split       # two relationships, all their views
python3 terminal_color_spectrums.py 1 9                  # hue families + full-spectrum bands
python3 terminal_color_spectrums.py rainbow --smart      # flags compose with selectors
```

## Flags

| Flag | Effect |
|---|---|
| `--smart` | Print tile numbers in **white** on dark colors (luminance-tested), instead of the default all-black text. Improves legibility of labels on deep navies/maroons. |
| `--width=N` | Force the band sections to wrap at `N` columns instead of auto-detecting the terminal width. The bands chunk *sheet-music style* — the program controls the line breaks and reprints every row per chunk — so vertically-aligned relationship columns survive any width. |
| `--page=N` | Print page `N` of the paginated output (agent display mode; see below). |
| `--all` | Force the entire render in one shot, even under an agent. |
| `--budget=N` | Per-page byte budget for agent display mode (default `20000`). |

## Agent display (Claude Code and friends)

Coding agents cap how much command output they show inline and shunt the overflow
to a file, and this reference is ~150 KB of ANSI codes, far over that cap, so an
agent would otherwise see only a truncated preview. When `CLAUDECODE` or `AI_AGENT`
is set in the environment, the script auto-paginates: it prints one page (sized by
`--budget`, default 20000 bytes), then tells the agent how to fetch the rest with
`--page=2`, `--page=3`, and so on, or `--all` to force the whole dump. A render that
already fits the budget prints whole, with no paging. In a real terminal (no agent
env var) nothing changes: the full output just scrolls and renders in color. A
single selector such as `complementary` usually fits one page.

## The sections

1. **Hue families** — all 210 chromatic colors binned into 12 families (30° each), each sorted darkest shade → lightest tint.
2. **Analogous spectrum** — all 210 sorted by exact hue angle.
3. **Rainbow spectrum** — families in wheel order, brightness grouped within each (the conventional rainbow reading).
4. **Complementary** · 5. **Triadic** · 6. **Tetradic** · 7. **Split-complementary** — family-paired relationship charts.
8. **Continuous bands** — the 30-hue pure ring stacked over itself, rotated by each relationship angle, so every *column* is a true relation at every wheel position (no family borders).
9. **Full-spectrum continuous bands** — §8 extended to all 210 colors: partner rows rotate each color's hue while preserving its saturation and value, so dark shades pair with dark shades and pastels with pastels.

## The cube math

The xterm-256 chromatic colors form a 6×6×6 RGB cube. Everything here is arithmetic on it.

| Fact | Value |
|---|---|
| Slot formula | `slot = 16 + 36·r + 6·g + b`, channels `r,g,b ∈ 0..5` |
| Channel strides | `+36` red, `+6` green, `+1` blue |
| Cube RGB levels | `0, 95, 135, 175, 215, 255` (nonlinear) |
| Pure-hue ring | start `196`, walk strides `+6, −36, +1, −6, +36, −1` (5 steps each) |
| Grays (excluded) | cube diagonal `16/59/102/145/188/231` + ramp `232`(dark)→`255`(light) |
| Readable label | black if luminance `0.30r+0.59g+0.11b ≥ 90`, else white |

Hue rotations are exact lattice operations at multiples of 60°: **180°** is
`max+min−channel` (the complement), **±120°** are channel permutations (the triad).
These are bijections on the 210 chromatic colors, which is why every full-spectrum
complementary/triadic/tetradic row contains all 210 colors exactly once. Other angles
rotate true-RGB hue and snap to the nearest cube color.

## License

MIT.
