# frequencyResponse / compensatorTool — Runbook

This markdown collects **ready-to-run CLI invocations** for the OOP tool:
`python -m frequencyResponse.compensatorTool.cli`

- **Artifacts** are written to: `frequencyResponse/compensatorTool/out/`
- If you later add **input files**, put them under: `frequencyResponse/compensatorTool/in/` and point flags there.
- Flexible list flags (`--nyquist_M`, `--nyquist_marks`, `--nichols_Mdb`, `--nichols_Ndeg`) accept **space-** or **comma-separated** values.
- **Matplotlib** windows pop unless you pass `--no_show`. All MPL examples here also **save** to disk.
- Static PNG export for Plotly requires **kaleido** (you have it).

> Tip (VS Code / Preview tools): many Markdown extensions let you run shell blocks inline. Otherwise, copy a block and paste into your terminal.

---

## 1) Nichols (Plotly) with custom M = 0.9 dB contour
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend plotly --plots nichols --nichols_templates \
  --nichols_Mdb -12 -9 -6 -3 0 0.9 3 6 9 12 \
  --nichols_Ndeg -30 -60 -90 -120 -150 -180 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html"
```

## 2) Nichols (Matplotlib) with the same custom contours
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend mpl --plots nichols --nichols_templates \
  --nichols_Mdb -12 -9 -6 -3 0 0.9 3 6 9 12 \
  --nichols_Ndeg -30 -60 -90 -120 -150 -180 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png"
```

## 3) Nyquist (Plotly) with multiple M-circles + ω marks
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend plotly --plots nyquist --ogata_axes \
  --nyquist_M 1.2 1.05 0.9 \
  --nyquist_marks 0.2 0.4 1 2 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html"
```

## 4) Nyquist (Matplotlib) with multiple M-circles + ω marks
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend mpl --plots nyquist --ogata_axes \
  --nyquist_M 1.2 1.05 0.9 \
  --nyquist_marks 0.2 0.4 1 2 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png"
```

## 5) Bode + Nyquist + Nichols (Plotly), custom grids, saved HTML
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend plotly --ogata_axes \
  --plots bode,nyquist,nichols \
  --nichols_templates \
  --nichols_Mdb -12 -9 -6 -3 0 0.9 3 6 9 12 \
  --nyquist_M 1.2 1.05 0.9 \
  --nyquist_marks 0.2 0.4 1 2 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html"
```

## 6) Default multi-plot (Matplotlib)
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend mpl \
  --plots bode,nyquist,nichols,step,ramp \
  --ogata_axes \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png"
```

## 7) Default multi-plot (Plotly) + HTML export
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend plotly \
  --plots bode,nyquist,nichols,step,ramp \
  --ogata_axes \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html"
```

## 8) Plotly + static PNGs (needs kaleido installed)
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend plotly --plots nyquist,nichols \
  --ogata_axes \
  --nyquist_M 1.2 --nyquist_marks 0.2 0.4 1 2 \
  --nichols_templates --nichols_Mdb -12 -6 0 3 6 9 12 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html" \
  --save_img "frequencyResponse/compensatorTool/out/og728_{kind}.png" \
  --no_show
```

## 9) Nichols (Plotly) – minimal extra contours (just Mdb=0.9)
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend plotly --plots nichols --nichols_templates \
  --nichols_Mdb 0.9 \
  --nichols_Ndeg -60 -120 -180 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html"
```

## 10) Nyquist with only the Ogata M=1.2 circle (both backends)
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend plotly --plots nyquist --ogata_axes \
  --nyquist_M 1.2 \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.html"
```
> For Matplotlib, swap `--backend mpl` and save as PNG.

## 11) Time-domain only (Step & Ramp), hide unstable baseline if any
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend mpl --plots step,ramp --ogata_axes \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png"
```

## 12) Custom frequency grid
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend mpl --plots bode,nyquist,nichols \
  --nichols_templates \
  --nichols_Mdb -12 -9 -6 -3 0 3 6 9 12 \
  --export_csv_prefix "frequencyResponse/compensatorTool/out/og728" \
  --export_json "frequencyResponse/compensatorTool/out/og728_design.json" \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png" \
  --no_show
```

## 13) CSV + JSON exports (good for reports/CI)
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend mpl --plots bode,nyquist,nichols \
  --nichols_templates \
  --nichols_Mdb -12 -9 -6 -3 0 3 6 9 12 \
  --export_csv_prefix "frequencyResponse/compensatorTool/out/og728" \
  --export_json "frequencyResponse/compensatorTool/out/og728_design.json" \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png" \
  --no_show
```

## 14) From a custom plant (TF string) with auto design
```bash
python -m frequencyResponse.compensatorTool.cli \
  --tf "K/(s*(s+1)*(s+2))" --params "K=8" \
  --Kv 10 --pm_target 50 \
  --backend plotly --plots nichols,nyquist --ogata_axes \
  --nichols_templates --nyquist_M 1.2 \
  --save "frequencyResponse/compensatorTool/out/custom_{kind}.html"
```

## 15) From ZPK form
```bash
python -m frequencyResponse.compensatorTool.cli \
  --z "" --p "0, -1, -2" --k "K" --params "K=20" \
  --backend mpl --plots bode,nyquist,nichols \
  --save "frequencyResponse/compensatorTool/out/zpk_{kind}.png"
```

## 16) From State-Space matrices
```bash
python -m frequencyResponse.compensatorTool.cli \
  --A "0,1,0;0,0,1;0,-3,-2" \
  --B "0;0;1" \
  --C "1,0,0" \
  --D "0" \
  --backend mpl --plots bode,nyquist,nichols \
  --save "frequencyResponse/compensatorTool/out/ss_{kind}.png"
```

## 17) Force-show unstable baseline in time responses (for comparison)
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend mpl --plots step,ramp \
  --ogata_axes --show_unstable \
  --save "frequencyResponse/compensatorTool/out/og728_{kind}.png"
```

## 18) Headless batch render (CI-friendly)
```bash
python -m frequencyResponse.compensatorTool.cli --ogata_7_28 \
  --backend plotly --plots bode,nyquist,nichols \
  --ogata_axes \
  --nichols_templates --nyquist_M 1.2 \
  --save "frequencyResponse/compensatorTool/out/batch_{kind}.html" \
  --no_show
```

---

### Notes
- If you need to **read** config/plant files later, place them under `frequencyResponse/compensatorTool/in/` and point the corresponding flags to that path.
- If running in a headless CI environment for Matplotlib, add `--no_show` and rely on saved files under `out/`.
