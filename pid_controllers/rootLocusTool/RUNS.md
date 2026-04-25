# RUNS — `rootLocusTool` (run from this folder)

Open a shell **inside** this folder:
```
cd pidControllers/rootLocusTool
```

You can run either of these entry points:

- As a script (import shim included):  
  `python cli.py [OPTIONS]`
- As a module (also works from anywhere):  
  `python -m pidControllers.rootLocusTool.cli [OPTIONS]`

> All relative output paths below write into **`./out/`** inside this package
> (no more top-level `out/`).

---

## Quick help & smoke

### Show help
```bash
python cli.py --help
```

### Minimal smoke (no plot, JSON only)
```bash
python cli.py \
  --example ogata_8_1 \
  --no_plot \
  --export_json out/smoke.json
```

---

## Plotly (HTML)

### Full-width Plotly, Ogata limits
```bash
python cli.py \
  --example ogata_8_1 \
  --zeta_values 0.60 0.65 0.67 0.70 \
  --omega 0.2 12 300 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --save out/rl_og81_plotly.html
```

### Force Ogata’s zero at −0.65 (match Fig. 8-12)
```bash
python cli.py \
  --example ogata_8_1 \
  --a 0.65 \
  --zeta_values 0.60 0.65 0.67 0.70 \
  --omega 0.2 12 300 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --save out/rl_og81_plotly_a065.html
```

### Plotly compact
```bash
python cli.py \
  --example ogata_8_1 \
  --zeta_values 0.6 0.7 \
  --omega 0.2 6 120 \
  --backend plotly \
  --title "Root Locus (Ogata 8-1, compact)" \
  --precision 5 \
  --xlim -10 2 --ylim -8 8 \
  --save out/rl_og81_compact.html
```

---

## Matplotlib (PNG)

### Matplotlib PNG
```bash
python cli.py \
  --example ogata_8_1 \
  --a 0.65 \
  --backend mpl \
  --xlim -10 2 --ylim -8 8 \
  --save out/rl_og81_mpl.png
```

### Matplotlib faster
```bash
python cli.py \
  --example ogata_8_1 \
  --zeta_values 0.6 0.7 \
  --omega 0.2 6 120 \
  --backend mpl \
  --xlim -10 2 --ylim -8 8 \
  --save out/rl_og81_fast.png
```

---

## Headless scans (no figure)

### JSON only
```bash
python cli.py \
  --example ogata_8_1 \
  --zeta_values 0.60 0.65 0.67 0.70 \
  --omega 0.2 12 300 \
  --no_plot \
  --export_json out/rl_scan.json
```

### JSON + CSV rows
```bash
python cli.py \
  --example ogata_8_1 \
  --zeta_values 0.6 0.7 \
  --omega 0.2 6 120 \
  --no_plot \
  --export_json out/rl_scan_small.json \
  --export_csv  out/rl_scan_small.csv
```

### Headless + analysis summary (Mp, Ts, Tr, margins)
```bash
python cli.py \
  --example ogata_8_1 \
  --zeta_values 0.6 0.65 0.7 \
  --omega 0.2 8 200 \
  --no_plot \
  --analyze \
  --export_json out/rl_with_perf.json
```

---

## Custom plant via numerator/denominator

### Plotly HTML for Gp(s) = 1/(s(s+1))
```bash
python cli.py \
  --num 1 \
  --den "1 1 0" \
  --zeta_values 0.6 0.7 \
  --omega 0.2 6 120 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --save out/rl_numden_plotly.html
```

### Headless scan + CSV for custom plant
```bash
python cli.py \
  --num 1 \
  --den "1 6 5 0" \
  --zeta_range 0.6 0.7 --zeta_n 4 \
  --omega 0.2 12 300 \
  --no_plot \
  --export_csv out/rl_numden.csv
```

---

## Advanced knobs

### Wider k-range for angle condition
```bash
python cli.py \
  --example ogata_8_1 \
  --zeta_values 0.6 0.65 0.7 \
  --omega 0.2 10 250 \
  --kmin -2 --kmax 2 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --save out/rl_km2_k2.html
```

### ζ-ray clipping controls
```bash
python cli.py \
  --example ogata_8_1 \
  --zeta_values 0.6 0.7 \
  --omega 0.2 6 120 \
  --ray_wmin 0.5 \
  --ray_scale 1.10 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --save out/rl_ray_clip.html
```

### Provide explicit axes
```bash
python cli.py \
  --example ogata_8_1 \
  --zeta_values 0.62 0.68 \
  --omega 0.2 8 180 \
  --backend mpl \
  --xlim -12 3 --ylim -9 9 \
  --save out/rl_custom_axes.png
```

---

## Tips
- `MPLBACKEND=Agg` helps in headless terminals when using the Matplotlib backend.
- Quotes are required for `--den` with spaces, e.g., `--den "1 6 5 0"`.

### Sphinx

python -m pid_controllers.rootLocusTool.cli sphinx-skel pid_controllers/rootLocusTool/docs
python -m sphinx -b html docs docs/_build/html
open docs/_build/html/index.html
sphinx-autobuild docs docs/_build/html