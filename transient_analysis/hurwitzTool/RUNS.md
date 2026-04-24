# Hurwitz Tool — Run Book (OO refactor)

This module provides a CLI for Hurwitz stability analysis that can be executed either:
- **From the project root** using `python -m transientAnalysis.hurwitzTool.cli ...`, or
- **From inside the package directory** using `python cli.py ...` (thanks to an import shim).

The examples below mirror the original standalone `hurwitz_tool_pro.py` commands.

---

## A. Run from the project root

From `modernControl/` (the repo root):

### 1) 1‑D exact region + pretty intervals
```bash
python -m transient_analysis.hurwitzTool.cli --coeffs "1, 5, 6, K" --symbols K --solve-for K --intervals-pretty
```
Output shows:
- Δ’s, the inequality system, and reduced region like `(0 < K) & (K < 30)`
- Pretty intervals: `(-∞, 0) ∪ (0, 30)` and **LaTeX**

### 2) 2‑D symbolic + scan (ASCII and PNG heatmap)
```bash
python -m transient_analysis.hurwitzTool.cli       --coeffs "1, 2, 4+K, 9, 25" --symbols "K,alpha" --solve-for "K,alpha"       --scan2 "K:0:15:0.1;alpha:-1:1:0.1" --csv2 out/region.csv --png out/region.png
```
Notes:
- Prints Δ’s and inequalities (exact condition if SymPy can reduce)
- Samples the rectangle and prints an ASCII heatmap
- Saves CSV to `out/region.csv` and PNG to `out/region.png` (relative to `--base-dir`, default `.`)

### 3) Classic numeric checks with verification
```bash
python -m transient_analysis.hurwitzTool.cli       --coeffs "1, 2, 4+K, 9, 25" --symbols K --subs "K=7.0" --verify
```

### 4) Liénard–Chipart for speed (requires a_i > 0)
```bash
python -m transient_analysis.hurwitzTool.cli       --coeffs "1, 2, 4+K, 9, 25" --symbols K --solve-for K --lienard --intervals-pretty
```

### Optional: choose IO base directory
All file outputs are resolved relative to `--base-dir` (defaults to current working directory).
For example:
```bash
python -m transient_analysis.hurwitzTool.cli ... --base-dir transient_analysis/hurwitzTool
```
will save under `transientAnalysis/hurwitzTool/out/` when `--csv/--csv2/--png` are used.

---

## B. Run from inside the package directory

You can also `cd transientAnalysis/hurwitzTool` and run `python cli.py ...` directly.
The CLI includes an **import shim** so absolute imports resolve without installing the package.

From `modernControl/transientAnalysis/hurwitzTool/`:

### 1) 1‑D exact region + pretty intervals
```bash
python cli.py --coeffs "1, 5, 6, K" --symbols K --solve-for K --intervals-pretty
```

### 2) 2‑D symbolic + scan (ASCII and PNG heatmap)
```bash
python cli.py       --coeffs "1, 2, 4+K, 9, 25" --symbols "K,alpha" --solve-for "K,alpha"       --scan2 "K:0:15:0.1;alpha:-1:1:0.1" --csv2 out/region.csv --png out/region.png
```

### 3) Classic numeric checks with verification
```bash
python cli.py --coeffs "1, 2, 4+K, 9, 25" --symbols K --subs "K=7.0" --verify
```

### 4) Liénard–Chipart for speed (requires a_i > 0)
```bash
python cli.py --coeffs "1, 2, 4+K, 9, 25" --symbols K --solve-for K --lienard --intervals-pretty
```

---

## Tips
- Use `--csv` with `--scan` (1‑D) and `--csv2`/`--png` with `--scan2` (2‑D).
- `--base-dir` controls the IO root (it creates `in/` and `out/` under that directory).
- If you run into import issues in custom environments, ensure the repo root is in `PYTHONPATH` or stick to the root-run form `python -m transientAnalysis.hurwitzTool.cli`.
