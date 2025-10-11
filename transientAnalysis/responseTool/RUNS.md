# responseTool — RUNS.md (one command per block)

> **How to use:** open this file in PyCharm, copy/paste any single block into the terminal.
> All commands are meant to be run **from inside** `transientAnalysis/responseTool`.
>
> First, `cd` there:

```bash
cd transientAnalysis/responseTool
```

Artifacts are written to `transientAnalysis/responseTool/out` by default.
You can override the output root with `--root <dir>` (artifacts then go to `<dir>/out`).

---

## Linear Simulation

### A) Unit ramp via state‑space augmentation

```bash
python cli.py ramp-ss --A "0 1; -1 -1" --B "0; 1" --C "1 0" --D "0" --tfinal 10 --dt 0.01 --plot
```

### B) Arbitrary input (TF): ramp

```bash
python cli.py lsim-tf --num "2 1" --den "1 1 1" --input ramp --tfinal 10 --dt 0.01 --plot
```

### B) Arbitrary input (TF): sine

```bash
python cli.py lsim-tf --num "25" --den "1 4 25" --input sine --tfinal 10 --dt 0.01 --plot
```

### B) Arbitrary input (TF): square

```bash
python cli.py lsim-tf --num "25" --den "1 4 25" --input square --tfinal 10 --dt 0.01 --plot
```

### Class diagram (PlantUML text → `out/response_tool_classes.puml`)
> Uses package imports; add the project root to `PYTHONPATH` before the `python -c` call.
```bash
PYTHONPATH="$(pwd)/../.." python -c "from transientAnalysis.responseTool.tools.class_diagram import generate; import pathlib; print(generate(pathlib.Path('')))"
```

### Pytests (optional)

```bash
pytest transientAnalysis/responseTool/tests \
  --override-ini addopts= \
  --cov \
  --cov-config=transientAnalysis/responseTool/.coveragerc \
  --cov-report=term-missing
```

---

## Custom File Names MIMO System

### 1) Custom plant, step from **u1**, custom prefix

```bash
python cli.py step-ss --A "-1 -1; 6.5 0" --B "1 1; 1 0" --C "1 0; 0 1" --D "0 0; 0 0" --input-index 0 --tfinal 8 --dt 0.01 --save-prefix "plantA_u" --plot
```

*(Outputs: `out/plantA_u1.json`, `out/plantA_u1.png`)*

### 2) Step from **u2**, also export states with custom prefix

```bash
python cli.py step-ss --A "-1 -1; 6.5 0" --B "1 1; 1 0" --C "1 0; 0 1" --D "0 0; 0 0" --input-index 1 --tfinal 8 --dt 0.01 --save-prefix "robotArm_u" --states --states-name "robotArm_states_u" --plot
```

*(Outputs: `out/robotArm_u2.json|.png`, `out/robotArm_states_u2.json|.png`)*

### 3) Put artifacts in a different folder (no filename changes)

```bash
python cli.py --root out step-ss --A "-1 -1; 6.5 0" --B "1 1; 1 0" --C "1 0; 0 1" --D "0 0; 0 0" --input-index 0 --tfinal 5 --dt 0.005 --save-prefix "arm_run_u" --states --states-name "arm_run_states_u" --plot
```

### 4) Metrics only (writes `out/ex5_3_step_metrics.json`)

```bash
python cli.py step-ss --metrics --A "-1 -1; 6.5 0" --B "1 1; 1 0" --C "1 0; 0 1" --D "0 0; 0 0"
```

> Note: `--input-index` is **0‑based**.

---

## Second Order Systems

### Single (parameters)

```bash
python cli.py second-order --wn 5 --zeta 0.4 --tfinal 2 --dt 0.001 --plot --save-prefix "plantB"
```

*(→ `out/plantB_single.json|.png`)*

### Single (coeffs: `K a2 a1 a0`)

```bash
python cli.py second-order --coeffs 25 1 4 25 --tfinal 2 --dt 0.001 --plot --save-prefix "from_coeffs"
```

*(→ `out/from_coeffs_single.json|.png`)*

### ζ‑sweep

