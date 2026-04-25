# Control Systems — Python CLI-First Control Systems Study & Design Suite

[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-3D74F7.svg)](https://pablomarcel.github.io/control-systems/)
[![Build & Publish Docs](https://github.com/pablomarcel/control-systems/actions/workflows/pages.yml/badge.svg)](https://github.com/pablomarcel/control-systems/actions/workflows/pages.yml)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Control Systems is a Python-first engineering toolkit for studying, reproducing, and extending continuous-time control systems workflows. The project is organized as a collection of focused command-line packages aligned with **Ogata, _Modern Control Engineering_ (5th ed.)** and related classical and modern control systems topics.

Each package is designed to be practical, reproducible, and easy to run from the terminal. Inputs live in dedicated `in/` folders, outputs are written to `out/`, and each tool includes copy-paste runnable examples through its local `RUNS.md` file.

---

## Live documentation

The full Sphinx documentation is published here:

**https://pablomarcel.github.io/control-systems/**

This is a large, package-by-package documentation site. The links below point directly to the published documentation for each tool.

---

## Documentation index

### Control-system modeling

- [control_systems/canonicalTool](https://pablomarcel.github.io/control-systems/control_systems/canonicalTool/) — Controllable and observable canonical-form transformations
- [control_systems/converterTool](https://pablomarcel.github.io/control-systems/control_systems/converterTool/) — Transfer-function and state-space conversion workflows
- [control_systems/mimoTool](https://pablomarcel.github.io/control-systems/control_systems/mimoTool/) — MIMO interconnections, assembly helpers, and system coupling utilities
- [control_systems/systemTool](https://pablomarcel.github.io/control-systems/control_systems/systemTool/) — SISO system construction, representation helpers, and workflow scaffolding

### Frequency response

- [frequency_response/bodeTool](https://pablomarcel.github.io/control-systems/frequency_response/bodeTool/) — Bode plots, gain margin, phase margin, bandwidth, and frequency-response helpers
- [frequency_response/compensatorTool](https://pablomarcel.github.io/control-systems/frequency_response/compensatorTool/) — Frequency-domain lead, lag, and lead-lag compensator design helpers
- [frequency_response/experimentTool](https://pablomarcel.github.io/control-systems/frequency_response/experimentTool/) — Empirical frequency-response experiment scaffolding and FRF-oriented workflows
- [frequency_response/plotTool](https://pablomarcel.github.io/control-systems/frequency_response/plotTool/) — Nichols, polar, and frequency-response plotting utilities

### PID controllers

- [pid_controllers/pidTool](https://pablomarcel.github.io/control-systems/pid_controllers/pidTool/) — PID controller forms, gain handling, and response-oriented PID workflows
- [pid_controllers/rootLocusTool](https://pablomarcel.github.io/control-systems/pid_controllers/rootLocusTool/) — PID effects on root-locus behavior
- [pid_controllers/tuningTool](https://pablomarcel.github.io/control-systems/pid_controllers/tuningTool/) — PID tuning workflows including rule-based controller settings
- [pid_controllers/zeroPoleTool](https://pablomarcel.github.io/control-systems/pid_controllers/zeroPoleTool/) — Pole-zero editing, interpretation, and visualization helpers

### Root-locus analysis and design

- [root_locus_analysis/compensatorTool](https://pablomarcel.github.io/control-systems/root_locus_analysis/compensatorTool/) — Lead, lag, and lead-lag compensator design helpers
- [root_locus_analysis/rootLocusTool](https://pablomarcel.github.io/control-systems/root_locus_analysis/rootLocusTool/) — Root-locus generation, gain sweeps, and pole migration analysis
- [root_locus_analysis/systemResponseTool](https://pablomarcel.github.io/control-systems/root_locus_analysis/systemResponseTool/) — Closed-loop response comparisons for candidate gains and compensators

### State-space analysis

- [state_space_analysis/canonicalTool](https://pablomarcel.github.io/control-systems/state_space_analysis/canonicalTool/) — State-space canonical-form transformations
- [state_space_analysis/converterTool](https://pablomarcel.github.io/control-systems/state_space_analysis/converterTool/) — Transfer-function/state-space conversion tools
- [state_space_analysis/mimoTool](https://pablomarcel.github.io/control-systems/state_space_analysis/mimoTool/) — MIMO state-space assembly and analysis helpers
- [state_space_analysis/stateRepTool](https://pablomarcel.github.io/control-systems/state_space_analysis/stateRepTool/) — State representation utilities
- [state_space_analysis/stateSolnTool](https://pablomarcel.github.io/control-systems/state_space_analysis/stateSolnTool/) — State-transition solutions and `Phi(t)`-style workflows
- [state_space_analysis/stateTool](https://pablomarcel.github.io/control-systems/state_space_analysis/stateTool/) — Matrix parsing, invariants, ranks, controllability, observability, and norms
- [state_space_analysis/stateTransTool](https://pablomarcel.github.io/control-systems/state_space_analysis/stateTransTool/) — Similarity transforms and state-coordinate transformation helpers

### State-space design

- [state_space_design/controllerTool](https://pablomarcel.github.io/control-systems/state_space_design/controllerTool/) — Full-state feedback controller design
- [state_space_design/gainMatrixTool](https://pablomarcel.github.io/control-systems/state_space_design/gainMatrixTool/) — Pole placement and gain-matrix workflows
- [state_space_design/lqrTool](https://pablomarcel.github.io/control-systems/state_space_design/lqrTool/) — Linear quadratic regulator design workflows
- [state_space_design/minOrdTfTool](https://pablomarcel.github.io/control-systems/state_space_design/minOrdTfTool/) — Minimal-order transfer-function synthesis helpers
- [state_space_design/minOrdTool](https://pablomarcel.github.io/control-systems/state_space_design/minOrdTool/) — Minimal-order observer workflows
- [state_space_design/observerGainMatrixTool](https://pablomarcel.github.io/control-systems/state_space_design/observerGainMatrixTool/) — Luenberger observer gain design
- [state_space_design/observerStatePlotTool](https://pablomarcel.github.io/control-systems/state_space_design/observerStatePlotTool/) — Measured-vs-estimated state plotting
- [state_space_design/regulatorTool](https://pablomarcel.github.io/control-systems/state_space_design/regulatorTool/) — Regulator forms, tracking structures, and integral-action workflows
- [state_space_design/robustTool](https://pablomarcel.github.io/control-systems/state_space_design/robustTool/) — Robust-control-oriented scaffolding and design templates
- [state_space_design/servoTool](https://pablomarcel.github.io/control-systems/state_space_design/servoTool/) — Augmented servo design and command-tracking workflows
- [state_space_design/statePlotsTool](https://pablomarcel.github.io/control-systems/state_space_design/statePlotsTool/) — State-space plotting utilities

### Transient analysis

- [transient_analysis/hurwitzTool](https://pablomarcel.github.io/control-systems/transient_analysis/hurwitzTool/) — Hurwitz determinants, leading minors, and stability checks
- [transient_analysis/icTool](https://pablomarcel.github.io/control-systems/transient_analysis/icTool/) — Initial-condition handling for state and output response workflows
- [transient_analysis/responseTool](https://pablomarcel.github.io/control-systems/transient_analysis/responseTool/) — Step, impulse, ramp, and transient-response metrics
- [transient_analysis/routhTool](https://pablomarcel.github.io/control-systems/transient_analysis/routhTool/) — Routh-Hurwitz arrays, sign-change checks, symbolic stability regions, and verification helpers

---

## Project goals

This repository is built around a simple idea: control systems calculations should be reproducible, inspectable, and scriptable.

The project aims to provide:

- Clean Python implementations of common control systems workflows
- CLI tools for repeatable analysis and design runs
- JSON/CSV-based input and output conventions
- Plot exports for reports, documentation, and engineering review
- Testable package boundaries for incremental development
- A study-friendly structure that follows the progression of modern control systems topics
- Package-level Sphinx documentation published through GitHub Pages

The intent is not only to compute answers, but to make the modeling, analysis, and design process visible through structured inputs, transparent outputs, and repeatable commands.

---

## Repository structure

The repository is organized by control systems topic. The package folder names match the published GitHub Pages documentation paths.

```text
control_systems/
  canonicalTool/
  converterTool/
  mimoTool/
  systemTool/

frequency_response/
  bodeTool/
  compensatorTool/
  experimentTool/
  plotTool/

pid_controllers/
  pidTool/
  rootLocusTool/
  tuningTool/
  zeroPoleTool/

root_locus_analysis/
  compensatorTool/
  rootLocusTool/
  systemResponseTool/

state_space_analysis/
  canonicalTool/
  converterTool/
  mimoTool/
  stateRepTool/
  stateSolnTool/
  stateTool/
  stateTransTool/

state_space_design/
  controllerTool/
  gainMatrixTool/
  lqrTool/
  minOrdTfTool/
  minOrdTool/
  observerGainMatrixTool/
  observerStatePlotTool/
  regulatorTool/
  robustTool/
  servoTool/
  statePlotsTool/

transient_analysis/
  hurwitzTool/
  icTool/
  responseTool/
  routhTool/
```

Each subfolder is intended to behave as a cohesive package with:

- A CLI entry point
- Example input files
- Reproducible output conventions
- Local `RUNS.md` commands
- Tests where applicable
- Sphinx documentation hooks for GitHub Pages

---

## What the project can do

Depending on the package, the tools can support workflows such as:

- Building transfer-function and state-space representations
- Converting between transfer functions and state-space forms
- Constructing canonical forms
- Assembling MIMO systems
- Computing transient responses
- Extracting step-response metrics
- Building Routh arrays and Hurwitz determinant checks
- Generating root-locus plots
- Comparing closed-loop candidate gains
- Designing lead, lag, and lead-lag compensators
- Generating Bode, Nichols, and polar plots
- Estimating gain margin, phase margin, and bandwidth
- Tuning PID controllers
- Designing state-feedback controllers
- Computing observer gains
- Building regulator and servo configurations
- Solving LQR design cases
- Exporting plots, tables, JSON manifests, and CSV data

---

## CLI-first workflow

The project emphasizes command-line execution so that analysis runs can be copied, reviewed, versioned, and repeated.

Typical workflows are built around commands such as:

```bash
python cli.py --help
python cli.py run --infile in/example.json --outfile out/example_out.json --pretty
```

Where possible, tools also support running from the repository root with module-style invocation:

```bash
python -m root_locus_analysis.rootLocusTool.cli --help
python -m transient_analysis.routhTool.cli run --coeffs "1,5,6,K" --symbol K --solve-for K
```

---

## Reproducible inputs and outputs

Most packages follow a consistent file convention:

```text
in/       # Input files: JSON, CSV, YAML, TXT, or other supported formats
out/      # Output files: JSON, CSV, PNG, HTML, and generated artifacts
RUNS.md   # Copy-paste commands for the package
```

This keeps examples inspectable and makes it easier to compare results across revisions.

---

## Structured results

Numerical results are intended to be useful both in the terminal and in downstream workflows. Many tools support some combination of:

- Console summaries
- JSON output manifests
- CSV tables
- Matplotlib PNG exports
- Plotly HTML exports
- Logs suitable for debugging and review

JSON output is generally treated as the primary machine-readable result. CSV exports are used for tabular data, while PNG and HTML exports are used for plots and engineering review artifacts.

---

## Quick start

```bash
# 1) Clone the repository
git clone https://github.com/pablomarcel/control-systems.git
cd control-systems

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

---

## Example commands

### Routh-Hurwitz stability check

```bash
cd transient_analysis/routhTool

python cli.py run \
  --coeffs "1,5,6,K" \
  --symbol K \
  --solve-for K \
  --hurwitz \
  --export cubic_gain
```

### Root-locus package help

```bash
cd root_locus_analysis/rootLocusTool
python cli.py --help
```

### Frequency-response package help

```bash
cd frequency_response/bodeTool
python cli.py --help
```

### State-space design package help

```bash
cd state_space_design/gainMatrixTool
python cli.py --help
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

## Documentation workflow

The documentation is generated with Sphinx and published to GitHub Pages.

The live site is:

```text
https://pablomarcel.github.io/control-systems/
```

The GitHub Actions workflow for documentation publishing lives here:

```text
https://github.com/pablomarcel/control-systems/actions/workflows/pages.yml
```

When package APIs, CLI behavior, examples, or docstrings change, update the package documentation and verify the docs build before pushing.

---

## I/O conventions

Typical package layout:

```text
someTool/
  cli.py
  apis.py
  core.py
  io.py
  utils.py
  in/
    example_input.json
  out/
    example_output.json
  tests/
  RUNS.md
  docs/
```

Common conventions:

- Input files are stored in `in/`
- Generated outputs are stored in `out/`
- CLI examples are documented in `RUNS.md`
- JSON output is treated as the primary machine-readable result
- CSV exports are used for tabular data
- PNG and HTML exports are used for plots and reports
- Sphinx documentation is kept package-focused and published through the main GitHub Pages site

---

## Typical outputs

Depending on the package, the tools may generate:

- Transfer functions
- State-space matrices
- Pole-zero summaries
- Stability tables
- Routh arrays
- Hurwitz determinant tables
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
- Keep documentation links aligned with the published GitHub Pages paths
- Prefer focused modules over large, tightly coupled scripts

Suggested pull request checklist:

- [ ] CLI command documented in `RUNS.md`
- [ ] `python cli.py --help` reflects new or changed flags
- [ ] New example input added under `in/`
- [ ] Output behavior verified under `out/`
- [ ] Tests added or updated
- [ ] Relevant documentation updated
- [ ] Sphinx build verified
- [ ] README documentation links still point to `https://pablomarcel.github.io/control-systems/`

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
- More consistent package-level examples, command manifests, and Sphinx pages

---

## License

Released under the **MIT License**. See `LICENSE` for details.

---

## Acknowledgments

This project is informed by standard control systems education and references, especially:

- K. Ogata, _Modern Control Engineering_ (5th ed.)
- The Python scientific computing ecosystem, including NumPy, SciPy, SymPy, matplotlib, plotly, and python-control
