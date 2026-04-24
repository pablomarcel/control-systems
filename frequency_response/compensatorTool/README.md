# frequencyResponse / compensatorTool — Runbook

This markdown collects **ready-to-run CLI invocations** for the OOP tool:

```
python -m frequencyResponse.compensatorTool.cli
```

- **Artifacts** are written to: `frequencyResponse/compensatorTool/out/`
- If you later add **input files**, put them under: `frequencyResponse/compensatorTool/in/` and point flags there.
- Flexible list flags (`--nyquist_M`, `--nyquist_marks`, `--nichols_Mdb`, `--nichols_Ndeg`) accept **space-** or **comma-separated** values.
- **Matplotlib** windows pop unless you pass `--no_show`. All MPL examples here also **save** to disk.
- Static PNG export for Plotly requires **kaleido** (you have it).

> **Modes**
>
> - Default mode is **laglead** (backward compatible with existing commands).
> - Lead-only runs use the same entrypoint with `--mode lead`.
> - Pattern stays consistent as you scale:  
>   `python -m frequencyResponse.compensatorTool.cli --mode <laglead|lead> <flags...>`

---

## Lag–Lead (default) Runbook

### 1) Nichols (Plotly) with custom M = 0.9 dB contour
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend plotly --plots nichols --nichols_templates \
  --nichols_Mdb -12 -9 -6 -3 0 0.9 3 6 9 12 \
  --nichols_Ndeg -30 -60 -90 -120 -150 -180 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html"
```

### 2) Nichols (Matplotlib) with the same custom contours
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend mpl --plots nichols --nichols_templates \
  --nichols_Mdb -12 -9 -6 -3 0 0.9 3 6 9 12 \
  --nichols_Ndeg -30 -60 -90 -120 -150 -180 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png"
```

### 3) Nyquist (Plotly) with multiple M-circles + ω marks
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend plotly --plots nyquist --ogata_axes \
  --nyquist_M 1.2 1.05 0.9 \
  --nyquist_marks 0.2 0.4 1 2 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html"
```

### 4) Nyquist (Matplotlib) with multiple M-circles + ω marks
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend mpl --plots nyquist --ogata_axes \
  --nyquist_M 1.2 1.05 0.9 \
  --nyquist_marks 0.2 0.4 1 2 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png"
```

### 5) Bode + Nyquist + Nichols (Plotly), custom grids, saved HTML
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend plotly --ogata_axes \
  --plots bode,nyquist,nichols \
  --nichols_templates \
  --nichols_Mdb -12 -9 -6 -3 0 0.9 3 6 9 12 \
  --nyquist_M 1.2 1.05 0.9 \
  --nyquist_marks 0.2 0.4 1 2 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html"
```

### 6) Default multi-plot (Matplotlib)
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend mpl \
  --plots bode,nyquist,nichols,step,ramp \
  --ogata_axes \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png"
```

### 7) Default multi-plot (Plotly) + HTML export
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend plotly \
  --plots bode,nyquist,nichols,step,ramp \
  --ogata_axes \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html"
```

### 8) Plotly + static PNGs (needs kaleido installed)
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend plotly --plots nyquist,nichols \
  --ogata_axes \
  --nyquist_M 1.2 --nyquist_marks 0.2 0.4 1 2 \
  --nichols_templates --nichols_Mdb -12 -6 0 3 6 9 12 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html" \
  --save_img "frequencyResponse/compensatorTool/out/og728_{kind}.png" \
  --no_show
```

### 9) Nichols (Plotly) – minimal extra contours (just Mdb=0.9)
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend plotly --plots nichols --nichols_templates \
  --nichols_Mdb 0.9 \
  --nichols_Ndeg -60 -120 -180 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html"
```

### 10) Nyquist with only the Ogata M=1.2 circle (both backends)
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend plotly --plots nyquist --ogata_axes \
  --nyquist_M 1.2 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html"
```
> For Matplotlib, swap `--backend mpl` and save as PNG.

