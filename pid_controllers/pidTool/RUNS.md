# RUNS for `pidControllers.pidTool` (Package-local)

Run these **from inside** the package directory:
```
cd pidControllers/pidTool
```

Assumes your venv is active (e.g., `source .venv/bin/activate`).  
All outputs (plots/JSON/CSV) are written to **`./out/`** (package-local).

---

## Quick help

Two equivalent ways to run:
```bash
# A) As a module (works from anywhere in the repo)
python -m pid_controllers.pidTool.cli --help
python -m pid_controllers.pidTool.cli run --help
```
```bash
# B) From inside the package (thanks to the import shim)
python cli.py --help
python cli.py run --help
```

---

## A) Ogata Example 8-2 (double-zero PID on his plant)

```bash
python cli.py run   --plant-form poly   --num-poly "1.2"   --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1"   --structure pid_dz   --K-range 2 3 --K-n 6   --a-range 0.5 1.5 --a-n 6   --max-overshoot 10   --objective itae   --backend plotly --plot-top 5   --export-json --export-csv   --save-prefix ogata82
```

---

## B) Same plant with full PID (coarse grid)

```bash
python cli.py run   --plant-form poly   --num-poly "1.2"   --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1"   --structure pid   --Kp-range 0.5 6 --Kp-n 6   --Ki-range 0.1 5 --Ki-n 6   --Kd-range 0.0 2.0 --Kd-n 5   --max-overshoot 10 --max-settling 3.0   --objective weighted --w-ts 1.0 --w-mp 0.2 --w-itae 0.5   --backend mpl --plot-top 4   --export-csv --save-prefix pid_coarse
```

---

## C) ZPK plant (factorized), PI/PD/PID-dz designs

### C1) Original (tight PI ranges) — *likely returns no candidate* with the given specs

```bash
python cli.py run   --plant-form zpk --gain 1.0 --zeros "" --poles "-1 -5 -10"   --structure pi   --pi-Kp-range 0.1 5 --pi-Kp-n 10   --pi-Ki-range 0.05 3 --pi-Ki-n 10   --max-overshoot 5 --max-settling 2.5   --backend none --export-json --save-prefix pi_zpk
```

### C2) Widened PI ranges (can meet specs; larger grid)

```bash
python cli.py run   --plant-form zpk --gain 1.0 --zeros "" --poles "-1 -5 -10"   --structure pi   --pi-Kp-range 20 400 --pi-Kp-n 25   --pi-Ki-range 1 120 --pi-Ki-n 25   --max-overshoot 5 --max-settling 2.5   --objective weighted --w-ts 1 --w-mp 1 --w-itae 0.2 --w-ise 0   --backend none --export-json --export-csv --save-prefix pi_zpk_wide
```

### C3) PD controller (adds phase lead; recommended)

```bash
python cli.py run   --plant-form zpk --gain 1.0 --zeros "" --poles "-1 -5 -10"   --structure pd   --pd-Kp-range 1 200 --pd-Kp-n 30   --pd-Kd-range 0.01 10 --pd-Kd-n 30   --max-overshoot 5 --max-settling 2.5   --objective weighted --w-ts 1 --w-mp 1 --w-itae 0.2   --backend plotly --plot-top 5 --save-prefix pd_zpk
```

### C4) PID “double-zero” (root-locus style; recommended)

```bash
python cli.py run   --plant-form zpk --gain 1.0 --zeros "" --poles "-1 -5 -10"   --structure pid_dz   --K-range 1 60 --K-n 25   --a-range 0.1 5 --a-n 25   --max-overshoot 5 --max-settling 2.5   --objective itae   --backend plotly --plot-top 5 --export-json --export-csv   --save-prefix pid_dz_zpk
```

---

## D) Coeff plant, PD design

```bash
python cli.py run   --plant-form coeff --num "1" --den "1 0 1"   --structure pd   --pd-Kp-range 0.5 20 --pd-Kp-n 8   --pd-Kd-range 0.0 5 --pd-Kd-n 8   --max-overshoot 20 --max-settling 5   --objective ts --backend plotly --plot-top 3 --save-prefix pd_demo
```

---

## E) Useful variants

### E1) Plot backends and saving

```bash
# Plotly HTML (full-width responsive)
python cli.py run \
  --plant-form poly \
  --num-poly "1.2" \
  --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1" \
  --structure pid_dz \
  --K-range 6 20 --K-n 40 \
  --a-range 0.45 1.8 --a-n 45 \
  --tfinal 25 --dt 0.002 \
  --settle-tol 0.05 \
  --objective itae \
  --backend plotly --plot-top 5 \
  --export-json --export-csv \
  --save-prefix demo_plotly
```

```bash
# Matplotlib PNG
python cli.py run \
  --plant-form poly \
  --num-poly "1.2" \
  --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1" \
  --structure pid_dz \
  --K-range 6 20 --K-n 40 \
  --a-range 0.45 1.8 --a-n 45 \
  --tfinal 25 --dt 0.002 \
  --settle-tol 0.05 \
  --objective itae \
  --backend mpl --plot-top 5 \
  --export-json --export-csv \
  --save-prefix demo_mpl
```

