# rootLocus.compensatorTool — Run Recipes

> Multi-lead lag–lead compensator designer (Ogata §6–8 style), with optional plotting.  
> CLI entry point: `python -m rootLocus.compensatorTool.cli`

## Setup & notes

- Run from the **project root** (the directory that contains the `rootLocus/` folder).
- If you run from elsewhere, make sure the project root is on `PYTHONPATH` or install the package.
- The help/banners include an en dash; ensure UTF-8:
  ```bash
  export PYTHONIOENCODING=utf-8 LANG=C.UTF-8 LC_ALL=C.UTF-8
  ```

---

## 0) Help / smoke

```bash
# Top-level CLI help
python -m root_locus_analysis.compensatorTool.cli --help

# Subcommand help
python -m root_locus_analysis.compensatorTool.cli design --help
```

---

## A) Ogata Example 6–8 style (G = 4 / [s (s+0.5)], ζ = 0.5, ωₙ = 5) — INDEPENDENT (γ ≠ β)

### A1. Lead via CANCEL (zero at −0.5), Kv target = 80, auto T2 with neutral lag

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "4" --den "0.5,1,0"   --zeta 0.5 --wn 5 --case indep   --lead-method cancel --cancel-at -0.5   --err kv --target 80
```

### A2. Same as A1 + plots (root locus + step)

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "4" --den "0.5,1,0"   --zeta 0.5 --wn 5 --case indep   --lead-method cancel --cancel-at -0.5   --err kv --target 80   --plot locus --plot step
```

### A3. Lead via BISECTOR (auto-repair if raw bisector invalid), Kv target = 80

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "4" --den "0.5,1,0"   --zeta 0.5 --wn 5 --case indep   --lead-method bisector   --err kv --target 80
```

### A4. Lead via MANUAL (T1, γ), Kv target = 80

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "4" --den "0.5,1,0"   --zeta 0.5 --wn 5 --case indep   --lead-method manual --T1 2 --gamma 10.04   --err kv --target 80
```

### A5. Lead via MANUAL (z, p), require p > z > 0 (here z = 0.5, p = 5.02)

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "4" --den "0.5,1,0"   --zeta 0.5 --wn 5 --case indep   --lead-method manual --lead-z 0.5 --lead-p 5.02   --err kv --target 80
```

### A6. Size β from IMPROVEMENT FACTOR instead of target (×16 on Kv)

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "4" --den "0.5,1,0"   --zeta 0.5 --wn 5 --case indep   --lead-method cancel --cancel-at -0.5   --err kv --factor 16
```

### A7. Fix β and T2 manually; print extra logs

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "4" --den "0.5,1,0"   --zeta 0.5 --wn 5 --case indep   --lead-method cancel --cancel-at -0.5   --beta 16.04 --T2 5 -v
```

### A8. Tight neutrality: |lag| ∈ [0.995, 1.005], |angle| ≤ 2°, cap T2

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "4" --den "0.5,1,0"   --zeta 0.5 --wn 5 --case indep   --lead-method bisector   --err kv --target 80   --thetamax 2 --magwin "0.995,1.005" --T2max 2000
```

---

## B) Ogata Example 6–9 style — COUPLED (γ = β); Kc set directly from Kv target

### B1. Coupled, bisector, Kv target = 80, auto T2

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "4" --den "0.5,1,0"   --zeta 0.5 --wn 5 --case coupled   --lead-method bisector   --err kv --target 80
```

### B3. Coupled + plots

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "4" --den "0.5,1,0"   --zeta 0.5 --wn 5 --case coupled   --lead-method bisector   --err kv --target 80   --plot locus --plot step
```

> **Note:** RC-mapping flags shown in some early notes (`--c1`, `--c2`, `--r5`, `--prefer-R`, etc.) are **not part of the current CLI** and have been omitted here.

---

## C) Different steady-state constants & direct pole entry

### C1. Improve Kp for a type-0 plant: G = 10 / [(s+1)(s+2)], desired s* = −1.8 ± j2.4

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "10" --den "1,3,2"   --sreal -1.8 --wimag 2.4   --case indep --lead-method bisector   --err kp --target 5
```

### C2. Improve Ka for a type-2 plant: G = 2 / [s^2 (s+1)], desired s* = −2 ± j3

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "2" --den "1,1,0,0"   --sreal -2 --wimag 3   --case indep --lead-method bisector   --nlead 4 --phi-per-lead 45   --err ka --target 2   --thetamax 2 --magwin "0.995,1.005" --T2max 2000
```

