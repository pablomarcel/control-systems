# RUNS.md — systemResponseTool (run from inside this folder)

> **How to use this file**
>
> 1. `cd rootLocus/systemResponseTool`
> 2. Run any block **as-is** (they all use `python cli.py run …`).
> 3. Results go to the local `out/` folder (created automatically). For CSV inputs, place files in `in/`.

The CLI also supports running as a module from the repo root:
```bash
python -m rootLocus.systemResponseTool.cli run …
```
But all the commands below are designed to run **from this folder** with:
```bash
python cli.py run …
```

---

## A) Ogata Example 6-6 — Unit **step** comparison (Fig. 6-45)

> Closed-loop TFs; keep `fb=none`.

```bash
python cli.py run   --sys "tf; name=Uncomp;  num=10; den=1,1,10; fb=none; color=#1f77b4"   --sys "tf; name=Comp M1; num=12.287,23.876; den=1,5.646,16.933,23.876; fb=none; color=#2ca02c; dash=dot"   --sys "tf; name=Comp M2; num=9; den=1,3,9; fb=none; color=#d62728; dash=dash"   --responses step --tfinal 5 --dt 0.005   --title "STEP response — Ogata Example 6-6 (Fig. 6-45)"   --out-prefix out/ex6_6_step   --log-level INFO
```

---

## B) Ogata Example 6-6 — Unit **ramp** comparison (Fig. 6-46) with ramp overlay

```bash
python cli.py run   --sys "tf; name=Comp M1; num=12.287,23.876; den=1,5.646,16.933,23.876; fb=none; color=#2ca02c; dash=dot"   --sys "tf; name=Comp M2; num=9; den=1,3,9; fb=none; color=#d62728; dash=dash"   --responses ramp --tfinal 5 --dt 0.005 --show-input   --title "RAMP response — Ogata Example 6-6 (Fig. 6-46)"   --out-prefix out/ex6_6_ramp   --log-level INFO
```

---

## C) Open-loop specified; unity feedback applied by tool

> Using factor syntax (quote in zsh/bash). These specify **open-loop** transfer functions; the tool applies unity feedback.

```bash
python cli.py run   --sys "tf; name=G0(OL);      num=10;                  den=1,1,0"   --sys "tf; name=Lead-M1(OL); num=12.287*(s+1.9432);   den=(s+4.6458)*s*(s+1); color=#2ca02c; dash=dot"   --sys "tf; name=Lead-M2(OL); num=0.9*(s+1)*10;        den=(s+3)*s*(s+1);     color=#d62728; dash=dash"   --responses step,ramp --tfinal 5 --dt 0.005 --show-input   --title "Open-loop specified; unity feedback applied by tool"   --out-prefix out/open_loop_demo   --log-level INFO
```

---

## D) **State-space** plant (MIMO), pick channel (u₁→y₁); unity feedback

```bash
python cli.py run   --sys "ss; name=Plant; A=[-1,-1; 6.5,0]; B=[1,1; 1,0]; C=[1,0; 0,1]; D=[0,0; 0,0]; out=0; in=0; color=#9467bd"   --responses step,arb --arb-kind expr --arb-expr 'sin(2*pi*0.5*t)+0.3*sin(2*pi*2*t)'   --tfinal 10 --dt 0.01   --title "SS channel y1 <- u1"   --out-prefix out/ss_demo   --log-level INFO
```

---

## E) Arbitrary input from **expression** (with input overlay)

```bash
python cli.py run   --sys "tf; name=PlantCL; num=10; den=1,1,10; fb=none"   --responses arb --arb-kind expr --arb-expr "sin(2*pi*0.5*t)+0.3*sin(2*pi*2*t)"   --tfinal 10 --dt 0.005 --show-input   --title "ARBITRARY response — u(t) from expression"   --out-prefix out/expr_demo   --log-level INFO
```

---

## F) Arbitrary input from **CSV**

First, create the input CSV **in the local `in/` folder**:

```bash
python - <<'PY'
import numpy as np, csv, pathlib
in_dir = pathlib.Path("in")
in_dir.mkdir(parents=True, exist_ok=True)
T = np.linspace(0,10,2001)
U = np.sin(2*np.pi*0.5*T) + 0.3*np.sin(2*np.pi*2*T)
with open(in_dir/"my_u.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["t","u"])
    for t,u in zip(T,U): w.writerow([t,u])
print("wrote", in_dir/"my_u.csv")
PY
```

Now run (passing just `my_u.csv` is fine — the app resolves it under `in/` automatically):

```bash
python cli.py run   --sys "tf; name=PlantCL; num=10; den=1,1,10; fb=none"   --responses arb --arb-kind file --arb-file my_u.csv --show-input   --tfinal 10 --dt 0.005   --title "ARBITRARY response — u(t) from file"   --out-prefix out/file_demo   --log-level INFO
```

---

## G) Initial-condition responses (Ogata §5-5)

**Case 1** — states `x(t)` from `x(0)=x0` (direct vs step-equiv overlay by default)

```bash
python cli.py run   --sys "ss; name=Plant; A=[0,1; -1,-1]; B=[0;1]; C=[1,0]; D=[0]; x0=[2; 1]"   --responses ic1 --tfinal 3 --dt 0.005   --title "IC Case 1 — x(0)=[2,1]^T (direct vs step-equivalent)"   --out-prefix out/ic_case1   --log-level INFO
```

**Case 1 (direct only)** — disable step-equivalent overlay:

```bash
python cli.py run   --sys "ss; name=Plant; A=[0,1; -1,-1]; B=[0;1]; C=[1,0]; D=[0]; x0=[2; 1]"   --responses ic1 --tfinal 3 --dt 0.005 --no-ic-compare   --title "IC Case 1 (direct only)"   --out-prefix out/ic_case1_direct   --log-level INFO
```

**Case 2** — outputs `y(t)=C x(t)` from `x(0)=x0` (select output rows; overlay step-equiv)

```bash
python cli.py run   --sys "ss; name=Plant; A=[0,1; -1,-1]; B=[0;1]; C=[1,0; 0,1]; D=[0,0; 0,0]; x0=[2; 1]; outs=all"   --responses ic2 --tfinal 3 --dt 0.005   --title "IC Case 2 — y1 and y2 from x(0)=[2,1]^T"   --out-prefix out/ic_case2   --log-level INFO
```

---

## Notes & tips

* `--out-prefix` can be any path. If it contains a separator, we treat it as a full/relative path and **create parent folders** as needed. All examples here write to `out/…`.
* For `--arb-kind file`, passing a relative filename like `my_u.csv` will be resolved against the local `in/` folder, which is created automatically.
* Factorized polynomials in `s` (e.g., `(s+4.6)*s*(s+1)`) are supported; quote them in your shell.
* Use `--log-level DEBUG` for extra diagnostics.
