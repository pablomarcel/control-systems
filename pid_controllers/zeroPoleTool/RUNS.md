# zeroPoleTool — Package-Local RUNS
Run these **from inside** `modernControl/pidControllers/zeroPoleTool/`.

Primary entrypoint here is the local script:
```
python cli.py --help
```
(You can still use the module form from anywhere: `python -m pidControllers.zeroPoleTool.cli ...`)

Outputs go to the package-local folder:
```
pidControllers/zeroPoleTool/out/
```

> Keep quotes around polynomial strings to avoid shell expansion.  
> Plotly is optional; if missing, plots are skipped with a warning.

---

## 0) Help / sanity

```bash
python cli.py --help
```

Small smoke run (single-point grid):
```bash
python cli.py   --plant-form coeff --num "1" --den "1,2,1"   --a-vals "2.0" --b-vals "2.0" --c-vals "1.0"   --os-min 0 --os-max 100 --ts-max 10   --no-progress
```

---

## A) Ogata Problem A-8-13 — Topology Fig. 8-30
**Plant**: \( G_p(s) = \dfrac{100}{s(s+1)} \).  
**Dominant poles**: \( -5 \pm j5 \), third at \( -5 \).

### 1) Exact (using the book poles)
```bash
python cli.py   --arch fig8-30   --plant-form poly --num-poly "100" --den-poly "s*(s+1)"   --a-vals "5" --b-vals "5" --c-vals "5"   --plots step_ref step_dist ramp_ref accel_ref   --export-json --export-csv
```

### 2) Search (≤25% OS, Ts ≤ 1.2 s)
```bash
python cli.py   --arch fig8-30   --plant-form poly --num-poly "100" --den-poly "s*(s+1)"   --a-range 3 6 --a-n 31   --b-range 3 6 --b-n 31   --c-range 3 7 --c-n 21   --os-min 15 --os-max 25 --ts-max 1.2   --rank-dist-peak-weight 0.3   --plots step_ref step_dist ramp_ref accel_ref   --export-json --export-csv --best-effort
```

---

## B) Ogata Example 8-5 — Topology Fig. 8-30
**Plant**: \( G_p(s) = \dfrac{5}{(s+1)(s+5)} \).  
(Highlights: dominant near \( -3 \pm j2 \), third \( \approx -6.605 \)).

### 1) Exact (book poles)
```bash
python cli.py   --arch fig8-30   --plant-form poly --num-poly "5" --den-poly "(s+1)*(s+5)"   --a-vals "3.6056" --b-vals "2" --c-vals "6.6051"   --plots step_ref step_dist ramp_ref accel_ref   --export-json --export-csv
```

### 2) Grid search (recommended region)
```bash
python cli.py   --arch fig8-30   --plant-form poly --num-poly "5" --den-poly "(s+1)*(s+5)"   --a-range 2 6 --a-n 21   --b-range 1.5 2.5 --b-n 21   --c-range 4 10 --c-n 31   --os-min 0 --os-max 25 --ts-max 2.0   --plots step_ref step_dist ramp_ref accel_ref   --export-json --export-csv --best-effort   --save-prefix ogata85 --plot-prefix ogata85
```

### 3) Replicate highlighted poles directly
```bash
python cli.py   --arch fig8-30   --plant-form poly --num-poly "5" --den-poly "(s+1)*(s+5)"   --a-vals "3" --b-vals "2" --c-vals "6.6051"   --os-min 0 --os-max 25 --ts-max 2.0   --plots step_ref step_dist ramp_ref accel_ref   --export-json --export-csv   --save-prefix ogata85_pinned --plot-prefix ogata85_pinned
```

---

## C) Ogata Example 8-4 — Topology Fig. 8-31 (original two-DOF form)
**Plant**: \( G_p(s) = \dfrac{10}{s(s+1)} \).

### 1) Grid search (ranked by disturbance peak = 1.0)
```bash
python cli.py   --arch fig8-31   --plant-form poly --num-poly "10" --den-poly "s*(s+1)"   --a-range 2 6 --a-n 21   --b-range 2 6 --b-n 21   --c-range 6 12 --c-n 31   --os-min 2 --os-max 19 --ts-max 1.0   --rank-dist-peak-weight 1.0   --plots step_ref step_dist ramp_ref accel_ref   --export-json --export-csv --best-effort
```

### 2) Same search with heavier disturbance ranking (2.0)
```bash
python cli.py   --arch fig8-31   --plant-form poly --num-poly "10" --den-poly "s*(s+1)"   --a-range 2 6 --a-n 21   --b-range 2 6 --b-n 21   --c-range 6 12 --c-n 31   --os-min 2 --os-max 19 --ts-max 1.0   --rank-dist-peak-weight 2.0   --plots step_ref step_dist ramp_ref accel_ref   --export-json --export-csv --best-effort
```

---

## D) Coeff / ZPK forms — examples

### 1) Coefficient form (plus exports)
```bash
python cli.py   --plant-form coeff --num "1" --den "1,2,1"   --a-vals "2.0 2.5" --b-vals "2.0" --c-vals "1.0"   --os-min 0 --os-max 100 --ts-max 10   --plots step_ref step_dist   --export-json --export-csv --best-effort   --save-prefix coeff_demo --plot-prefix coeff_demo
```

### 2) ZPK form (no zeros, 2 poles), Fig. 8-31
```bash
python cli.py   --arch fig8-31   --plant-form zpk --zeros "" --poles "-1 -5" --gain 5   --a-range 2 6 --a-n 9   --b-range 2 6 --b-n 9   --c-range 6 12 --c-n 13   --os-min 2 --os-max 19 --ts-max 1.0   --plots step_ref   --best-effort
```

---

## E) Prefixes & minimal outputs

### 1) Custom file prefixes (JSON/CSV/HTML)
```bash
python cli.py   --plant-form poly --num-poly "5" --den-poly "(s+1)*(s+5)"   --a-vals "3" --b-vals "2" --c-vals "6.6051"   --plots step_ref   --export-json --export-csv   --save-prefix custom_run --plot-prefix custom_run
```

### 2) No plots / fast ranking run
```bash
python cli.py   --plant-form poly --num-poly "10" --den-poly "s*(s+1)"   --a-range 2 6 --a-n 11   --b-range 2 6 --b-n 11   --c-range 6 12 --c-n 17   --os-min 2 --os-max 19 --ts-max 1.0   --no-progress
```

---

## Notes & Gotchas
- **Plots**: `--plots` supports `step_ref`, `step_dist`, `ramp_ref`, `accel_ref`. If Plotly is not installed, calls are skipped with a warning.
- **Best-effort**: If no candidate meets specs and `--best-effort` is set, the tool promotes the closest candidate so you still get channels/plots.
- **Performance**: Big grids can be slow; tighten ranges or reduce `*-n` for speed.
- **Exports**: JSON/CSV end up in `./out/` (this package’s `out` folder). Use `--save-prefix`/`--plot-prefix` to avoid overwrites.
