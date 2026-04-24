
# lqrTool — RUNS.md (inside-package edition)

These examples are designed to be executed **from inside** the folder:
```
modernControl/stateSpaceDesign/lqrTool/
```
Use the import shim in `cli.py` by calling:
```
python cli.py <args...>
```

> Notes
> - When using `--save_prefix` with a **basename** (e.g., `--save_prefix quickrun`), files are saved in **./out/** relative to this folder.
> - Add `--no_show` to suppress interactive figure windows in automated runs.
> - `--plots` accepts `mpl`, `plotly`, `both`, or `none`.

---

## 0) Help

```bash
python cli.py --help
```

---

## 1) Ogata Example 10-13 — step (Ogata prefilter)

```bash
python cli.py   --A "0 1 0; 0 0 1; 0 -2 -3" --B "0; 0; 1"   --Q "diag:100,1,1" --R "0.01"   --C "1 0 0"   --step --prefilter ogata --tfinal 8 --dt 0.01 --plots mpl   --save_prefix out/ogata1013
```

### 1.1) Same plant, unity‑DC prefilter

```bash
python cli.py   --A "0 1 0; 0 0 1; 0 -2 -3" --B "0; 0; 1"   --Q "diag:100,1,1" --R "0.01"   --C "1 0 0"   --step --prefilter dcgain --tfinal 8 --plots mpl   --save_prefix out/ogata1013_dc
```

### 1.2) Same plant, no prefilter (raw regulator)

```bash
python cli.py   --A "0 1 0; 0 0 1; 0 -2 -3" --B "0; 0; 1"   --Q "diag:100,1,1" --R "0.01"   --C "1 0 0"   --step --prefilter none --tfinal 8 --dt 0.01 --plots mpl   --save_prefix out/ogata1013_none
```

---

## 2) Initial‑condition response only

```bash
python cli.py   --A "0 1; 0 -1" --B "0; 1"   --Q "eye" --R "1"   --x0 "1 1" --tfinal 6 --plots mpl   --save_prefix out/ic_demo
```

### 2.1) Initial‑condition with Plotly (no window)

```bash
python cli.py   --A "0 1; 0 -1" --B "0; 1"   --Q "eye" --R "1"   --x0 "1 0" --tfinal 2 --dt 0.02   --plots plotly --no_show   --save_prefix out/ic_plotly
```

---

## 3) Transfer‑function path

### 3.1) First‑order plant, step track (dcgain prefilter)

```bash
python cli.py   --num "1" --den "1, 1"   --Q "eye:1" --R "1"   --C "1"   --step --prefilter dcgain --tfinal 4 --dt 0.01 --plots mpl   --save_prefix out/tf_first_order
```

### 3.2) Second‑order plant, step track with amplitude and Plotly

```bash
python cli.py   --num "1" --den "1, 0.2, 1"   --Q "eye:2" --R "0.5"   --C "1 0"   --step --step_amp 2.0 --prefilter dcgain   --tfinal 6 --dt 0.01 --plots plotly --no_show   --save_prefix out/tf_second_order
```
> If the DC map is numerically near zero for some designs, the tool will warn and use `N=0` (safe fallback).

---

## 4) Weight specification variants

### 4.1) Diagonal Q via `diag:` and scalar R

```bash
python cli.py   --A "0 1; -2 -3" --B "0; 1" --C "1 0"   --Q "diag:10,1" --R "0.1"   --step --prefilter dcgain --tfinal 5 --dt 0.01 --plots mpl   --save_prefix out/weights_diag_scalar
```

### 4.2) Full‑matrix Q (SISO) with scalar R

```bash
python cli.py   --A "0 1; -2 -3" --B "0; 1" --C "1 0"   --Q "1 0; 0 0.5" --R "1"   --step --prefilter dcgain --tfinal 5 --plots mpl   --save_prefix out/weights_full
```
> For SISO, `R` must be a scalar. For MIMO with `m` inputs, `R` must be `m×m`.

### 4.3) Identity Q via `eye:n`

```bash
python cli.py   --A "0 1 0; 0 0 1; -1 -2 -3" --B "0; 0; 1" --C "1 0 0"   --Q "eye:3" --R "1"   --step --prefilter dcgain --tfinal 5 --plots none   --save_prefix out/weights_eye3
```

---

## 5) JSON summaries and headless runs

### 5.1) Export JSON (stdout + file)

```bash
python cli.py   --A "0 1 0; 0 0 1; 0 -2 -3" --B "0; 0; 1"   --Q "diag:100,1,1" --R "0.01"   --C "1 0 0"   --step --prefilter ogata --tfinal 2 --dt 0.05 --plots none --no_show   --export_json out/ogata1013.json
```
> Eigenvalues are exported as `[real, imag]` numeric pairs.

---

## 6) Mixed backends and artifacts

### 6.1) Generate both MPL and Plotly artifacts

```bash
python cli.py   --A "0 1; 0 -1" --B "0; 1" --C "1 0"   --Q "eye" --R "1"   --x0 "1 0"   --tfinal 2 --dt 0.05 --plots both --no_show   --save_prefix out/both_ic
```

### 6.2) Disable plots entirely (numbers only)

```bash
python cli.py   --A "0 1 0; 0 0 1; 0 -2 -3" --B "0; 0; 1"   --Q "diag:100,1,1" --R "1" --C "1 0 0"   --step --prefilter dcgain --tfinal 2 --dt 0.02 --plots none
```

---

## 7) Timebase variations

```bash
python cli.py   --A "0 1; -10 -5" --B "0; 1" --C "1 0"   --Q "diag:5,1" --R "0.1"   --step --prefilter dcgain   --tfinal 1.5 --dt 0.002 --plots none   --save_prefix out/timebase_fine
```

---

## 8) Class diagram tool (inside this folder)

### 8.1) Run the script directly from here

```bash
python tools/tool_classdiagram.py --out out/lqrTool.dot
```

Then render with Graphviz (if installed):
```bash
dot -Tpng out/lqrTool.dot -o out/lqrTool.png
```

> To run via module path instead, execute from **project root**:
> ```bash
> python -m state_space_design.lqrTool.tools.tool_classdiagram --out state_space_design/lqrTool/out/lqrTool.dot
> ```

---

## 9) Quick sanity smoke (fast, headless)

```bash
python cli.py   --A "0 1; 0 -1" --B "0; 1" --C "1 0"   --Q "eye" --R "1"   --step --prefilter dcgain --tfinal 0.5 --dt 0.05   --plots none --no_show   --export_json out/smoke.json
```

---

## 10) Tips

- For reproducible artifacts in CI, prefer `--plots none` or add `--no_show`.
- Use `--save_prefix out/<name>` to keep output in the package-level `out/` directory when running from inside this folder.
- On systems without a display, matplotlib will auto-switch or you can force a non-interactive backend via `MPLBACKEND=Agg`.
