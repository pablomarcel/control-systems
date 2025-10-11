# frequencyResponse.plotTool — Runbook & Verified Commands (macOS / oh‑my‑zsh)

This README collects **working commands** for `frequencyResponse.plotTool` based on verified runs.
It’s optimized for **oh‑my‑zsh on macOS**.

> You can run from inside the package folder (`frequencyResponse/plotTool`) with:
>
> ```bash
> python cli.py ...
> ```
>
> or as a module from the project root:
>
> ```bash
> python -m frequencyResponse.plotTool.cli ...
> ```

---

## Environment helpers

```bash
# Output folder
export OUT=out

# High‑signal debug (prints libs, backend, parsed args, channel summaries)
export PLOTTOOL_DEBUG=1

# Plotly rendering:
#   CI / headless: export PLOTLY_RENDERER=none
#   Interactive:   export PLOTLY_RENDERER=browser
```

> **Pathing notes**
>
> - `--save-html` is a **file prefix**. If you pass `--save-html "$OUT/run_all"` it writes
>   `out/run_all_bode.html`, `out/run_all_nyquist.html`, `out/run_all_nichols.html`.
>   Only the **parent** directory (`out/`) is created; no extra nested folder.
> - `--save-png` is a **directory** where PNGs are placed (created if missing).

### Minimal sanity checks

```bash
# Help — proves CLI is importable
python cli.py -h
```

> **Design note:** Supply **exactly one** plant description:
> - `--num/--den` **or**
> - `--gain/--zeros/--poles` **or**
> - `--fnum/--fden` (+ optional `--K`).

---

## Ogata baseline plant — \(K / [s (s+1) (0.5 s + 1)]\)

### Plotly Nichols (save + open)
```bash
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --nichols --nichols-grid --nichols-closedloop --plotly \
  --nichols-range=-240,0,-16,32 \
  --save-html "$OUT/nichols_quick" && open "$OUT/nichols_quick_nichols.html"
```

### Matplotlib Nichols (PNG only; no GUI window)
```bash
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --nichols --nichols-grid --nichols-closedloop \
  --nichols-range=-240,0,-16,32 \
  --save-png "$OUT/figs"
```

### Plotly trio (Bode + Nyquist + Nichols)
```bash
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --wmin 0.1 --wmax 5 --npts 600 \
  --bode --nyquist --nichols --nyq-markers --nichols-closedloop \
  --plotly --save-html "$OUT/run_all" && \
  open "$OUT/run_all_bode.html" && \
  open "$OUT/run_all_nyquist.html" && \
  open "$OUT/run_all_nichols.html"
```

---

## Ogata **+5 dB** tangency (custom loci)

```bash
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --nichols --nichols-grid --nichols-closedloop --plotly \
  --nichols-Mdb -12 -9 -6 -3 0 3 5 6 9 12 16 20 24 28 32 \
  --nichols-Ndeg -10 -20 -30 -45 -60 -90 -120 \
  --nichols-range=-240,0,-16,32 \
  --save-html "$OUT/nichols_ogata" && open "$OUT/nichols_ogata_nichols.html"
```

---

## Plant specification modes

### A) Factored strings (+ scalar K)
```bash
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --nichols --nichols-grid --nichols-closedloop --plotly \
  --nichols-range=-240,0,-16,32 \
  --save-html "$OUT/nichols_factored" && open "$OUT/nichols_factored_nichols.html"
```

### B) ZPK-style (gain + poles)
```bash
python cli.py \
  --gain 10 --poles "0, -1, -5" \
  --bode --nyquist --nichols --nichols-grid \
  --plotly --save-html "$OUT/ex7_20_k10" && \
  open "$OUT/ex7_20_k10_bode.html" && \
  open "$OUT/ex7_20_k10_nyquist.html" && \
  open "$OUT/ex7_20_k10_nichols.html"
```

### C) Polynomial coefficients (descending)
```bash
python cli.py \
  --num "20, 20" --den "1, 7, 20, 50, 0" \
  --nichols --nichols-grid --nichols-closedloop \
  --plotly --save-html "$OUT/poly_demo" && open "$OUT/poly_demo_nichols.html"
```

---

## View windows

```bash
# Ogata window
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --nichols --nichols-grid --nichols-closedloop --plotly \
  --nichols-range=-240,0,-16,32 \
  --save-html "$OUT/nichols_win" && open "$OUT/nichols_win_nichols.html"
```

```bash
# Tighter phase window
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --nichols --nichols-grid --nichols-closedloop --plotly \
  --nichols-range=-210,-90,-12,20 \
  --save-html "$OUT/nichols_tight" && open "$OUT/nichols_tight_nichols.html"
```

---

## Frequency sampling

```bash
# Linear, narrow band
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --wmin 0.1 --wmax 2 --npts 2000 \
  --nichols --nichols-grid --nichols-closedloop --plotly \
  --nichols-range=-240,0,-16,32 \
  --save-html "$OUT/nichols_lin" && open "$OUT/nichols_lin_nichols.html"
```