(Variant with a fixed `--T2` can be run similarly; just add `--T2 5`.)

---

## D) Alternate plant (G = 1 / [s (s+2) (s+5)]), specs ζ = 0.5, ωₙ = 3

### D1. Independent, bisector, Kv target = 2

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "1" --den "1,7,10,0"   --zeta 0.5 --wn 3 --case indep   --lead-method bisector   --err kv --target 2
```

### D2. Independent, manual lead via (T1, γ); size β from target; auto T2

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "1" --den "1,7,10,0"   --zeta 0.5 --wn 3 --case indep   --lead-method manual --T1 1 --gamma 4.08   --err kv --target 2
```

### D3. Coupled, bisector, Kv target = 2, with plots

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "1" --den "1,7,10,0"   --zeta 0.5 --wn 3 --case coupled   --lead-method bisector   --err kv --target 2   --plot locus --plot step
```

---

## E) Bisector auto-repair demo (naïve bisector would produce invalid z/p)

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "4" --den "0.5,1,0"   --zeta 0.5 --wn 5 --case indep   --lead-method bisector   --err kv --target 80 --T2max 2000 -v
```

---

## F) Tight lag neutrality regression (angle & magnitude window)

```bash
python -m root_locus_analysis.compensatorTool.cli design   --num "4" --den "0.5,1,0"   --zeta 0.5 --wn 5 --case indep   --lead-method cancel --cancel-at -0.5   --err kv --target 80   --thetamax 1 --magwin "0.997,1.003" --T2max 5000
```

---

## Lag-only subcommand (Ogata §6–7)

### Help

```bash
python -m root_locus_analysis.compensatorTool.cli lag --help
```

### Size β from target Kv

```bash
python -m root_locus_analysis.compensatorTool.cli lag   --num "1.06" --den "1,3,2,0"   --zeta 0.491 --wn 0.673   --err kv --target 5.12
```

### Size β from improvement factor (×3 on Kv)

```bash
python -m root_locus_analysis.compensatorTool.cli lag   --num "10" --den "1,1,0"   --zeta 0.5 --wn 3   --err kv --factor 3
```

### Fix β and pick T directly

```bash
python -m root_locus_analysis.compensatorTool.cli lag   --num "1.06" --den "1,3,2,0"   --zeta 0.491 --wn 0.673   --beta 10 --T 5
```

### Place z,p manually

```bash
python -m root_locus_analysis.compensatorTool.cli lag   --num "1.06" --den "1,3,2,0"   --zeta 0.491 --wn 0.673   --z 0.05 --p 0.005
```

### Provide s* directly

```bash
python -m root_locus_analysis.compensatorTool.cli lag   --num "1.06" --den "1,3,2,0"   --sreal -0.31 --wimag 0.55   --beta 10
```

---

## Lead-only subcommand (Ogata §6–6)

### Help
```bash
python -m root_locus_analysis.compensatorTool.cli lead --help
```

### Method 1 (bisector construction)

```bash
python -m root_locus_analysis.compensatorTool.cli lead   --num "10" --den "1,1,0"   --zeta 0.5 --wn 3   --method 1
```

### Method 2 (zero cancels a pole at −1)

```bash
python -m root_locus_analysis.compensatorTool.cli lead   --num "10" --den "1,1,0"   --zeta 0.5 --wn 3   --method 2 --cancel-at -1
```

---

### Tip for CI

Silence Matplotlib warnings during plotting:

```bash
export PYTHONWARNINGS=ignore
```

---

# Parallel compensator (series-equivalent locus) — Run Recipes

> Parallel compensation via series-equivalent root locus (Ogata §6-9).  
> CLI entry point: `python -m rootLocus.compensatorTool.cli parallel`

### Help

```bash
python -m root_locus_analysis.compensatorTool.cli parallel --help
```

### Notes

- To request multiple plots, **repeat** the `--plot` flag (Click requires one value per flag):
  - ✅ `--plot locus --plot step`
  - ❌ `--plot locus step`  _(this will error)_
