# controllerTool — RUNS.md (inside-folder, correct output paths)

You are here: `stateSpaceDesign/controllerTool/`

## Quick help
```bash
python cli.py --help
```

## Output path note
When running **from inside this folder**, use `--save_prefix "out/<name>"` so files land in `stateSpaceDesign/controllerTool/out/`.
(The `out/` directory already exists.)

> If you run from the **project root**, then use `--save_prefix "stateSpaceDesign/controllerTool/out/<name>"` instead.

> Tip: for values that start with “-”, prefer the equals form: `--K_poles=-1+1j,-1-1j,-8`

---

## Reference plants
- **P1 (Ogata §10-7):** G(s) = 1 / (s (s^2+1))  
  `--num "1" --den "1 0 1 0"`
- **P2 (from §10-6 into §10-7):** G(s) = 10(s+2) / (s (s+4) (s+6))  
  `--num "10 20" --den "1 10 24 0"`

---

## A) §10-7 example (P1), manual poles
Controller poles: -1±j, -8 — Observer poles: -4, -4

### A1. Both configurations, Matplotlib → saves to `out/ogata10_7_mpl_*.png`
```bash
python cli.py       --num "1" --den "1 0 1 0"       --K_poles=-1+1j,-1-1j,-8       --obs_poles=-4,-4       --cfg both --plots mpl       --save_prefix "out/ogata10_7_mpl"
```

### A2. Both configurations, Plotly (responsive) → saves to `out/ogata10_7_plotly_*.html`
```bash
python cli.py       --num "1" --den "1 0 1 0"       --K_poles=-1+1j,-1-1j,-8       --obs_poles=-4,-4       --cfg both --plots plotly       --save_prefix "out/ogata10_7_plotly"
```

### A3. Both configurations, Plotly (fixed width)
```bash
python cli.py       --num "1" --den "1 0 1 0"       --K_poles=-1+1j,-1-1j,-8       --obs_poles=-4,-4       --cfg both --plots plotly --ply_width 980       --save_prefix "out/ogata10_7_plotly_980"
```

### A4. Both configurations, both backends (save all)
```bash
python cli.py       --num "1" --den "1 0 1 0"       --K_poles=-1+1j,-1-1j,-8       --obs_poles=-4,-4       --cfg both --plots both       --save_prefix "out/ogata10_7_both"
```

### A5. Both configurations, no plots (CI/headless)
```bash
python cli.py       --num "1" --den "1 0 1 0"       --K_poles=-1+1j,-1-1j,-8       --obs_poles=-4,-4       --cfg both --plots none
```

### A6. Config-1 only, Matplotlib
```bash
python cli.py       --num "1" --den "1 0 1 0"       --K_poles=-1+1j,-1-1j,-8       --obs_poles=-4,-4       --cfg cfg1 --plots mpl       --save_prefix "out/ogata10_7_cfg1"
```

### A7. Config-2 only, Plotly
```bash
python cli.py       --num "1" --den "1 0 1 0"       --K_poles=-1+1j,-1-1j,-8       --obs_poles=-4,-4       --cfg cfg2 --plots plotly       --save_prefix "out/ogata10_7_cfg2"
```

### A8. Verbose (no plots)
```bash
python cli.py       --num "1" --den "1 0 1 0"       --K_poles=-1+1j,-1-1j,-8       --obs_poles=-4,-4       --cfg both --plots none --verbose
```

---

## B) §10-6 → §10-7 (P2), manual poles
Controller: -1±2j, -5 — Observer: -4.5, -4.5

### B1. Both configurations, both backends
```bash
python cli.py       --num "10 20" --den "1 10 24 0"       --K_poles=-1+2j,-1-2j,-5       --obs_poles=-4.5,-4.5       --cfg both --plots both       --save_prefix "out/sec10_6_to_10_7_both"
```

### B2. Config-1 only, Matplotlib
```bash
python cli.py       --num "10 20" --den "1 10 24 0"       --K_poles=-1+2j,-1-2j,-5       --obs_poles=-4.5,-4.5       --cfg cfg1 --plots mpl       --save_prefix "out/sec10_6_cfg1"
```

### B3. Config-2 only, Plotly
```bash
python cli.py       --num "10 20" --den "1 10 24 0"       --K_poles=-1+2j,-1-2j,-5       --obs_poles=-4.5,-4.5       --cfg cfg2 --plots plotly       --save_prefix "out/sec10_6_cfg2"
```

### B4. No plots
```bash
python cli.py       --num "10 20" --den "1 10 24 0"       --K_poles=-1+2j,-1-2j,-5       --obs_poles=-4.5,-4.5       --cfg both --plots none
```

---

## C) Auto-synthesized poles from specs (P1)

### C1. Auto: ts + undershoot (Matplotlib)
```bash
python cli.py       --num "1" --den "1 0 1 0"       --ts 5 --undershoot "0.2,0.3" --obs_speed_factor 5       --cfg both --plots mpl       --save_prefix "out/auto_ts5_undershoot_0p2_0p3"
```

### C2. Auto: faster observer (10× sigma), Plotly
```bash
python cli.py       --num "1" --den "1 0 1 0"       --ts 3 --undershoot "0.15,0.25" --obs_speed_factor 10       --cfg both --plots plotly       --save_prefix "out/auto_ts3_obsx10"
```

### C3. Auto, no plots (quick numeric)
```bash
python cli.py       --num "1" --den "1 0 1 0"       --ts 4 --undershoot "0.2,0.2" --obs_speed_factor 5       --cfg both --plots none --verbose
```

---

## Alternative (from project root)
```bash
python cli.py       --num "1" --den "1 0 1 0"       --K_poles=-1+1j,-1-1j,-8       --obs_poles=-4,-4       --cfg both --plots mpl       --save_prefix "out/ogata10_7_mpl"
```
