# Control Systems — Python CLI-First Control Systems Study & Design Suite

Control Systems is a Python-first engineering toolkit for studying, reproducing, and extending continuous-time control systems workflows. The project is organized as a collection of focused command-line packages aligned with **Ogata, _Modern Control Engineering_ (5th ed.)** and related control systems topics.

Each package is designed to be practical, reproducible, and easy to run from the terminal. Inputs live in dedicated `in/` folders, outputs are written to `out/`, and each tool includes copy-paste runnable examples through its local `RUNS.md` file.

---

## Project goals

This repository is built around a simple idea: control systems calculations should be reproducible, inspectable, and scriptable.

The project aims to provide:

- Clean Python implementations of common control systems workflows
- CLI tools for repeatable analysis and design runs
- JSON/CSV-based input and output conventions
- Plot exports for reports, documentation, and engineering review
- Testable package boundaries for incremental development
- A study-friendly structure that follows the progression of a modern control systems textbook

The intent is not only to compute answers, but to make the modeling, analysis, and design process visible through structured inputs, transparent outputs, and repeatable commands.

---

## Documentation

[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-3D74F7.svg)](https://pablomarcel.github.io/control-modernControl/)
[![Build & Publish Docs](https://github.com/pablomarcel/control-modernControl/actions/workflows/pages.yml/badge.svg)](https://github.com/pablomarcel/control-modernControl/actions/workflows/pages.yml)

Live documentation:

**https://pablomarcel.github.io/control-modernControl/**

Published package documentation:

- [frequencyResponse/bodeTool](https://pablomarcel.github.io/control-modernControl/frequencyResponse/bodeTool/) — Bode plots, gain/phase margins, and frequency-response helpers
- [modelingSystems/canonicalTool](https://pablomarcel.github.io/control-modernControl/modelingSystems/canonicalTool/) — Controllable and observable canonical-form transformations
- [modelingSystems/converterTool](https://pablomarcel.github.io/control-modernControl/modelingSystems/converterTool/) — Transfer-function and state-space conversions
- [modelingSystems/mimoTool](https://pablomarcel.github.io/control-modernControl/modelingSystems/mimoTool/) — MIMO interconnections and system assembly utilities
- [modelingSystems/systemTool](https://pablomarcel.github.io/control-modernControl/modelingSystems/systemTool/) — SISO system construction and workflow scaffolding

---

## Repository structure

The repository is organized by control systems topic and roughly follows the chapter sequence from Ogata’s _Modern Control Engineering_.

Each subfolder is intended to behave as a cohesive package with:

- A CLI entry point
- Example input files
- Reproducible output conventions
- Local `RUNS.md` commands
- Tests where applicable
- Documentation hooks for GitHub Pages

---

## Chapter 1 — Introduction to Control Systems

```text
intro/
  laplaceTool/                # Work in progress
```

**Status:** package scaffolding is in place. Additional tools and examples will be added as the project expands.

---

## Chapter 2 — Mathematical Modeling of Control Systems

```text
modelingSystems/
  canonicalTool/              # Controllable and observable canonical-form transforms
  converterTool/              # Transfer-function / state-space conversion toolkit
  mimoTool/                   # MIMO interconnections, assembly, and coupling utilities
  systemTool/                 # SISO system builder and scaffolding
```

These tools support the construction and transformation of basic control system representations, including transfer functions, state-space models, canonical forms, and multi-input/multi-output interconnections.

**Current focus:** SISO modeling, MIMO assembly, canonical transformations, and representation conversion.

---

## Chapter 3 — Mathematical Modeling of Mechanical and Electrical Systems

```text
modelingMechanical/
  canonicalTool/              # Controllable and observable canonical-form transforms
  converterTool/              # Transfer-function / state-space conversion toolkit
  mimoTool/                   # MIMO interconnections, assembly, and coupling utilities
  systemTool/                 # SISO system builder and scaffolding
```

This area is intended for physical-system modeling workflows, including mechanical and electrical examples that can be reduced to transfer-function or state-space form.

**Status:** package scaffolding is in place. The structure mirrors the modeling tools used in Chapter 2 so physical-system examples can share consistent CLI and I/O conventions.

---

## Chapter 4 — Modeling of Fluid and Thermal Systems

```text
modelingFluid/
  canonicalTool/              # Controllable and observable canonical-form transforms
  converterTool/              # Transfer-function / state-space conversion toolkit
  mimoTool/                   # MIMO interconnections, assembly, and coupling utilities
  systemTool/                 # SISO system builder and scaffolding
```

This section is intended for fluid and thermal systems modeled as dynamic systems, including transfer-function construction, state-space representation, and linearized system analysis.

**Status:** package scaffolding is in place. Future development will extend the examples and utilities for fluid, thermal, and related physical domains.

---

## Chapter 5 — Transient and Steady-State Response Analyses

```text
transientAnalysis/
  hurwitzTool/                # Hurwitz minors and Lienard-Chipart checks
  icTool/                     # Initial-condition handling for x(0) and y(0+)
  responseTool/               # Step, impulse, ramp responses and response metrics
  routhTool/                  # Routh-Hurwitz table, crossings, and stability checks
```

These tools support response analysis and stability checking, including classical transient response specifications and algebraic stability tests.

Expected outputs include:

- Step, impulse, and ramp response data
- Rise time, settling time, overshoot, and steady-state error estimates
- Routh-Hurwitz tables
- Hurwitz determinant checks
- CSV/JSON exports and plots where applicable

---

## Chapter 6 — Root-Locus Analysis and Design

```text
rootLocus/
  rootLocusTool/              # Root-locus generation and analysis
  compensatorTool/            # Lead, lag, and lead-lag compensator design helpers
  systemResponseTool/         # Closed-loop responses for candidate gains
```

The root-locus tools are intended for classical control design workflows, including pole migration, gain selection, compensator placement, and closed-loop response comparison.

Expected outputs include:

- Root-locus plots
- Candidate gain tables
- Pole locations
- Compensator parameters
- Closed-loop response comparisons
- PNG, HTML, CSV, and JSON artifacts where supported

---

## Chapter 7 — Frequency-Response Analysis and Design

```text
frequencyResponse/
  bodeTool/                   # Bode plots, margins, bandwidth, and templates
  plotTool/                   # Nichols and polar plot helpers
  compensatorTool/            # Frequency-domain lead/lag design helpers
  experimentTool/             # Work in progress: empirical FRF helpers
```

These packages support classical frequency-response analysis and design workflows.

Expected outputs include:

- Bode plots
- Gain margin and phase margin
- Bandwidth estimates
- Nichols and polar plot exports
- Frequency-domain compensator design artifacts
- Interactive Plotly HTML and static Matplotlib PNG outputs where supported

---

## Chapter 8 — PID Controllers and Variants

```text
pidControllers/
  pidTool/                    # PID forms and controller parameter workflows
  tuningTool/                 # Ziegler-Nichols, CHR, and IMC-style tuners
  rootLocusTool/              # PID effects on root-locus behavior
  zeroPoleTool/               # Zero/pole editing and visualization helpers
```

This section focuses on PID controller workflows, including common controller forms, tuning rules, response evaluation, and pole-zero interpretation.

Expected outputs include:

- PID gain sets
- Step response comparisons
- Frequency-response templates
- Pole-zero summaries
- CSV/JSON manifests and plots

---

## Chapter 9 — Control Systems Analysis in State Space

```text
stateSpaceAnalysis/
  stateTool/                  # A, B, C, D parsing, invariants, and norms
  stateRepTool/               # State representation utilities
  canonicalTool/              # Controllable and observable canonical transforms
  stateTransTool/             # Similarity transforms and Jordan-form helpers where applicable
  converterTool/              # Transfer-function / state-space conversion utilities
  mimoTool/                   # Work in progress: MIMO state-space helpers
  stateSolnTool/              # State-transition solutions and Phi(t) exports
```

These tools support state-space analysis workflows, including controllability, observability, state transition, canonical representation, and transfer-function conversion.

Expected outputs include:

- State matrices
- Controllability and observability matrices
- Rank checks
- Minimality checks
- State transition matrices
- Time-response samples
- Symbolic derivations where useful

---

## Chapter 10 — Control Systems Design in State Space

```text
stateSpaceDesign/
  controllerTool/             # Full-state feedback design
  gainMatrixTool/             # Pole placement and gain-matrix workflows
  observerGainMatrixTool/     # Luenberger observer gain design
  observerStatePlotTool/      # Measured vs. estimated state plots
  regulatorTool/              # Regulator forms and integral action
  servoTool/                  # Augmented servo designs and command tracking
  lqrTool/                    # Linear quadratic regulator workflows
  minOrdTool/                 # Minimal-order observer workflows
  minOrdTfTool/               # Minimal-order transfer-function synthesis helpers
  robustTool/                 # Work in progress: robustness-oriented templates
  statePlotsTool/             # State-space plotting utilities
```

This section focuses on state-space design workflows, including state feedback, observer design, servo design, regulator structures, LQR, and related plotting utilities.

Expected outputs include:

- Feedback gain matrices
- Observer gain matrices
- Closed-loop state matrices
- Augmented system models
- Regulator and servo summaries
- Time-domain plots
- JSON/CSV artifacts for review and reuse

---

## Design principles

### CLI-first workflow

The project emphasizes command-line execution so that analysis runs can be copied, reviewed, versioned, and repeated.

Typical workflows are built around commands such as:

```bash
python cli.py --help
python cli.py run --infile in/example.json --outfile out/example_out.json --pretty
```

Where possible, tools also support running from the repository root with module-style invocation.

### Reproducible inputs and outputs

The project follows a consistent file convention:

```text
in/      # Input files: JSON, CSV, YAML, or other supported formats
out/     # Output files: JSON, CSV, PNG, HTML, and generated artifacts
RUNS.md  # Copy-paste commands for the package
```

This keeps examples inspectable and makes it easier to compare results across revisions.

### Structured results

Numerical results are intended to be useful both in the terminal and in downstream workflows. Many tools support some combination of:

- Console summaries
- JSON output manifests
- CSV tables
- Matplotlib PNG exports
- Plotly HTML exports
- Logs suitable for debugging and review

### Package-level focus

Each tool is kept relatively focused. This makes the repository easier to extend, test, and document without forcing every workflow into a single monolithic application.

---

## Quick start

```bash
# 1) Clone the repository
git clone https://github.com/pablomarcel/control-modernControl.git
cd control-modernControl

# 2) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows PowerShell/CMD

# 3) Install dependencies
pip install -U pip
pip install -r requirements.txt

# 4) Enter a package and inspect the CLI
cd root_locus_analysis/rootLocusTool
python cli.py --help

# 5) Use the local RUNS.md for copy-paste examples
cat RUNS.md
```

Some packages also support module execution from the repository root, depending on the local import shim and package structure:

```bash
python -m root_locus_analysis.rootLocusTool.cli --help
```

---

## Running tests

Run tests for a specific tool from the repository root:

```bash
pytest root_locus_analysis/rootLocusTool/tests \
  --cov \
  --cov-config=root_locus_analysis/rootLocusTool/.coveragerc \
  --cov-report=term-missing
```

For broader refactors, run the relevant package test suites before committing changes.

---

## I/O conventions

Typical package layout:

```text
someTool/
  cli.py
  apis.py
  core.py
  in/
    example_input.json
  out/
    example_output.json
  tests/
  RUNS.md
```

Common conventions:

- Input files are stored in `in/`
- Generated outputs are stored in `out/`
- CLI examples are documented in `RUNS.md`
- JSON output is treated as the primary machine-readable result
- CSV exports are used for tabular data
- PNG and HTML exports are used for plots and reports

---

## Typical outputs

Depending on the package, the tools may generate:

- Transfer functions
- State-space matrices
- Pole-zero summaries
- Stability tables
- Response metrics
- Gain and compensator tables
- Time-history data
- Frequency-response data
- Static plots as PNG
- Interactive plots as HTML
- JSON manifests for repeatable analysis

---

## Tested setup

The project has been developed primarily with:

- Python 3.13
- NumPy 2.x
- SciPy 1.15.x
- SymPy 1.13.x
- matplotlib 3.10.x
- plotly 5.x
- python-control 0.10.x
- macOS 13.7
- Windows 10/11

See `requirements.txt` for dependency details.

---

## Development notes

When adding or modifying a tool:

- Keep the CLI behavior explicit and documented
- Add or update examples in `in/`
- Keep generated artifacts under `out/`
- Update the local `RUNS.md`
- Add tests for new solver behavior
- Keep JSON outputs stable where possible
- Prefer focused modules over large, tightly coupled scripts

Suggested pull request checklist:

- [ ] CLI command documented in `RUNS.md`
- [ ] `python cli.py --help` reflects new or changed flags
- [ ] New example input added under `in/`
- [ ] Output behavior verified under `out/`
- [ ] Tests added or updated
- [ ] Relevant documentation updated

---

## Roadmap

Planned and ongoing areas of development include:

- Expanded textbook example coverage
- More complete MIMO workflows
- Improved state-space design utilities
- Additional compensator design helpers
- More robust plotting and export options
- Expanded GitHub Pages documentation
- Additional validation tests against known examples

---

## License

Released under the **MIT License**. See `LICENSE` for details.

---

## Acknowledgments

This project is informed by standard control systems education and references, especially:

- K. Ogata, _Modern Control Engineering_ (5th ed.)
- The Python scientific computing ecosystem, including NumPy, SciPy, SymPy, matplotlib, plotly, and python-control