### 11) Time-domain only (Step & Ramp), hide unstable baseline if any
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend mpl --plots step,ramp --ogata_axes \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png"
```

### 12) Custom frequency grid
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend mpl --plots bode,nyquist,nichols \
  --nichols_templates \
  --nichols_Mdb -12 -9 -6 -3 0 3 6 9 12 \
  --export_csv_prefix "frequencyResponse/compensatorTool/out/og728" \
  --export_json "frequencyResponse/compensatorTool/out/og728_design.json" \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png" \
  --no_show
```

### 13) CSV + JSON exports (good for reports/CI)
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend mpl --plots bode,nyquist,nichols \
  --nichols_templates \
  --nichols_Mdb -12 -9 -6 -3 0 3 6 9 12 \
  --export_csv_prefix "frequencyResponse/compensatorTool/out/og728" \
  --export_json "frequencyResponse/compensatorTool/out/og728_design.json" \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png" \
  --no_show
```

### 14) From a custom plant (TF string) with auto design
```bash
python -m frequency_response.compensatorTool.cli \
  --tf "K/(s*(s+1)*(s+2))" --params "K=8" \
  --Kv 10 --pm_target 50 \
  --backend plotly --plots nichols,nyquist --ogata_axes \
  --nichols_templates --nyquist_M 1.2 \
  --save "frequencyResponse/compensatorTool/out/custom_{kind}.html"
```

### 15) From ZPK form
```bash
python -m frequency_response.compensatorTool.cli \
  --z "" --p "0, -1, -2" --k "K" --params "K=20" \
  --backend mpl --plots bode,nyquist,nichols \
  --save "frequencyResponse/compensatorTool/out/zpk_{kind}.png"
```

### 16) From State-Space matrices
```bash
python -m frequency_response.compensatorTool.cli \
  --A "0,1,0;0,0,1;0,-3,-2" \
  --B "0;0;1" \
  --C "1,0,0" \
  --D "0" \
  --backend mpl --plots bode,nyquist,nichols \
  --save "frequencyResponse/compensatorTool/out/ss_{kind}.png"
```

### 17) Force-show unstable baseline in time responses (for comparison)
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend mpl --plots step,ramp \
  --ogata_axes --show_unstable \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png"
```

### 18) Headless batch render (CI-friendly)
```bash
python -m frequency_response.compensatorTool.cli --ogata_7_28 \
  --backend plotly --plots bode,nyquist,nichols \
  --ogata_axes \
  --nichols_templates --nyquist_M 1.2 \
  --save "frequencyResponse/compensatorTool/out/batch_{kind}.html" \
  --no_show
```

---

## Lead-only Runbook (`--mode lead`)

### 0) help
```bash
python -m frequency_response.compensatorTool.cli --mode lead --help
```

### 1) minimal auto design (MPL, Bode only, no windows; saves PNG)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --num 4 --den "1, 2, 0" \
  --lead_pm_target 50 --lead_pm_add 5 --lead_stages 1 \
  --backend mpl --plots bode --no_show \
  --save "frequencyResponse/compensatorTool/out/lead_min_{kind}.png"
```

### 2) minimal auto design (Plotly HTML)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --num 4 --den "1, 2, 0" \
  --lead_pm_target 50 --lead_pm_add 5 --lead_stages 1 \
  --backend plotly --plots bode --no_show \
  --save "frequencyResponse/compensatorTool/out/lead_min_{kind}.html"
```

### 3) Kv scaling + full plot set + JSON/CSV (MPL, headless)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --num 4 --den "1, 2, 0" --Kv 20 \
  --lead_pm_target 50 --lead_pm_add 5 --lead_stages 1 \
  --backend mpl --plots bode,nyquist,nichols,step,ramp --no_show \
  --export_json "frequencyResponse/compensatorTool/out/lead_kv.json" \
  --export_csv_prefix "frequencyResponse/compensatorTool/out/lead_kv" \
  --save "frequencyResponse/compensatorTool/out/lead_kv_{kind}.png"
