# System Response Tool — `rootLocus/systemResponseTool`

Clean, copy‑pasteable **run commands** for the object‑oriented package CLI.

These mirror the original standalone script examples but call:

```
python -m rootLocus.systemResponseTool.cli run ...
```

## Conventions

- **Inputs** (e.g., CSV for arbitrary inputs): `rootLocus/systemResponseTool/in/`
- **Outputs** (CSV + HTML): default to whatever you pass via `--out-prefix`.
  - If the prefix contains a path separator, it’s treated as a path relative to your current working directory and parent folders are created automatically.
  - Examples below write under: `rootLocus/systemResponseTool/out/…`
- **Logging flag:** use `--log-level` (values: `DEBUG`, `INFO`, `WARNING`, `ERROR`).
  - Legacy `--log LEVEL` is still accepted; the CLI rewrites it internally to `--log-level`.
- **Factorized polynomials** in `s` are supported (e.g., `(s+4.6458)*s*(s+1)`); quote them in zsh/bash.
- **Plot display:** When running under pytest, plots don’t auto‑open. In normal shells they will.

---

## A) Ogata Example 6‑6 — Unit **step** comparison (Fig. 6‑45)

> Closed‑loop TFs; keep `fb=none`.

```bash
python -m root_locus_analysis.systemResponseTool.cli run \
  --sys "tf; name=Uncomp;  num=10; den=1,1,10; fb=none; color=#1f77b4" \
  --sys "tf; name=Comp M1; num=12.287,23.876; den=1,5.646,16.933,23.876; fb=none; color=#2ca02c; dash=dot" \
  --sys "tf; name=Comp M2; num=9; den=1,3,9; fb=none; color=#d62728; dash=dash" \
  --responses step --tfinal 5 --dt 0.005 \
  --title "STEP response — Ogata Example 6-6 (Fig. 6-45)" \
  --out-prefix root_locus_analysis/systemResponseTool/out/ex6_6_step \
  --log-level INFO
```

---

## B) Ogata Example 6‑6 — Unit **ramp** comparison (Fig. 6‑46) with ramp overlay

```bash
python -m root_locus_analysis.systemResponseTool.cli run \
  --sys "tf; name=Comp M1; num=12.287,23.876; den=1,5.646,16.933,23.876; fb=none; color=#2ca02c; dash=dot" \
  --sys "tf; name=Comp M2; num=9; den=1,3,9; fb=none; color=#d62728; dash=dash" \
  --responses ramp --tfinal 5 --dt 0.005 --show-input \
  --title "RAMP response — Ogata Example 6-6 (Fig. 6-46)" \
  --out-prefix root_locus_analysis/systemResponseTool/out/ex6_6_ramp \
  --log-level INFO
```

---

## C) Same comparison but specify **open‑loop** (tool applies unity feedback)

> Using factor syntax (quote if your shell is zsh).

```bash
python -m root_locus_analysis.systemResponseTool.cli run \
  --sys "tf; name=G0(OL);      num=10;                  den=1,1,0" \
  --sys "tf; name=Lead-M1(OL); num=12.287*(s+1.9432);   den=(s+4.6458)*s*(s+1); color=#2ca02c; dash=dot" \
  --sys "tf; name=Lead-M2(OL); num=0.9*(s+1)*10;        den=(s+3)*s*(s+1);     color=#d62728; dash=dash" \
  --responses step,ramp --tfinal 5 --dt 0.005 --show-input \
  --title "Open-loop specified; unity feedback applied by tool" \
  --out-prefix root_locus_analysis/systemResponseTool/out/open_loop_demo \
  --log-level INFO
```

---

## D) **State‑space** plant (MIMO), pick channel (u₁→y₁), unity feedback default

```bash
python -m root_locus_analysis.systemResponseTool.cli run \
  --sys "ss; name=Plant; A=[-1,-1; 6.5,0]; B=[1,1; 1,0]; C=[1,0; 0,1]; D=[0,0; 0,0]; out=0; in=0; color=#9467bd" \
  --responses step,arb --arb-kind expr --arb-expr 'sin(2*pi*0.5*t)+0.3*sin(2*pi*2*t)' \
  --tfinal 10 --dt 0.01 \
  --title "SS channel y1 <- u1" \
  --out-prefix root_locus_analysis/systemResponseTool/out/ss_demo \
  --log-level INFO
```

