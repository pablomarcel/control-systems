# Root‑Locus Tool — Verified Run Commands

These are copy‑pasteable (and runnable in many Markdown‑aware terminals/editors) recipes for the **rootLocusTool** CLI.

> **Assumptions**
> - Run all commands from the **modernControl/** repo root.
> - Update `--outdir` as you prefer; examples below use `rootLocus/rootLocusTool/out`.

---

## A) Ogata Fig. 6‑29(a): \(L_0(s)=\dfrac{s+2}{s^2+2s+3}\) + ζ‑line + constant‑gain contours

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --num "1,2" --den "1,2,3"   --zeta "0.7" --klabels "1.34,5.464"   --cg --kgains "1,2,6" --cg-res 221   --xlim -6 2 --ylim -4 8   --arrows --arrow-every 60 --arrow-scale 0.02   --title "Root–Locus: (s+2)/(s^2+2s+3) + constant-gain contours"   --html ex6_2_cg.html --outdir root_locus_analysis/rootLocusTool/out
```
*Tip:* hover the dashed contours: hover shows `|L0|` and dynamic `K≈…`; RL traces still show `K` from the locus.

---

## B) Ogata Fig. 6‑29(b): \(L_0(s)=\dfrac{1}{s(s+1)(s+2)}\) + const‑gain

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --num "1" --den "1,3,2,0"   --zeta "0.5" --klabels "1.0383,6"   --cg --kgains "1,3,6" --cg-res 201   --xlim -7 3 --ylim -4 4   --title "Root–Locus: 1/[s(s+1)(s+2)] + const-gain"   --html ex6_1_cg.html --outdir root_locus_analysis/rootLocusTool/out
```

---

## C) Absolute \(|L_0|\) contours (instead of K‑levels)

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --num "1,2" --den "1,2,3"   --cg --cg-absL "0.5,1,2" --cg-res 181   --xlim -6 2 --ylim -4 8   --title "Root–Locus + |L0| contours"   --html ex6_2_absL.html --outdir root_locus_analysis/rootLocusTool/out
```

---

## D) Series \(G(s)H(s)\) + ζ‑line + const‑gain

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --Gnum "10" --Gden "1,1,0"   --Hnum "1,5" --Hden "1,50"   --cg --kgains "0.3,1,10" --cg-res 181   --zeta "0.6"   --xlim -55 5 --ylim -15 15   --title "Root–Locus: G(s)H(s) with constant-gain contours"   --html gh_cg.html --outdir root_locus_analysis/rootLocusTool/out
```

---

## E) State‑space input

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --ssA "0,1,0;0,0,1;-160,-56,-14"   --ssB "0;1;-14"   --ssC "1,0,0"   --ssD "0"   --cg --kgains "0.5,1,2" --zeta "0.5,0.707"   --xlim -20 20 --ylim -20 20   --title "State-space example + const-gain"   --html ss_cg.html --outdir root_locus_analysis/rootLocusTool/out
```

---

## Quick sanity‑run set

### 1) Example 6‑2, arrows + hoverable ζ=0.7 + labels

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --num "1,2" --den "1,2,3"   --zeta "0.7" --wn "none"   --klabels "1.34,5.464"   --arrows --arrow-every 60 --arrow-scale 0.02   --xlim -6 2 --ylim -4 8   --title "Root–Locus: (s+2)/(s^2+2s+3)"   --html ex6_2_pro.html --outdir root_locus_analysis/rootLocusTool/out
```

### 2) MATLAB‑style s‑grid overlay (hover shows ζ/ωₙ; prints labels)

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --num "0,0,0,1" --den "1,4,5,0"   --sgrid   --xlim -3 3 --ylim -3 3   --title "S-grid overlay"   --html sgrid_pro.html --outdir root_locus_analysis/rootLocusTool/out
```

### 3) State‑space (Ogata Ex. 6‑5 style), SISO

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --ssA "0 1 0; 0 0 1; -160 -56 -14"   --ssB "0; 1; -14"   --ssC "1 0 0"   --ssD "0"   --sgrid --zeta "0.5,0.707" --wn "0.5,1,2"   --arrows   --xlim -20 20 --ylim -20 20   --title "Root–Locus from state-space (A,B,C,D)"   --html ss_pro.html --outdir root_locus_analysis/rootLocusTool/out
```
> MIMO? Pick channel: `--io 0 1` (row=0, col=1; 0‑indexed).

### 4) Only ωₙ circles (no ζ) + no labels

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --num "1" --den "1,3,2,0"   --zeta none --wn "0.5,1,2,3"   --no-wn-labels   --xlim -6 2 --ylim -6 6   --title "Only ωₙ circles"   --html wn_only.html --outdir root_locus_analysis/rootLocusTool/out
```

---

## Ogata Example 6‑6 set

### Method 1 style (as in the standalone notes)

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --num "12.287,23.876" --den "1,5.646,16.933,23.876"   --zeta "0.5" --wn "3"   --klabels "1.34,5.464"   --arrows --arrow-every 60 --arrow-scale 0.02   --xlim -6 2 --ylim -4 8   --title "Root–Locus: (12.287s+23.876)/(s^3+5.646s^2+16.933s+23.876)"   --html ex6_6_adv_pro_b.html --outdir root_locus_analysis/rootLocusTool/out
```

### Plant \(10/(s^2+s)\), ζ=0.5, ωₙ=3

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --num "0,0,10" --den "1,1,0"   --zeta "0.5" --wn "3"   --klabels "1.34,5.464"   --arrows --arrow-every 60 --arrow-scale 0.02   --xlim -6 2 --ylim -4 8   --title "Root–Locus: (10)/(s^2+s)"   --html ex6_6_adv_pro_b.html --outdir root_locus_analysis/rootLocusTool/out
```

### Compensated \(L_0\) (fixed gain inside)

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --num "12.287,23.8760984"   --den "1,5.6458,4.6458,0"   --title "Root–Locus: compensated L0(s)"   --sgrid --zeta "0.5,0.7" --wn "1,2"   --klabels "1"   --html comp_in.html --outdir root_locus_analysis/rootLocusTool/out
```

### Compensated with gain factored **out** (script’s \(K\) = fixed gain)

```bash
python -m root_locus_analysis.rootLocusTool.cli run   --num "1,1.9432"   --den "1,5.6458,4.6458,0"   --klabels "12.287"   --title "Root–Locus: compensated (gain factored out)"   --sgrid   --html comp_out.html --outdir root_locus_analysis/rootLocusTool/out
```

---

## Batch mode

### Minimal YAML (example)

```yaml
# root_locus_analysis/rootLocusTool/in/cases.yaml
- title: Example 6-1
  num: "1"
  den: "1,3,2,0"
  zeta: "0.5"
  klabels: "1.0383,6"
  html: "ex6_1.html"
  csv:  "ex6_1.csv"

- title: p3 z1
  poles: "0,-2,-4"
  zeros: "-1"
  kgain: 1
  wn: "1,2"
  zeta: "0.5,0.7"
  html: "p3z1.html"
```

### Run it

```bash
python -m root_locus_analysis.rootLocusTool.cli batch   --batch root_locus_analysis/rootLocusTool/in/cases.yaml   --outdir root_locus_analysis/rootLocusTool/out   --report root_locus_report.html
```

---

## Extra power‑user switches

### Include **negative** \(K\) sweep
```bash
... --kneg "0.1,100"
```

### Custom \(K\ge 0\) grid (linear or log)
```bash
# linear 0..50 with 200 samples
... --kpos "0,50,200,lin"

# log from ~1e-6 up to 100 with 500 samples
... --kpos "1e-6,100,500,log"
```

### Export PNG and CSV alongside HTML
```bash
... --png "figure.png" --csv "roots.csv" --outdir root_locus_analysis/rootLocusTool/out
```

### Turn off ζ/ωₙ labels only
```bash
... --no-zeta-labels --no-wn-labels
```