- Axes overrides use the **pair form**: `--xlim -7 1 --ylim -14 14`.
- HTML exports are written under `rootLocus/compensatorTool/out/`.
- You can build \(F(s)\) three ways:
  1) from **blocks** (`--g1-*`, `--g2-*`, `--h-*`, `--gcb-*`),  
  2) from **characteristic split** \(A+K\cdot B\) (`--A-num`, `--B-num`) with optional `--step-num` for step overlays,  
  3) **directly** (`--F-num`, `--F-den`).

---

## A) ζ-scan at ζ = 0.4 (find intersections), locus + steps, export Plotly locus & steps

```bash
python -m root_locus_analysis.compensatorTool.cli parallel   --A-num "1,5,4,20" --B-num "1,0" --step-num "20"   --zeta 0.4 --scale 20   --plot locus --plot step --k-pts 800   --xlim -7 1 --ylim -14 14 --legend outside   --plotly-locus "rootLocus/compensatorTool/out/ogata_6_10_locus.html"   --plotly-step  "rootLocus/compensatorTool/out/ogata_6_10_steps.html"   --plotly-grid off --plotly-cross-axes
```

## B) Single design point P (s* = −1.0490 + j2.4065)

```bash
python -m root_locus_analysis.compensatorTool.cli parallel   --A-num "1,5,4,20" --B-num "1,0" --step-num "20"   --sreal -1.0490 --wimag 2.4065 --scale 20   --plot locus --plot step --k-pts 800   --xlim -7 1 --ylim -14 14 --legend outside   --plotly-step "rootLocus/compensatorTool/out/ogata_6_10_P_steps.html"   --plotly-grid off
```

## C) Single design point Q (s* = −2.1589 + j4.9652)

```bash
python -m root_locus_analysis.compensatorTool.cli parallel   --A-num "1,5,4,20" --B-num "1,0" --step-num "20"   --sreal -2.1589 --wimag 4.9652 --scale 20   --plot locus --plot step --k-pts 800   --xlim -7 1 --ylim -14 14 --legend outside   --plotly-step "rootLocus/compensatorTool/out/ogata_6_10_Q_steps.html"   --plotly-grid off
```

## D) ζ-scan via blocks (Gc_base = 1/[(s+1)(s+4)] → F = s/(s³+5s²+4s+20))

```bash
python -m root_locus_analysis.compensatorTool.cli parallel   --g1-num "20" --g1-den "1,5,4"   --g2-num "1"  --g2-den "1"   --h-num  "1"  --h-den  "1,0"   --gcb-num "1" --gcb-den "1,5,4"   --zeta 0.4 --scale 20   --plot locus --plot step --k-pts 800   --xlim -7 1 --ylim -14 14 --legend outside   --plotly-locus "rootLocus/compensatorTool/out/ogata_6_10_from_blocks.html"   --plotly-step  "rootLocus/compensatorTool/out/ogata_6_10_from_blocks_steps.html"   --plotly-grid off --plotly-cross-axes
```

## E) ζ-scan with direct F(s) (and A,B for step overlay)

```bash
python -m root_locus_analysis.compensatorTool.cli parallel   --F-num "1,0" --F-den "1,5,4,20"   --A-num "1,5,4,20" --B-num "1,0" --step-num "20"   --zeta 0.4 --scale 20   --plot locus --plot step --k-pts 800   --xlim -7 1 --ylim -14 14 --legend outside   --plotly-locus "rootLocus/compensatorTool/out/ogata_6_10_from_direct.html"   --plotly-step  "rootLocus/compensatorTool/out/ogata_6_10_from_direct_steps.html"   --plotly-grid off --plotly-cross-axes
```

## F) Single design point via ζ + ωₙ (instead of sreal/wimag)

```bash
python -m root_locus_analysis.compensatorTool.cli parallel   --A-num "1,5,4,20" --B-num "1,0" --step-num "20"   --zeta 0.4 --wn 3.0 --scale 20   --plot locus --plot step   --xlim -7 1 --ylim -14 14 --legend outside
```

## G) Locus only, with a custom K sweep range

```bash
python -m root_locus_analysis.compensatorTool.cli parallel   --F-num "1,0" --F-den "1,5,4,20"   --zeta 0.4   --plot locus --k-range "1e-3,1e3" --k-pts 600   --xlim -7 1 --ylim -14 14 --legend outside
```