```

### 4) two-stage auto design (MPL, Bode+Nichols)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --num 4 --den "1, 2, 0" --Kv 20 \
  --lead_pm_target 50 --lead_pm_add 5 --lead_stages 2 \
  --backend mpl --plots bode,nichols --no_show \
  --save "frequencyResponse/compensatorTool/out/lead_2stage_{kind}.png"
```

### 5) two-stage with asymmetric φ split (60/40)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --num 4 --den "1, 2, 0" --Kv 20 \
  --lead_pm_target 50 --lead_pm_add 5 --lead_stages 2 --lead_phi_split "60,40" \
  --backend mpl --plots bode,nichols --no_show \
  --save "frequencyResponse/compensatorTool/out/lead_split_{kind}.png"
```

### 6) manual single-stage lead (α, T, optional Kc) — no auto design
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --num 4 --den "1, 2, 0" \
  --lead_alpha 0.25 --lead_T 0.15 --lead_Kc 3.2 \
  --backend mpl --plots bode,nyquist,step --no_show \
  --save "frequencyResponse/compensatorTool/out/lead_manual_{kind}.png"
```

### 7) TF via expressions + params (Plotly)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --num K --den "(T1*T2), (T1+T2), 1" --params "K=8,T1=0.2,T2=0.5" \
  --lead_pm_target 55 --lead_pm_add 5 --lead_stages 1 \
  --backend plotly --plots bode,nichols --no_show \
  --save "frequencyResponse/compensatorTool/out/lead_expr_{kind}.html"
```

### 8) ZPK input (auto design)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --z "" --p "-1, -2" --k 5 \
  --lead_pm_target 50 --lead_pm_add 5 --lead_stages 1 \
  --backend mpl --plots bode,nyquist --no_show \
  --save "frequencyResponse/compensatorTool/out/lead_zpk_{kind}.png"
```

### 9) state-space input (auto design, step focus)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --A "0,1; -4,-2" --B "0; 4" --C "1,0" --D "0" \
  --lead_pm_target 60 --lead_pm_add 5 --lead_stages 1 \
  --backend mpl --plots bode,step --no_show \
  --save "frequencyResponse/compensatorTool/out/lead_ss_{kind}.png"
```

### 10) Nichols with default template grid (MPL)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --num 4 --den "1, 2, 0" \
  --lead_pm_target 50 --lead_pm_add 5 --lead_stages 1 \
  --backend mpl --plots nichols --nichols_templates --no_show \
  --save "frequencyResponse/compensatorTool/out/lead_nichols_{kind}.png"
```

### 11) Nichols with explicit contours (MPL)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --num 4 --den "1, 2, 0" \
  --lead_pm_target 50 --lead_pm_add 5 --lead_stages 1 \
  --backend mpl --plots nichols --no_show \
  --nichols_Mdb -12 -9 -6 -3 0 3 6 9 12 \
  --nichols_Ndeg -30 -60 -90 -120 -150 -180 \
  --save "frequencyResponse/compensatorTool/out/lead_nichols_custom_{kind}.png"
```

### 12) Nyquist with M-circles and ω marks (MPL)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --num 4 --den "1, 2, 0" \
  --lead_pm_target 50 --lead_pm_add 5 --lead_stages 1 \
  --backend mpl --plots nyquist --no_show \
  --nyquist_M 1.2 1.05 0.9 \
  --nyquist_marks 0.2 0.4 1 2 5 \
  --save "frequencyResponse/compensatorTool/out/lead_nyq_{kind}.png"
```

### 13) time-domain only (force-show unstable baseline if you want it visible)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --tf "1/(s*(s+1)*(s+2))" \
  --lead_pm_target 40 --lead_pm_add 5 --lead_stages 1 \
  --backend mpl --plots step,ramp --no_show --show_unstable \
  --save "frequencyResponse/compensatorTool/out/lead_time_{kind}.png"
```

### 14) Plotly full set + HTML/PNG + exports (headless)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --num 4 --den "1, 2, 0" --Kv 20 \
  --lead_pm_target 50 --lead_pm_add 5 --lead_stages 1 \
  --backend plotly --plots bode,nyquist,nichols --no_show \
  --save "frequencyResponse/compensatorTool/out/lead_full_{kind}.html" \
  --save_img "frequencyResponse/compensatorTool/out/lead_full_{kind}.png" \
  --export_json "frequencyResponse/compensatorTool/out/lead_full.json" \
  --export_csv_prefix "frequencyResponse/compensatorTool/out/lead_full"
```