```bash
# Wider band
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --wmin 0.05 --wmax 10 --npts 3000 \
  --nichols --nichols-grid --nichols-closedloop --plotly \
  --nichols-range=-240,0,-16,32 \
  --save-html "$OUT/nichols_log" && open "$OUT/nichols_log_nichols.html"
```

---

## Contour customization

```bash
# Space‑separated lists (recommended)
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --nichols --nichols-grid --plotly \
  --nichols-Mdb -18 -12 -9 -6 -3 0 3 5 6 9 12 18 \
  --nichols-Ndeg -10 -20 -30 -45 -60 -90 -120 \
  --nichols-closedloop --nichols-range=-240,0,-16,32 \
  --save-html "$OUT/nichols_custom" && open "$OUT/nichols_custom_nichols.html"
```

```bash
# CSV variants (zsh‑safe via the equals form)
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --nichols --nichols-grid --plotly \
  --nichols-Mdb-csv="-18,-12,-9,-6,-3,0,3,5,6,9,12,18" \
  --nichols-Ndeg-csv="-10,-20,-30,-45,-60,-90,-120" \
  --nichols-closedloop --nichols-range=-240,0,-16,32 \
  --save-html "$OUT/nichols_csv" && open "$OUT/nichols_csv_nichols.html"
```

```bash
# Hide grid labels (Plotly)
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --nichols --nichols-grid --plotly --nichols-no-grid-labels \
  --nichols-range=-240,0,-16,32 \
  --save-html "$OUT/nichols_nolabels" && open "$OUT/nichols_nolabels_nichols.html"
```

---

## Ogata Example 7‑21

```bash
# Plotly bundle (Bode + Nyquist + Nichols)
python cli.py \
  --fnum "20 (s+1)" --fden "s (s+5) (s^2+2s+10)" \
  --wmin 0.1 --wmax 50 --npts 400 \
  --bode --nyquist --nichols --nyq-markers --nichols-closedloop \
  --plotly --save-html "$OUT/ex7_21" && \
  open "$OUT/ex7_21_bode.html" && \
  open "$OUT/ex7_21_nyquist.html" && \
  open "$OUT/ex7_21_nichols.html"
```

```bash
# Matplotlib trio (PNG + JSON) — no GUI window
python cli.py \
  --fnum "20 (s+1)" --fden "s (s+5) (s^2+2s+10)" \
  --bode --nyquist --nichols --nichols-grid \
  --wmin 0.1 --wmax 100 --npts 400 \
  --save-png "$OUT/figs" --save-json "$OUT/ex7_21_all.json" \
  --title "Ogata Ex. 7-21 — full set"
```

---

## Nyquist showcase (state‑space)

```bash
# Plotly Nyquist with ~11 ω markers
python cli.py \
  --A "-1,-1; 6.5,0" \
  --B "1,1; 1,0" \
  --C "1,0; 0,1" \
  --D "0,0; 0,0" \
  --nyquist --nyq-markers --nyq-samples 11 \
  --plotly --save-html "$OUT/ex7_13" && \
  ls -1 "$OUT"/*nyquist*.html && \
  open "$OUT"/ex7_13*nyquist*.html
```

```bash
# Nyquist with scale factor
python cli.py \
  --fnum "K (s+0.5)" --fden "s^3 + s^2 + 1" --K 1 \
  --scale 0.25 \
  --nyquist --nyq-markers \
  --plotly --save-html "$OUT/ex7_19_scaled" && open "$OUT/ex7_19_scaled_nyquist.html"
```

---

## Bode‑only convenience

```bash
# Plotly Bode only
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --wmin 0.1 --wmax 10 --npts 400 \
  --bode --plotly --save-html "$OUT/bode_only" && open "$OUT/bode_only_bode.html"
```

```bash
# Matplotlib Bode only (PNG)
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --wmin 0.1 --wmax 10 --npts 400 \
  --bode --save-png "$OUT"
```

---

## CI‑ready (headless) examples

```bash
# Headless Plotly Nichols (no GUI)
PLOTLY_RENDERER=none MPLBACKEND=Agg \
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --nichols --nichols-grid --nichols-closedloop --plotly \
  --nichols-range=-240,0,-16,32 \
  --save-html "$OUT/ci_nichols"
```

```bash
# Headless Matplotlib Bode (PNG)
MPLBACKEND=Agg \
python cli.py \
  --fnum "K" --fden "s (s+1) (0.5*s+1)" --K 1 \
  --bode --save-png "$OUT"
```

---

## Common pitfalls (from real logs)

- **No plant** → `ValueError: Use exactly one …`
- **CSV args on zsh** → use **equals** form, e.g. `--nichols-Mdb-csv="..."`.
- **Matplotlib window** → not implemented in the CLI; use `--save-png` or Plotly.
- **Opening saved files**: if unsure of the suffix, list then open:
  ```bash
  ls -1 "$OUT"/*nyquist*.html
  open "$OUT"/*nyquist*.html
  ```

---

### Version glimpse (from debug)
`numpy`, `python-control`, `matplotlib`, backend, and `plotly` versions appear when `PLOTTOOL_DEBUG=1`.
