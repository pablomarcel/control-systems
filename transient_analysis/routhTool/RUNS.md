
# routhTool — RUNS.md

This file shows how to run the **routhTool** commands **from inside** the
`transientAnalysis/routhTool` package, and also how to run them **from the repo root**.

---

## ✅ Run from inside the package (recommended during development)

Change into the package directory first:

```bash
cd transient_analysis/routhTool
```

Now run `cli.py` directly (the file includes an import shim so absolute imports work):

### 1) Purely numeric cubic: p(s) = s^3 + 5 s^2 + 6 s + 2
```bash
python cli.py --coeffs "1, 5, 6, 2" --verify
```

### 2) Cubic with gain K: p(s) = s^3 + 5 s^2 + 6 s + K
```bash
python cli.py --coeffs "1, 5, 6, K" --symbol K --solve-for K
```

### 3) Quartic with gain + Hurwitz minors
```bash
python cli.py --coeffs "1, 2, 3, 4, K" --symbol K --solve-for K --hurwitz
```

### 4) Edge case: row of zeros  (p(s) = (s^2 + 1)^2)
```bash
python cli.py --coeffs "1, 0, 2, 0, 1" --verify
```

### 5) Export a JSON report to `out/<basename>.json`
```bash
python cli.py --coeffs "1, 5, 6, 2" --export demo
# -> writes transient_analysis/routhTool/out/demo.json
```

> Outputs (in/ out) are created under `transientAnalysis/routhTool/` automatically.


---

## ✅ Run from the repo root via the module entry point

From the repository root:

```bash
python -m transient_analysis.routhTool.cli --coeffs "1, 5, 6, 2" --verify
python -m transient_analysis.routhTool.cli --coeffs "1, 5, 6, K" --symbol K --solve-for K
python -m transient_analysis.routhTool.cli --coeffs "1, 2, 3, 4, K" --symbol K --solve-for K --hurwitz
python -m transient_analysis.routhTool.cli --coeffs "1, 0, 2, 0, 1" --verify
python -m transient_analysis.routhTool.cli --coeffs "1, 5, 6, 2" --export demo
```

---

## CLI flags recap

- `--coeffs "a0, a1, ..., an"` (required): polynomial coefficients in **descending** powers.
- `--symbol NAME` (repeatable): declare symbolic parameter(s) present in the coefficients.
- `--solve-for NAME`: solve the first-column `> 0` inequalities for this single symbol.
- `--hurwitz`: print leading principal Hurwitz minors (requires `sympy`).
- `--verify`: numerically verify number of RHP roots using `numpy.roots` (numeric-only).
- `--eps 1e-9`: epsilon used for the ε-trick when a row’s leading entry is zero.
- `--export NAME`: write a JSON report to `out/NAME.json`.

### Sphinx

python -m transient_analysis.routhTool.cli sphinx-skel transient_analysis/routhTool/docs
python -m sphinx -b html docs docs/_build/html
open docs/_build/html/index.html
sphinx-autobuild docs docs/_build/html