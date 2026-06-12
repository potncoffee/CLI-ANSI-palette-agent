---
name: terminal-colors
description: Use when designing terminal color schemes, picking ANSI/xterm 256-color slot numbers, choosing harmonious color combinations for CLI output (dashboards, kanban boards, TUI apps, prompts), or when the user asks to see the terminal palette, color spectrums, hue families, complementary/triadic/tetradic pairings, or "what color code is that". Trigger: /terminal-colors.
---

# Terminal Colors

## Overview

Renders the xterm-256 palette as color-relationship spectrums for designing terminal color schemes. Every color appears as a 3-cell tile with its slot number printed in black on its own background, so codes can be read straight off the swatch and used immediately.

## Usage

```bash
python3 ~/.claude/skills/terminal-colors/terminal_color_spectrums.py [selectors] [--smart] [--width=N]
```

No selectors renders everything (~150KB — far exceeds the conversation display limit; chunk via `awk` on section headers or have June run it with the `!` prefix). **Prefer selectors for in-conversation rendering** — a single relationship's output usually fits in one message.

Selectors (mix freely, space- or comma-separated): section numbers `1`–`9`, or names — `families`/`fam` (1), `analogous`/`ana` (2 + band rows), `rainbow` (3), `complementary`/`comp` (4 + band rows), `triadic`/`tri` (5 + band rows), `tetradic`/`tetra` (6 + band rows), `split`/`split-comp` (7 + band rows), `bands`/`ring` (8 full), `fullbands`/`full` (9 full). A relationship name pulls its family chart **and** its rows in both band sections — the whole concept, not one section. `--list` prints the table. Examples:

```bash
... complementary                 # everything complementary: section 4 + bands in 8 and 9
... triadic,split                 # two relationships, all their views
... 1 9                           # hue families + full-spectrum bands
... rainbow --smart --width=80    # flags compose with selectors
```

Flags: `--smart` = white tile text on dark colors (default all black); `--width=N` overrides terminal-width detection for band chunking.

Sections: (1) 12 hue families dark→light, (2) full 210-color analogous spectrum (exact hue-angle sort — adjacent hues interleave brightness), (3) rainbow spectrum (families in wheel order, dark→light within each — the conventional rainbow-chart reading), (4) complementary, (5) triadic, (6) tetradic, (7) split-complementary, (8) continuous bands — the borderless wheel-equivalent: the 30-hue pure ring stacked over itself rotated by each relationship angle, so every COLUMN is a true relation at every wheel position, (9) full-spectrum continuous bands — section 8 extended to ALL 210 chromatic colors: base row is the rainbow spectrum, partner rows rotate each color's hue while preserving its saturation and value (dark shades pair with dark shades, pastels with pastels). Rotations at 60-deg multiples are exact lattice bijections (180 = max+min−channel, ±120 = channel permutation), so those partner rows each contain all 210 colors; other angles snap to the nearest cube color with a gray-guard. Bands chunk sheet-music style (program-controlled line breaks, all rows reprinted per chunk) so vertical column alignment survives any terminal width; `--width=N` overrides detection.

Coverage: the 12 families partition all 210 chromatic colors, so every relationship section covers the full 210 across its lines; any single line shows only its named families.

## Quick reference — the cube math

| Fact | Value |
|------|-------|
| Slot formula | `slot = 16 + 36r + 6g + b`, channels r,g,b ∈ 0..5 |
| Channel strides | +36 red, +6 green, +1 blue |
| Cube RGB levels | 0, 95, 135, 175, 215, 255 (nonlinear) |
| Rainbow ring | start 196, strides +6,−36,+1,−6,+36,−1 (5 steps each) |
| Grays | cube diagonal 16/59/102/145/188/231 + ramp 232 (dark) → 255 (light) |
| Use a color | fg `\033[38;5;Nm`, bg `\033[48;5;Nm`, reset `\033[0m` |
| Browns | descending cube coords r > g > b (e.g. 130, 94, 137, 180) |
| Readable text on tile | black if luminance `0.30r+0.59g+0.11b ≥ 90`, else white |

Harmony = family-index arithmetic mod 12: complementary +6, triadic +4, tetradic +3, split-complementary +5/+7.

## Repo conventions

This skill folder is its own local git repo — commit changes here locally (no remote yet). `github-committed/` holds the curated staging copy destined for eventual GitHub publication: when the working script reaches a publishable state, copy it there and commit. Do not push anywhere until June says to.

The original dated artifact lives in the vault at `Garden/Claude Code/terminal-color-spectrums 06.12.26.py`; this folder's copy is the canonical working version per `~/.claude/rules/skills.md`.
