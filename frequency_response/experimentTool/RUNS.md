# Frequency Response — experimentTool (modernControl)

This README is a quick-run cookbook for the **frequencyResponse/experimentTool** package.
All commands are designed to be copy/paste-friendly and runnable from your repo root
(`modernControl/`).

> Tip: In VS Code or similar, you can click the copy button on each code block and run
> directly in your terminal.


## 0) Environment & prerequisites

```bash
# (optional) create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# install deps used by this tool (adjust versions as needed)
pip install numpy scipy "matplotlib>=3.7" "control>=0.10" "plotly>=6" kaleido click pytest pytest-cov
```

Plotly HTML export works without Kaleido, but PNG export for Plotly requires `kaleido`.


## 1) Quick smoke run (Ogata preset)

```bash
python cli.py run --ogata   --backend mpl   --save-prefix smoke   --npts 64
```

Outputs land in `frequencyResponse/experimentTool/out/`.


## 2) Book model (both backends + exports)

```bash
python cli.py run --ogata   --backend both   --save-prefix ogata_book   --wmin 0.1 --wmax 40 --npts 1200   --export-json --export-csv
```


## 3) Manual model (flags version)

```bash
python cli.py run   --K 10 --type 1 --zeros 2 --poles1 1 --wns 8 --zetas 0.5   --delay 0.2   --backend both --save-prefix ogata_flags   --wmin 0.1 --wmax 40 --npts 1200
```


## 4) Padé delay on run

```bash
python cli.py run   --K 10 --type 1 --zeros 2 --poles1 1 --wns 8 --zetas 0.5   --delay 0.2 --delay-method pade --pade-order 6   --backend mpl --save-prefix ogata_pade   --wmin 0.1 --wmax 40 --npts 1200
```


## 5) Generate synthetic CSV (for pipeline testing)

```bash
python cli.py make-csv --ogata   --wmin 0.1 --wmax 40 --npts 600   --csv-out in/data.csv
```


## 6) Fit from CSV (with optional refinement) + overlay

```bash
python cli.py fit   --csv in/data.csv   --refine   --backend both --save-prefix fit_from_data   --wmin 0.1 --wmax 40 --npts 1200   --export-json
```

The `fit` subcommand takes `--csv` (required). It automatically overlays the data on the model plots.


## 7) Overlay a CSV on a **manual** model

```bash
python cli.py run   --K 10 --type 1 --zeros 2 --poles1 1 --wns 8 --zetas 0.5   --delay 0.2   --backend both --save-prefix overlay_demo   --wmin 0.1 --wmax 40 --npts 1200   --csv in/data.csv
```


## 8) Verbose logging

```bash
python cli.py --verbose run --ogata   --backend mpl --save-prefix verbose_demo --npts 128
```


## 9) Minimal CSV export of model Bode

```bash
python cli.py run --ogata   --backend mpl   --save-prefix bode_export   --npts 256   --export-csv
```


## 10) JSON export (model summary)

```bash
python cli.py run --ogata   --backend mpl   --save-prefix summary_export   --npts 256   --export-json
```

The JSON includes the final `ModelSpec`, rational numerator/denominator (Padé included if selected),
and rational poles/zeros.


## 11) Reproduce your CI smoke tests locally

```bash
pytest frequency_response/experimentTool/tests \
  --override-ini addopts= \
  --cov \
  --cov-config=frequency_response/experimentTool/.coveragerc \
  --cov-report=term-missing
```


## 12) CLI Help

Group-level options:
```bash
python cli.py --help
```

Per-subcommand help:
```bash
python cli.py run --help
python cli.py make-csv --help
python cli.py fit --help
```


## Notes & Conventions

- **Input CSVs** go in `frequencyResponse/experimentTool/in/` (default suggested location).
  Expected headers: `w,mag_db,phase_deg` (or `omega` for `w`, `mag` for `mag_db`, `phase` for `phase_deg`).
- **Outputs** go to `frequencyResponse/experimentTool/out/` with the given `--save-prefix`.
- Transport lag is handled by either:
  - `--delay-method frd` (default): exact phase shift via `exp(-j ω T)` during Bode computation.
  - `--delay-method pade`: rational approximation (order via `--pade-order`, default 6).
- Plotly HTML is saved even without Kaleido; PNG export requires Kaleido.
- Nonlinear refinement (`--refine`) requires SciPy.

Happy identifying! 🔧📈