```bash
# No plot (export only)
python cli.py run \
  --plant-form poly \
  --num-poly "1.2" \
  --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1" \
  --structure pid_dz \
  --K-range 6 20 --K-n 40 \
  --a-range 0.45 1.8 --a-n 45 \
  --tfinal 25 --dt 0.002 \
  --settle-tol 0.05 \
  --objective itae \
  --backend none --plot-top 5 \
  --export-json --export-csv \
  --save-prefix demo_export
```

### E2) Objective choices

```bash
# ITAE (default)
python cli.py run \
  --plant-form poly \
  --num-poly "1.2" \
  --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1" \
  --structure pid_dz \
  --K-range 6 20 --K-n 40 \
  --a-range 0.45 1.8 --a-n 45 \
  --tfinal 25 --dt 0.002 \
  --settle-tol 0.05 \
  --objective itae \
  --backend plotly --plot-top 5 \
  --export-json --export-csv \
  --save-prefix obj_itae
```

```bash
# ISE
python cli.py run \
  --plant-form poly \
  --num-poly "1.2" \
  --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1" \
  --structure pid_dz \
  --K-range 6 20 --K-n 40 \
  --a-range 0.45 1.8 --a-n 45 \
  --tfinal 25 --dt 0.002 \
  --settle-tol 0.05 \
  --objective ise \
  --backend plotly --plot-top 5 \
  --export-json --export-csv \
  --save-prefix obj_ise
```

```bash
# Minimize settling time directly
python cli.py run \
  --plant-form poly \
  --num-poly "1.2" \
  --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1" \
  --structure pid_dz \
  --K-range 6 20 --K-n 40 \
  --a-range 0.45 1.8 --a-n 45 \
  --tfinal 25 --dt 0.002 \
  --settle-tol 0.05 \
  --objective ts \
  --backend plotly --plot-top 5 \
  --export-json --export-csv \
  --save-prefix obj_ts
```

```bash
# Weighted mix
python cli.py run \
  --plant-form poly \
  --num-poly "1.2" \
  --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1" \
  --structure pid_dz \
  --K-range 6 20 --K-n 40 \
  --a-range 0.45 1.8 --a-n 45 \
  --tfinal 25 --dt 0.002 \
  --settle-tol 0.05 \
  --objective weighted --w-ts 1 --w-mp 0.5 --w-itae 0.2 --w-ise 0 \
  --backend plotly --plot-top 5 \
  --export-json --export-csv \
  --save-prefix obj_weighted
```

### E3) Tighter settling band (e.g., 1% instead of 2%)

```bash
python cli.py run \
  --plant-form poly \
  --num-poly "1.2" \
  --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1" \
  --structure pid_dz \
  --K-range 6 20 --K-n 40 \
  --a-range 0.45 1.8 --a-n 45 \
  --tfinal 25 --dt 0.002 \
  --settle-tol 0.01 \
  --objective itae \
  --backend plotly --plot-top 5 \
  --export-json --export-csv \
  --save-prefix settle_1pct
```

### E4) Custom simulation horizon (if responses are truncated or too long)

```bash
python cli.py run \
  --plant-form poly \
  --num-poly "1.2" \
  --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1" \
  --structure pid_dz \
  --K-range 6 20 --K-n 40 \
  --a-range 0.45 1.8 --a-n 45 \
  --tfinal 20 --dt 0.002 \
  --settle-tol 0.05 \
  --objective itae \
  --backend plotly --plot-top 5 \
  --export-json --export-csv \
  --save-prefix horizon_20s
```

### E5) Two-stage search (coarse → refine, *looser specs example*)

1) **Stage 1 — Overshoot scout**
```bash
python cli.py run   --plant-form poly   --num-poly "1.2"   --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1"   --structure pid_dz   --K-range 6 20 --K-n 40   --a-range 0.45 1.8 --a-n 45   --tfinal 25 --dt 0.002   --settle-tol 0.05   --objective mp   --backend none --export-json --save-prefix dz_os_scout_demo
```
Open `./out/dz_os_scout_demo_results.json` and note the top `(K, a)` pairs.

2) **Stage 2 — Refine around the best `(K*, a*)`**
```bash
# Replace <K*> and <a*> with the Stage-1 best
python cli.py run   --plant-form poly   --num-poly "1.2"   --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1"   --structure pid_dz   --K-range <K*-1.0> <K*+1.0> --K-n 36   --a-range <a*-0.15> <a*+0.15> --a-n 36   --max-overshoot 15 --max-settling 3.4   --settle-tol 0.02   --tfinal 25 --dt 0.002   --objective weighted --w-ts 1.0 --w-mp 0.8 --w-itae 0.2   --backend plotly --plot-top 6   --export-json --export-csv --save-prefix dz_refine_demo
```

---

## Extras

```bash
# Mermaid class diagram (optional)
python -m pid_controllers.pidTool.tools.diagram_tool --emit-mermaid
# or, if you have the same shim pattern in diagram_tool.py:
# python tools/diagram_tool.py --emit-mermaid
# Writes ./out/pidTool_classes.mmd
```
