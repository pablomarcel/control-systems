# RUNS for `pidControllers.pidTool` (OOP refactor)

Run these from your **repo root** (where the `pidControllers/` folder lives).  
Assumes your venv is active (e.g., `source .venv/bin/activate`).  
All outputs (plots/JSON/CSV) are written to `pidControllers/pidTool/out/` by the app.

---

## Quick help

```bash
python -m pid_controllers.pidTool.cli --help
python -m pid_controllers.pidTool.cli run --help
```

---

## A) Ogata Example 8-2 (double-zero PID on his plant)

```bash
python -m pid_controllers.pidTool.cli run   --plant-form poly   --num-poly "1.2"   --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1"   --structure pid_dz   --K-range 2 3 --K-n 6   --a-range 0.5 1.5 --a-n 6   --max-overshoot 10   --objective itae   --backend plotly --plot-top 5   --export-json --export-csv   --save-prefix ogata82
```

---

## B) Same plant with full PID (coarse grid)

```bash
python -m pid_controllers.pidTool.cli run   --plant-form poly   --num-poly "1.2"   --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1"   --structure pid   --Kp-range 0.5 6 --Kp-n 6   --Ki-range 0.1 5 --Ki-n 6   --Kd-range 0.0 2.0 --Kd-n 5   --max-overshoot 10 --max-settling 3.0   --objective weighted --w-ts 1.0 --w-mp 0.2 --w-itae 0.5   --backend mpl --plot-top 4   --export-csv --save-prefix pid_coarse
```

---

## C) ZPK plant (factorized), PI/PD/PID-dz designs

### C1) Original (tight PI ranges) — **likely returns no candidate** with the given specs

```bash
python -m pid_controllers.pidTool.cli run   --plant-form zpk --gain 1.0 --zeros "" --poles "-1 -5 -10"   --structure pi   --pi-Kp-range 0.1 5 --pi-Kp-n 10   --pi-Ki-range 0.05 3 --pi-Ki-n 10   --max-overshoot 5 --max-settling 2.5   --backend none --export-json --save-prefix pi_zpk
```

### C2) Widened PI ranges (can meet specs; larger grid)

```bash
python -m pid_controllers.pidTool.cli run   --plant-form zpk --gain 1.0 --zeros "" --poles "-1 -5 -10"   --structure pi   --pi-Kp-range 20 400 --pi-Kp-n 25   --pi-Ki-range 1 120 --pi-Ki-n 25   --max-overshoot 5 --max-settling 2.5   --objective weighted --w-ts 1 --w-mp 1 --w-itae 0.2 --w-ise 0   --backend none --export-json --export-csv --save-prefix pi_zpk_wide
```

### C3) PD controller (adds phase lead; recommended)

```bash
python -m pid_controllers.pidTool.cli run   --plant-form zpk --gain 1.0 --zeros "" --poles "-1 -5 -10"   --structure pd   --pd-Kp-range 1 200 --pd-Kp-n 30   --pd-Kd-range 0.01 10 --pd-Kd-n 30   --max-overshoot 5 --max-settling 2.5   --objective weighted --w-ts 1 --w-mp 1 --w-itae 0.2   --backend plotly --plot-top 5 --save-prefix pd_zpk
```

### C4) PID “double-zero” (root-locus style; recommended)

```bash
python -m pid_controllers.pidTool.cli run   --plant-form zpk --gain 1.0 --zeros "" --poles "-1 -5 -10"   --structure pid_dz   --K-range 1 60 --K-n 25   --a-range 0.1 5 --a-n 25   --max-overshoot 5 --max-settling 2.5   --objective itae   --backend plotly --plot-top 5 --export-json --export-csv   --save-prefix pid_dz_zpk
```

---

## D) Coeff plant, PD design

```bash
python -m pid_controllers.pidTool.cli run   --plant-form coeff --num "1" --den "1 0 1"   --structure pd   --pd-Kp-range 0.5 20 --pd-Kp-n 8   --pd-Kd-range 0.0 5 --pd-Kd-n 8   --max-overshoot 20 --max-settling 5   --objective ts --backend plotly --plot-top 3 --save-prefix pd_demo
```

---

## E) Useful variants

### E1) Plot backends and saving

- Plotly HTML (full-width responsive):
```bash
python -m pid_controllers.pidTool.cli run ... --backend plotly --save-prefix demo_plotly
```
- Matplotlib PNG:
```bash
python -m pid_controllers.pidTool.cli run ... --backend mpl --save-prefix demo_mpl
```
- No plot (export only):
```bash
python -m pid_controllers.pidTool.cli run ... --backend none --export-json --export-csv --save-prefix demo_export
```

### E2) Objective choices

