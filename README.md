# Modern Control App (Python) — CLI‑First Study & Design Suite

> **Mission:** prove you can learn, reproduce, and *do* continuous‑time control systems **without MATLAB®/Simulink®** — using Python, a clean CLI workflow, and open libraries.

This repository is a collection of focused, test‑driven Python packages ("tools") that replicate and extend the core workflows from **Ogata, *Modern Control Engineering* (5th ed.)** — plus adjacent topics. Every package ships with a friendly **CLI**, example inputs, and a **RUNS.md** full of copy‑paste commands. No notebooks required, no proprietary stack needed.

<p align="center">
  <em>“MATLAB® is not a skill — control engineering is.”</em>
</p>

---

## Why this exists

- I didn’t have a MATLAB® license — and I don't need one.
- Python’s ecosystem (NumPy, SciPy, SymPy, python‑control, etc.) can do everything the textbooks require — but it’s code‑heavy.
- So I wrapped the hard parts into **consistent command‑line tools** with clean I/O, file conventions, and tests.
- The result is a **drop‑in study companion** and **reproducible design lab** for modern control.

> **Trademark note:** MATLAB® and Simulink® are registered trademarks of The MathWorks, Inc. This project is not affiliated with or endorsed by MathWorks.

---

## What’s inside — ordered like Ogata’s book

Each subfolder is a cohesive package with its own CLI, tests, and a RUNS.md. The list below follows the **book chapter order** (PyCharm may display folders alphabetically).

### Chapter 1 — Introduction to Control Systems
```
intro/
  __init__.py                 # (WIP) scaffolding; CLI helpers to come
```
*Status:* package scaffolding in place; short descriptions TBD as tools land.

### Chapter 2 — Mathematical Modeling of Control Systems
### Chapter 3 — Mathematical Modeling of Mechanical & Electrical Systems
### Chapter 4 — Modeling of Fluid & Thermal Systems
```
modelingSystems/
  __init__.py                 # (WIP) system‑level model builders

modelingMechanical/
  __init__.py                 # (WIP) mass‑spring‑damper, gears, shafts

modelingFluid/
  __init__.py                 # (WIP) tanks, pneumatic/hydraulic, thermal
```
*Status:* sub‑packages will grow to mirror Ch.2–4 examples (transfer functions, state space, linearization).

### Chapter 5 — Transient & Steady‑State Response Analyses
```
transientAnalysis/
  hurwitzTool/                # Hurwitz minors, Liénard–Chipart checks
  icTool/                     # Initial‑condition handling (x(0), y(0+))
  responseTool/               # Step/impulse/ramp; specs (t_r, M_p, t_s, e_ss)
  routhTool/                  # Routh–Hurwitz table, crossings & stability
```
- **Goal:** replicate Ogata Ch.5 response calculations and stability tests from raw TF/SS inputs, with CSV/JSON exports and plots.

### Chapter 6 — Root‑Locus Analysis & Design
```
rootLocus/
  rootLocusTool/              # Classic root‑locus engine (asymptotes, breakaway)
  compensatorTool/            # Lead/lag/lead‑lag via angle deficiency; design at s*
  systemResponseTool/         # Closed‑loop responses for candidate gains
```
- **CLI outputs:** locus plots (Matplotlib/Plotly), design tables, selected K, pole sets, and PNG/HTML exports.

### Chapter 7 — Frequency‑Response Analysis & Design
```
frequencyResponse/
  bodeTool/                   # Bode (margins, bandwidth, templates)
  plotTool/                   # Nichols/Polar overlays; grids; export helpers
  compensatorTool/            # Lead/lag design in frequency domain
  experimentTool/             # (WIP) empirical FRF helpers
```
- **CLI outputs:** Bode, Nichols, and Polar plots, PM/GM, target‑PM design, and interactive Plotly HTML.

### Chapter 8 — PID Controllers & Variants
```
pidControllers/
  pidTool/                    # PID forms (ideal/parallel), specs → gains
  tuningTool/                 # Ziegler–Nichols, CHR, IMC‑style tuners
  rootLocusTool/              # PID shapes on root locus (educational)
  zeroPoleTool/               # Add/remove ZPK; visualize impact
```
- **CLI outputs:** controller parameter sets, step responses, frequency templates, CSV/JSON manifests.

