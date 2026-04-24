# icTool — RUNS.md

This page shows how to run the **response to initial conditions** demos/tests directly
from *inside the package directory* (`transientAnalysis/icTool/`) **and** from the repo root.

The CLI now includes an **import shim**, so `python cli.py ...` works when you’re cd’ed
inside `transientAnalysis/icTool/` — no need to use `-m` if you don’t want to.

---

## 0) Requirements

```bash
pip install numpy matplotlib control click
```

(Optional) If running on a headless box, set a non-interactive backend before plotting:

```bash
export MPLBACKEND=Agg
```

Artifacts (plots/JSON) are written to:

```bash
echo transient_analysis/icTool/out/
```

---

## 1) Run from the repo root

### Case 1 (states), compare direct vs step-equivalent
```bash
python -m transient_analysis.icTool.cli compare1   --A "0 1; -6 -5"   --x0 "2; 1"   --tfinal 3 --dt 0.005   --save
```

### Case 2 (outputs), compare direct vs step-equivalent
```bash
python -m transient_analysis.icTool.cli compare2   --A "0 1 0; 0 0 1; -10 -17 -8"   --C "1 0 0"   --x0 "2; 1; 0.5"   --tfinal 10 --dt 0.01   --save
```

### Only states (Case 1)
```bash
python -m transient_analysis.icTool.cli case1   --A "0 1; -2 -3"   --x0 "0.1; 0.05"   --tfinal 3 --dt 0.005   --save
```

### Only outputs (Case 2)
```bash
python -m transient_analysis.icTool.cli case2   --A "0 1; -6 -5"   --C "1 0; 0 1"   --x0 "1; -0.5"   --tfinal 3 --dt 0.005   --save
```

### TF path — Ogata Ex. 5-8 (with analytic overlay + JSON)
```bash
python -m transient_analysis.icTool.cli tf-step-ogata   --m 1 --b 3 --k 2 --x0 0.10 --v0 0.05   --tfinal 5 --dt 0.01   --save --json --analytic
```

### TF path — Generic G_ic(s) = num_ic/den
```bash
python -m transient_analysis.icTool.cli tf-step   --num_ic "0.1 0.05 0"   --den "1 3 2"   --tfinal 5 --dt 0.01   --save --json
```

---

## 2) Run from *inside* `transientAnalysis/icTool/`

First, change into the package directory:

```bash
cd transient_analysis/icTool/
```

### Case 1 (states), compare direct vs step-equivalent
```bash
python cli.py compare1   --A "0 1; -6 -5"   --x0 "2; 1"   --tfinal 3 --dt 0.005   --save
```

### Case 2 (outputs), compare direct vs step-equivalent
```bash
python cli.py compare2   --A "0 1 0; 0 0 1; -10 -17 -8"   --C "1 0 0"   --x0 "2; 1; 0.5"   --tfinal 10 --dt 0.01   --save
```

### Only states (Case 1)
```bash
python cli.py case1   --A "0 1; -2 -3"   --x0 "0.1; 0.05"   --tfinal 3 --dt 0.005   --save
```

### Only outputs (Case 2)
```bash
python cli.py case2   --A "0 1; -6 -5"   --C "1 0; 0 1"   --x0 "1; -0.5"   --tfinal 3 --dt 0.005   --save
```

### TF path — Ogata Ex. 5-8 (with analytic overlay + JSON)
```bash
python cli.py tf-step-ogata   --m 1 --b 3 --k 2 --x0 0.10 --v0 0.05   --tfinal 5 --dt 0.01   --save --json --analytic
```

### TF path — Generic G_ic(s) = num_ic/den
```bash
python cli.py tf-step   --num_ic "0.1 0.05 0"   --den "1 3 2"   --tfinal 5 --dt 0.01   --save --json
```

---

## 3) Artifacts and validation

- Plots: `transientAnalysis/icTool/out/*.png`
- JSON series: `transientAnalysis/icTool/out/*.json`

For **Ogata Ex. 5-8**, when poles are real and distinct, the plot can overlay the **analytic**
closed-form to validate the numeric curve.

Happy controls! ⚙️