- ITAE (default):
```bash
python -m pid_controllers.pidTool.cli run ... --objective itae
```
- ISE:
```bash
python -m pid_controllers.pidTool.cli run ... --objective ise
```
- Minimize settling time directly:
```bash
python -m pid_controllers.pidTool.cli run ... --objective ts
```
- Weighted mix (tune weights as needed):
```bash
python -m pid_controllers.pidTool.cli run ... --objective weighted --w-ts 1 --w-mp 0.5 --w-itae 0.2 --w-ise 0
```

### E3) Tighter settling band (e.g., 1% instead of 2%)

```bash
python -m pid_controllers.pidTool.cli run ... --settle-tol 0.01
```

### E4) Custom simulation horizon (if responses are truncated or too long)

```bash
python -m pid_controllers.pidTool.cli run ... --tfinal 20 --dt 0.002
```

### E5) Two-stage search (coarse → refine)

1. **Coarse scan** (example for `pid_dz`):
```bash
python -m pid_controllers.pidTool.cli run   --plant-form poly   --num-poly "1.2"   --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1"   --structure pid_dz   --K-range 0.5 80 --K-n 30   --a-range 0.1 6 --a-n 30   --max-overshoot 10 --max-settling 3.0   --objective itae --backend none   --export-json --save-prefix coarse_pid_dz
```
2. Inspect `pidControllers/pidTool/out/coarse_pid_dz_results.json` for the best `K` and `a`, then **refine** narrowly around them, e.g.:
```bash
python -m pid_controllers.pidTool.cli run   --plant-form poly   --num-poly "1.2"   --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1"   --structure pid_dz   --K-range 12 20 --K-n 25   --a-range 0.55 0.9 --a-n 25   --max-overshoot 8 --max-settling 2.8   --objective weighted --w-ts 1 --w-mp 0.3 --w-itae 0.4   --backend plotly --plot-top 6   --export-json --export-csv --save-prefix refine_pid_dz
```

---

## Notes
- Empty zeros list must be written as `--zeros ""` (empty string).
- Zsh tip: keep quotes around polynomial strings and complex lists to avoid shell expansion.
- If a grid is very large, the tool prints a warning. Tighten ranges or reduce `*-n` to speed up.
- All plots/exports go to `pidControllers/pidTool/out/` automatically.
- Mermaid class diagram (optional):
```bash
python -m pid_controllers.pidTool.tools.diagram_tool --emit-mermaid
```
This writes `pidControllers/pidTool/out/pidTool_classes.mmd`.

## Two‑Stage Search (looser specs example)

This mirrors what we learned while exploring the Ogata 8‑2 plant with the `pid_dz` form.  
Goal here is **illustration** (find a good region fast), not strict final specs.  
We’ll use relaxed constraints to ensure feasibility, then refine.

### Stage 1 — Scout for lowest overshoot (no hard constraints)
Minimize overshoot directly to locate the low‑OS basin. Use a moderate horizon and a 5% settling band to avoid false negatives.

```bash
python -m pid_controllers.pidTool.cli run   --plant-form poly   --num-poly "1.2"   --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1"   --structure pid_dz   --K-range 6 20 --K-n 40   --a-range 0.45 1.8 --a-n 45   --tfinal 25 --dt 0.002   --settle-tol 0.05   --objective mp   --backend none --export-json --save-prefix dz_os_scout_demo
```
Open `pidControllers/pidTool/out/dz_os_scout_demo_results.json` and note the top 3–5 `(K, a)` pairs.

### Stage 2 — Refine with gentle specs (feasible & smooth)
Center around the best `(K*, a*)` from Stage 1. Use a **looser** spec for illustration (e.g., `OS ≤ 15%`, `Ts ≤ 3.4 s`, 2% settling band), and switch to a weighted objective that prefers faster settling but still penalizes overshoot.
# Replace <K*> and <a*> with your best from Stage 1
```bash
python -m pid_controllers.pidTool.cli run \
  --plant-form poly \
  --num-poly "1.2" \
  --den-poly "0.36*s**3 + 1.86*s**2 + 2.5*s + 1" \
  --structure pid_dz \
  --K-range 7.0 9.0 --K-n 36 \
  --a-range 0.45 0.75 --a-n 36 \
  --max-overshoot 15 --max-settling 3.4 \
  --settle-tol 0.02 \
  --tfinal 25 --dt 0.002 \
  --objective weighted --w-ts 1.0 --w-mp 0.8 --w-itae 0.2 \
  --backend plotly --plot-top 6 \
  --export-json --export-csv --save-prefix dz_refine_demo
```
**Tips**
- If you get “No candidate”, nudge the box slightly **up** in `a` (more damping) and **±10–15%** in `K`.
- If settling barely misses (e.g., 3.45 s), keep the same box and try `--objective ts` once to snap to the fastest point under the overshoot cap, then switch back to `weighted`.
- If you prefer, map the best `pid_dz` to a PID seed via `Kp=2Ka`, `Ki=Ka^2`, `Kd=K`, then run a small PID refine box with the same looser specs.

