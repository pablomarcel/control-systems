# =============================
# File: transientAnalysis/hurwitzTool/README.md
# =============================
# hurwitzTool (modernControl/transientAnalysis)

**Purpose.** Object‑oriented Hurwitz stability analyzer: numeric checks, symbolic regions, 1‑D/2‑D scans, ASCII/PNG heatmaps, and pretty 1‑D interval rendering.

## Layout
```
transientAnalysis/
  hurwitzTool/
    app.py        # App context, helpers, pretty intervals
    apis.py       # Requests/Results dataclasses + service façade
    cli.py        # End‑user CLI (argparse)
    core.py       # Polynomial, Hurwitz matrix/minors, conditions, numeric checker
    design.py     # Small presets/examples
    io.py         # IO manager for in/ out/ + CSV/PNG helpers
    utils.py      # Parsing, interval pretty printing, ASCII heatmap
    tools/
      tool_plantuml.py  # Minimal PlantUML class diagram generator
    tests/
      test_*.py   # Pytest suite (TDD‑friendly)
    in/           # input assets (if any)
    out/          # outputs (CSVs, PNGs)
```