### 15) custom frequency grid (dense sweep)
```bash
python -m frequency_response.compensatorTool.cli --mode lead \
  --num 4 --den "1, 2, 0" \
  --lead_pm_target 50 --lead_pm_add 5 --lead_stages 1 \
  --backend mpl --plots bode --no_show \
  --wmin 1e-1 --wmax 1e4 --wnum 5000 \
  --save "frequencyResponse/compensatorTool/out/lead_grid_{kind}.png"
```

---

## Lag-only Runbook (`--mode lag`)

## 0) Help

```bash
python -m frequency_response.compensatorTool.cli --mode lag --help
```

## 1) Minimal auto design (MPL, Bode only)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --num 4 --den "1, 2, 0" \
  --lag_pm_target 45 --lag_pm_add 8 \
  --backend mpl --plots bode --no_show \
  --save "frequencyResponse/compensatorTool/out/lag_min_{kind}.png"
```

## 2) Minimal auto design (Plotly HTML)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --num 4 --den "1, 2, 0" \
  --lag_pm_target 45 --lag_pm_add 8 \
  --backend plotly --plots bode --no_show \
  --save "frequencyResponse/compensatorTool/out/lag_min_{kind}.html"
```

## 3) Kv scaling + full plot set + JSON/CSV (MPL, headless)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --num 4 --den "1, 2, 0" --Kv 20 \
  --lag_pm_target 45 --lag_pm_add 8 \
  --backend mpl --plots bode,nyquist,nichols,step,ramp --no_show \
  --export_json "frequencyResponse/compensatorTool/out/lag_kv.json" \
  --export_csv_prefix "frequencyResponse/compensatorTool/out/lag_kv" \
  --save "frequencyResponse/compensatorTool/out/lag_kv_{kind}.png"
```

## 4) Lag auto design tuned like Ogata Ex 7-27 (use tighter zero spacing)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --tf "1/(s*(s+1)*(0.5*s+1))" --Kv 5 \
  --lag_pm_target 40 --lag_pm_add 12 --lag_w_ratio 5 \
  --backend mpl --plots bode,nyquist,nichols,step,ramp --no_show \
  --save "frequencyResponse/compensatorTool/out/lag_og727_{kind}.png"
```

## 5) Manual lag (β, T, optional Kc) — no auto design

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --tf "1/(s*(s+1)*(0.5*s+1))" --Kv 5 \
  --lag_beta 10 --lag_T 10 --lag_Kc 0.5 \
  --backend mpl --plots bode,nyquist,step --no_show \
  --save "frequencyResponse/compensatorTool/out/lag_manual_{kind}.png"
```

## 6) TF via expressions + params (Plotly)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --tf "K/(s*(s+1)*(T*s+1))" --params "K=1.0,T=0.5" \
  --lag_pm_target 45 --lag_pm_add 8 \
  --backend plotly --plots bode,nichols --no_show \
  --save "frequencyResponse/compensatorTool/out/lag_expr_{kind}.html"
```

## 7) ZPK input (auto design)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --z "" --p "0, -1, -2" --k 1 \
  --lag_pm_target 45 --lag_pm_add 8 \
  --backend mpl --plots bode,nyquist --no_show \
  --save "frequencyResponse/compensatorTool/out/lag_zpk_{kind}.png"
```

## 8) State-space input (auto design, step focus)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --A "0,1; -4,-2" --B "0; 4" --C "1,0" --D "0" \
  --lag_pm_target 45 --lag_pm_add 8 \
  --backend mpl --plots bode,step --no_show \
  --save "frequencyResponse/compensatorTool/out/lag_ss_{kind}.png"
```