### Chapter 9 — Control Systems Analysis in State Space
```
stateSpaceAnalysis/
  stateTool/                  # A,B,C,D parsing; invariants; norms
  stateRepTool/               # Canonical forms; observability/controllability matrices
  canonicalTool/              # Controllable/Observable canonical transforms
  stateTransTool/             # Similarity transforms, Jordan where applicable
  converterTool/              # TF↔SS (minimal realizations)
  mimoTool/                   # (WIP) multi‑input/multi‑output helpers
  stateSolnTool/              # x(t)=e^{At}x0+…; convolution; Φ(t) exports
```
- **CLI outputs:** ranks, Gramians, minimality checks, Φ(t) samples, proofs via SymPy where helpful.

### Chapter 10 — Control Systems Design in State Space
```
stateSpaceDesign/
  controllerTool/             # Full‑state feedback; targets → K
  gainMatrixTool/             # Ackermann/eigs placement; conditioning
  observerGainMatrixTool/     # Luenberger observer gains; duality helpers
  observerStatePlotTool/      # Measured vs estimated; error dynamics
  regulatorTool/              # Servo/regulator forms; integral action
  servoTool/                  # Augmented designs; command tracking
  lqrTool/                    # Quadratic optimal (finite/steady‑state)
  minOrdTool/                 # Minimal‑order observer
  minOrdTfTool/               # Minimal‑order TF synthesis
  robustTool/                 # (WIP) μ-lite: weights, margins, templates
  statePlotsTool/             # Plot helpers: time/frequency overlays
```
- **CLI outputs:** K, L, augmented A_cl, observer forms, performance metrics, CSV/JSON artifacts, and publication‑ready plots.

---

## Design philosophy

- **CLI‑first**: Everything important is a flag, not hidden in a notebook cell.
- **Reproducible**: Inputs live in `in/`, outputs in `out/`, commands in `RUNS.md` next to each tool.
- **Test‑driven**: `pytest` suites per tool; coverage gates during refactors.
- **Pragmatic math**: Uses `python‑control` when it helps; falls back to explicit numerics for robustness and clarity.
- **Teacher‑friendly**: Both Matplotlib **PNG** and Plotly **HTML** exports; clean logs for reports/lectures.

---

## Quick start

```bash
# 1) Clone and create a virtual env (example)
git clone https://github.com/pablomarcel/control-modernControl.git
cd modernControl
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -U pip
pip install -r requirements.txt

# 3) Run a demo from *inside* a package
cd rootLocus/rootLocusTool
python cli.py --help
# Then open that package's RUNS.md for copy‑paste commands.

# 4) Run tests (per tool)
cd ../../
pytest rootLocus/rootLocusTool/tests --cov --cov-config=rootLocus/rootLocusTool/.coveragerc --cov-report=term-missing
```

> Each package contains an **import shim** so `python cli.py ...` works when you `cd` into that folder, and also supports `python -m package.tool.cli` from the repo root.

---

## I/O conventions

- **Inputs**: `in/` (JSON/CSV/YAML, VCD where relevant)
- **Outputs**: `out/` (CSV / JSON manifests / PNG / HTML)
- **Logs**: human‑readable console logs; many CLIs support `--pretty`, `--save_json`, and `--save_csv`

Most tools can:
- print numeric results to console
- export matrices, poles/zeros, responses to **CSV/JSON**
- write **Plotly** interactive HTML and **Matplotlib** PNGs

---

## Tested setup

- Python 3.13 (generally works with 3.11/3.12)
- NumPy 2.x, SciPy 1.15.x, SymPy 1.13.x, matplotlib 3.10.x, plotly 5.x, python‑control 0.10.x
- macOS 13.7 and Windows 10/11

See `requirements.txt` for exact pins.

---

## Contributing

Issues and PRs are welcome:
- Respect the folder structure and the **CLI‑first** approach.
- Keep inputs in `in/`, outputs in `out/`, and runnable **RUNS.md** examples.
- Add or update **tests** with any new feature or refactor.
- Prefer small, focused modules and clean dataclasses for I/O (`apis.py`).

A simple PR checklist:
- [ ] `pytest` passes locally for the changed tool(s)
- [ ] `RUNS.md` updated with new/changed commands
- [ ] New flags documented in `cli.py --help`
- [ ] Outputs reproducible under `out/`

---

## License

Released under the **MIT License** (see `LICENSE`).

---

## Acknowledgments

- K. Ogata, *Modern Control Engineering* (5th ed.).
- The Python open‑source ecosystem: NumPy, SciPy, SymPy, matplotlib, plotly, python‑control, and others.