---

## E) Arbitrary input from **expression** (with input overlay)

```bash
python -m root_locus_analysis.systemResponseTool.cli run \
  --sys "tf; name=PlantCL; num=10; den=1,1,10; fb=none" \
  --responses arb --arb-kind expr --arb-expr "sin(2*pi*0.5*t)+0.3*sin(2*pi*2*t)" \
  --tfinal 10 --dt 0.005 --show-input \
  --title "ARBITRARY response — u(t) from expression" \
  --out-prefix root_locus_analysis/systemResponseTool/out/expr_demo \
  --log-level INFO
```

---

## F) Arbitrary input from **CSV**

First, create the input CSV **in the package input folder**:

```bash
python - <<'PY'
import numpy as np, csv, pathlib
in_dir = pathlib.Path("rootLocus/systemResponseTool/in")
in_dir.mkdir(parents=True, exist_ok=True)
T = np.linspace(0,10,2001)
U = np.sin(2*np.pi*0.5*T) + 0.3*np.sin(2*np.pi*2*T)
with open(in_dir/"my_u.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["t","u"])
    for t,u in zip(T,U): w.writerow([t,u])
print("wrote", in_dir/"my_u.csv")
PY
```

Now run (passing just `my_u.csv` is fine — the app resolves it under `…/systemResponseTool/in`):

```bash
python -m root_locus_analysis.systemResponseTool.cli run \
  --sys "tf; name=PlantCL; num=10; den=1,1,10; fb=none" \
  --responses arb --arb-kind file --arb-file my_u.csv --show-input \
  --tfinal 10 --dt 0.005 \
  --title "ARBITRARY response — u(t) from file" \
  --out-prefix root_locus_analysis/systemResponseTool/out/file_demo \
  --log-level INFO
```

---

## G) Initial‑condition responses (Ogata §5‑5)

**Case 1** — states `x(t)` from `x(0)=x0` (direct vs step‑equivalent overlay by default)

```bash
python -m root_locus_analysis.systemResponseTool.cli run \
  --sys "ss; name=Plant; A=[0,1; -1,-1]; B=[0;1]; C=[1,0]; D=[0]; x0=[2; 1]" \
  --responses ic1 --tfinal 3 --dt 0.005 \
  --title "IC Case 1 — x(0)=[2,1]^T (direct vs step-equivalent)" \
  --out-prefix root_locus_analysis/systemResponseTool/out/ic_case1 \
  --log-level INFO
```

**Case 2** — outputs `y(t)=C x(t)` from `x(0)=x0` (select output rows; overlay step‑equiv)

```bash
python -m root_locus_analysis.systemResponseTool.cli run \
  --sys "ss; name=Plant; A=[0,1; -1,-1]; B=[0;1]; C=[1,0; 0,1]; D=[0,0; 0,0]; x0=[2; 1]; outs=all" \
  --responses ic2 --tfinal 3 --dt 0.005 \
  --title "IC Case 2 — y1 and y2 from x(0)=[2,1]^T" \
  --out-prefix root_locus_analysis/systemResponseTool/out/ic_case2 \
  --log-level INFO
```

> Want *direct‑only* (no step‑equivalent overlay)? Add `--no-ic-compare`.

Example (Case 1 direct‑only):

```bash
python -m root_locus_analysis.systemResponseTool.cli run \
  --sys "ss; name=Plant; A=[0,1; -1,-1]; B=[0;1]; C=[1,0]; D=[0]; x0=[2; 1]" \
  --responses ic1 --tfinal 3 --dt 0.005 --no-ic-compare \
  --title "IC Case 1 (direct only)" \
  --out-prefix root_locus_analysis/systemResponseTool/out/ic_case1_direct \
  --log-level INFO
```

---

## Notes & Tips

- `--out-prefix` can be **any** path. Parent folders are created as needed.
- For `--arb-kind file`, a relative filename like `my_u.csv` is resolved against `rootLocus/systemResponseTool/in/`.
- Add `--log-level DEBUG` for more diagnostics.
- The CLI prints step metrics to stdout for SISO TF cases.
- Tests disable plot popups; your normal shell will open figures as usual.