## 9) Nichols with default template grid (MPL)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --num 4 --den "1, 2, 0" \
  --lag_pm_target 45 --lag_pm_add 8 \
  --backend mpl --plots nichols --nichols_templates --no_show \
  --save "frequencyResponse/compensatorTool/out/lag_nichols_{kind}.png"
```

## 10) Nichols with explicit contours (MPL)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --num 4 --den "1, 2, 0" \
  --lag_pm_target 45 --lag_pm_add 8 \
  --backend mpl --plots nichols --no_show \
  --nichols_Mdb -12 -9 -6 -3 0 3 6 9 12 \
  --nichols_Ndeg -30 -60 -90 -120 -150 -180 \
  --save "frequencyResponse/compensatorTool/out/lag_nichols_custom_{kind}.png"
```

## 11) Nyquist with M-circles and ω marks (MPL)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --num 4 --den "1, 2, 0" \
  --lag_pm_target 45 --lag_pm_add 8 \
  --backend mpl --plots nyquist --no_show \
  --nyquist_M 1.2 1.05 0.9 \
  --nyquist_marks 0.2 0.4 1 2 5 \
  --save "frequencyResponse/compensatorTool/out/lag_nyq_{kind}.png"
```

## 12) Time-domain only (force-show unstable baseline if desired)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --tf "1/(s*(s+1)*(0.5*s+1))" --Kv 5 \
  --lag_pm_target 40 --lag_pm_add 12 --lag_w_ratio 5 \
  --backend mpl --plots step,ramp --no_show --show_unstable \
  --save "frequencyResponse/compensatorTool/out/lag_time_{kind}.png"
```

## 13) Plotly full set + HTML/PNG + exports (headless)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --num 4 --den "1, 2, 0" --Kv 20 \
  --lag_pm_target 45 --lag_pm_add 8 \
  --backend plotly --plots bode,nyquist,nichols --no_show \
  --save "frequencyResponse/compensatorTool/out/lag_full_{kind}.html" \
  --save_img "frequencyResponse/compensatorTool/out/lag_full_{kind}.png" \
  --export_json "frequencyResponse/compensatorTool/out/lag_full.json" \
  --export_csv_prefix "frequencyResponse/compensatorTool/out/lag_full"
```

## 14) Custom frequency grid (dense sweep)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --num 4 --den "1, 2, 0" \
  --lag_pm_target 45 --lag_pm_add 8 \
  --backend mpl --plots bode --no_show \
  --wmin 1e-1 --wmax 1e4 --wnum 5000 \
  --save "frequencyResponse/compensatorTool/out/lag_grid_{kind}.png"
```

## 15) Headless batch render (CI-friendly, Nichols + Nyquist overlays)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --num 4 --den "1, 2, 0" \
  --lag_pm_target 45 --lag_pm_add 8 \
  --backend plotly --plots bode,nyquist,nichols --no_show \
  --nichols_templates --nyquist_M 1.2 \
  --save "frequencyResponse/compensatorTool/out/lag_batch_{kind}.html"
```

## 16) Ogata-style axes on time plots (compare shapes)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --tf "1/(s*(s+1)*(0.5*s+1))" --Kv 5 \
  --lag_pm_target 40 --lag_pm_add 12 --lag_w_ratio 5 \
  --backend mpl --plots step,ramp --no_show \
  --ogata_axes \
  --save "frequencyResponse/compensatorTool/out/lag_og_axes_{kind}.png"
```

## 17) Nichols + closed-loop performance annotations (Plotly)

```bash
python -m frequency_response.compensatorTool.cli --mode lag \
  --tf "1/(s*(s+1)*(0.5*s+1))" --Kv 5 \
  --lag_pm_target 40 --lag_pm_add 12 --lag_w_ratio 5 \
  --backend plotly --plots nichols --no_show --nichols_templates \
  --save "frequencyResponse/compensatorTool/out/lag_nichols_cl_{kind}.html"
```



### Notes
- If you need to **read** config/plant files later, place them under `frequencyResponse/compensatorTool/in/` and point the corresponding flags to that path.
- If running in a headless CI environment for Matplotlib, add `--no_show` and rely on saved files under `out/`.