```bash
python cli.py second-order --wn 5 --sweep-zeta "0.0,0.2,0.4,0.7,1.0,2.0" --tfinal 2 --dt 0.001 --plot --save-prefix "sweep_demo"
```

*(→ `out/sweep_demo_sweep.json|.png`)*

### Alternate output root

```bash
python cli.py --root transientAnalysis/responseTool/out second-order --wn 5 --zeta 0.4 --plot
```

---

## Example Section 5‑5

### 1) Standard form (given ωn, ζ)

```bash
python cli.py second-order --wn 5 --zeta 0.4 --tfinal 2 --dt 0.001 --plot --save-prefix "ex5_5_1"
```

*(→ `out/ex5_5_1_single.json|.png`)*

### 2) From coefficients (`25/(s^2 + 4 s + 25)`)

```bash
python cli.py second-order --coeffs 25 1 4 25 --tfinal 2 --dt 0.001 --plot --save-prefix "ex5_5_1_coeffs"
```

*(→ `out/ex5_5_1_coeffs_single.json|.png`)*

### 3) ζ sweep

```bash
python cli.py second-order --wn 5 --sweep-zeta "0.0,0.2,0.4,0.7,1.0,2.0" --tfinal 2 --dt 0.001 --plot --save-prefix "ex5_5_1_sweep"
```

*(→ `out/ex5_5_1_sweep.json|.png`)*

### 4) Custom output root (“double‑out” example)

```bash
python cli.py --root out second-order --wn 5 --zeta 0.4 --plot --save-prefix "ex5_5_1"
```

*(→ `transientAnalysis/responseTool/out/out/ex5_5_1_single.json|.png`)*

---

## Second Order Overlays

### 2D overlays (custom ζ list + prefix)

```bash
python cli.py second-order-overlays --wn 5 --zetas "0,0.2,0.4,0.8,1.0" --tfinal 8 --dt 0.01 --save-prefix "std2_overlay_demo" --plot
```

*(→ `out/std2_overlay_demo_2D.json`, `out/std2_overlay_demo_2D.png`)*

### 3D mesh (surface + heatmap)

```bash
python cli.py second-order-mesh --wn 5 --zeta-min 0 --zeta-max 1 --zeta-steps 51 --tfinal 8 --dt 0.01 --save-prefix "std2_surface_demo" --plot
```

*(→ `out/std2_surface_demo_3D.json`, `out/std2_surface_demo_3D.png`, `out/std2_surface_demo_3D_heatmap.png`)*

### Put results in a specific folder

```bash
python cli.py second-order-overlays --root transientAnalysis/responseTool/out/out --wn 5 --zetas "0,0.3,0.6,1.0" --tfinal 8 --dt 0.01 --save-prefix "overlay_run" --plot
```

```bash
python cli.py second-order-mesh --root transientAnalysis/responseTool/out/out --wn 3 --zeta-min 0 --zeta-max 1 --zeta-steps 61 --tfinal 10 --dt 0.01 --save-prefix "mesh_run" --plot
```

---

## Plotly 3D Plots

> Requires `plotly` (and optionally `kaleido` for PNG). A JSON snapshot is always saved.

### Minimal interactive surface (JSON snapshot)

```bash
python cli.py second-order-plotly --wn 5 --zeta-min 0 --zeta-max 1 --zeta-steps 61 --tfinal 8 --dt 0.01 --save-prefix "std2_plotly"
```

### Save interactive HTML with overlayed ζ slices

```bash
python cli.py second-order-plotly --wn 5 --zeta-min 0 --zeta-max 1 --zeta-steps 61 --tfinal 8 --dt 0.01 --overlay "0,0.2,0.7,1.0" --title "Overlay slices" --save-prefix "std2_plotly_overlay" --save-html "std2_plotly_overlay.html"
```

### Save PNG too (needs `kaleido`)

```bash
python cli.py second-order-plotly --wn 3 --zeta-min 0 --zeta-max 1 --zeta-steps 41 --tfinal 6 --dt 0.01 --overlay "0.1,0.4,0.7" --save-prefix "std2_plotly_png" --save-html "std2_plotly_png.html" --save-png "std2_plotly_png.png"
```
