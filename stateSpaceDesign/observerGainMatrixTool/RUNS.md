# observerGainMatrixTool — RUNS.md (inside-package edition)

These examples are designed to be executed **from inside** this folder:
```
modernControl/stateSpaceDesign/observerGainMatrixTool/
```
Use the import shim in `cli.py` by calling:
```
python cli.py <args...>
```

> Notes
> - If a value starts with `-`, prefer the **equals form**, e.g. `--K_poles="-3,-4"`.
> - `--export_json` path rules in this tool:
>   - **Absolute** or **path/with/dirs** → the file is written **exactly there**.
>   - **Bare filename** (e.g., `results.json`) → written to the **current working directory**.
> - All examples below assume you are **inside** this folder. When you run from the repo root, see Section 9.
> - Outputs (LaTeX, JSON, etc.) are small and safe for CI headless runs.

---

## 0) Help

```bash
python cli.py --help
```

---

## 1) Minimal observer (SISO C) — JSON to stdout

```bash
python cli.py \
  --A "0 1; -2 -3" \
  --C "1 0" \
  --poles -5 -6
```

### 1.1) Pretty summary

```bash
python cli.py \
  --A "0 1; -2 -3" \
  --C "1 0" \
  --poles -5 -6 \
  --pretty
```

### 1.2) Export JSON to the current folder

```bash
python cli.py \
  --A "0 1; -2 -3" \
  --C "1 0" \
  --poles -5 -6 \
  --export_json out/observer_basic.json
```

---

## 2) Controller K via poles (robust `--K_poles` parsing)

### 2.1) Equals-form CSV (recommended when values start with `-`)

```bash
python cli.py \
  --A "0 1; -2 -3" --B "0;1" --C "1 0" \
  --poles -8 -9 \
  --K_poles="-3,-4" \
  --export_json out/observer_with_K.csvform.json
```

### 2.2) List form (separate tokens)

```bash
python cli.py \
  --A "0 1; -2 -3" --B "0;1" --C "1 0" \
  --poles -8 -9 \
  --K_poles_list "-3" "-4" \
  --export_json out/observer_with_K_list.json
```

---

## 3) Observer synthesis methods

### 3.1) Dual place (default `--method auto` may use place)

```bash
python cli.py \
  --A "0 1; -2 -3" \
  --C "1 0" \
  --poles -5 -6 \
  --method place \
  --export_json out/place_basic.json
```

### 3.2) Ackermann dual (requires SISO C)

```bash
python cli.py \
  --A "0 1; -2 -3" \
  --C "1 0" \
  --poles -5 -6 \
  --method ack \
  --export_json out/ack_basic.json
```

### 3.3) Jitter fallback (when repeated pole multiplicity exceeds `p = rows(C)` for place)

```bash
python cli.py \
  --A "0 1; -2 -3" \
  --C "1 0" \
  --poles -5 -5 \
  --method place --place_fallback jitter --jitter_eps 1e-6 \
  --export_json out/place_jitter.json
```

---

## 4) MIMO output (multi-row C) with place

```bash
python cli.py \
  --A "0 1; -2 -3" \
  --C "1 0; 0 1" \
  --poles -4 -6 \
  --method place \
  --export_json out/place_mimo.json
```

> For MIMO outputs, Ackermann is not available; use `--method place` (or `--method auto`).

---

## 5) Closed loop + observer-controller transfer + simulation

### 5.1) Build augmented matrix and Gc(s), no simulation

```bash
python cli.py \
  --A "0 1; -2 -3" --B "0;1" --C "1 0" \
  --poles -8 -9 \
  --K_poles="-3,-4" \
  --compute_closed_loop \
  --export_json out/closed_loop_no_sim.json
```

### 5.2) Add a short zero-input simulation

```bash
python cli.py \
  --A "0 1; -2 -3" --B "0;1" --C "1 0" \
  --poles -8 -9 \
  --K_poles="-3,-4" \
  --compute_closed_loop \
  --x0 "1,0" --e0 "0,0" --t_final 2 --dt 0.01 \
  --export_json out/closed_loop_with_sim.json
```

### 5.3) Pretty + closed loop + simulation

```bash
python cli.py \
  --A "0 1; -2 -3" --B "0;1" --C "1 0" \
  --poles -8 -9 \
  --K_poles="-3,-4" \
  --compute_closed_loop \
  --x0 "1,0" --e0 "0,0" --t_final 2 --dt 0.01 \
  --pretty \
  --export_json out/closed_loop_pretty.json
```

---

## 6) Explicit K (bypass K pole placement)

```bash
python cli.py \
  --A "0 1; -2 -3" --B "0;1" --C "1 0" \
  --poles -8 -9 \
  --K "3.0 1.0" \
  --compute_closed_loop \
  --x0 "1,0" --e0 "0,0" --t_final 1 --dt 0.01 \
  --export_json out/explicit_K.json
```

---

## 7) LaTeX snippet for the observer equation

```bash
python cli.py \
  --A "0 1; -2 -3" --B "0;1" --C "1 0" \
  --poles -5 -6 \
  --latex observer_eq.tex \
  --export_json out/latex_only.json
```
The LaTeX file is written to `./observer_eq.tex` and the path is echoed in JSON.

---

## 8) Logging and diagnostics

```bash
python cli.py \
  --A "0 1; -2 -3" --C "1 0" \
  --poles -5 -6 \
  --log INFO
```

### 8.1) Common errors (examples)

- Not observable:
  ```bash
  python cli.py --A "0 1; -2 -3" --C "0 0" --poles -5 -6
  ```
- Missing `B` when supplying controller poles:
  ```bash
  python cli.py --A "0 1; -2 -3" --C "1 0" --poles -5 -6 --K_poles="-3,-4"
  ```

---

## 9) Running **from project root**

From repository root (containing `stateSpaceDesign/`):
```bash
python -m stateSpaceDesign.observerGainMatrixTool.cli --help
```

Examples (module form):
```bash
python -m stateSpaceDesign.observerGainMatrixTool.cli \
  --A "0 1; -2 -3" --C "1 0" --poles -5 -6 --pretty

python -m stateSpaceDesign.observerGainMatrixTool.cli \
  --A "0 1; -2 -3" --B "0;1" --C "1 0" \
  --poles -8 -9 --K_poles="-3,-4" \
  --compute_closed_loop --x0 "1,0" --e0 "0,0" --t_final 2 --dt 0.01 \
  --export_json stateSpaceDesign/observerGainMatrixTool/out/closed_loop_from_root.json
```

---

## 10) Class diagram tool (inside this folder)

```bash
python tools/tool_class_diagram.py --out ./out/observerGainMatrixTool.mmd
```
Render with Mermaid (or just commit the `.mmd` to your docs).

> To run via module from repo root:
> ```bash
> python -m stateSpaceDesign.observerGainMatrixTool.tools.tool_class_diagram --out stateSpaceDesign/observerGainMatrixTool/out/observerGainMatrixTool.mmd
> ```

---

## 11) Quick CI smoke (fast, headless)

```bash
python cli.py \
  --A "0 1; 0 -1" --C "1 0" \
  --poles -5 -6 \
  --export_json ./smoke.json
```

---

## 12) Tips

- For reproducible artifacts in CI, prefer `--export_json` paths under the working directory.
- If `python-control` is not installed, `--method ack` still supports SISO observers; multi-row `C` requires `--method place`.
- Use equals-form for any argument whose immediate value starts with `-`, e.g. `--K_poles="-1.8+2.4j,-1.8-2.4j"`.
