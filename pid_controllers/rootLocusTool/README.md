
# README — `pidControllers.rootLocusTool` Command Cookbook (correct output paths)

Run all commands from your project root (e.g., `.../modernControl`).  
**Outputs will be written inside `pidControllers/rootLocusTool/out/`** by passing **absolute paths**
derived from the current working directory (`$(pwd)`), which avoids the tool's default `./out/` prefixing.

> CLI entry point:
>
> ```bash
> python -m pid_controllers.rootLocusTool.cli --help
> ```

---

## Quick help & sanity checks

### Show help
```bash
python -m pid_controllers.rootLocusTool.cli --help
```

### Minimal smoke test (no plot, JSON only)
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --no_plot \
  --export_json "$(pwd)/pidControllers/rootLocusTool/out/smoke.json"
```

---

## 1) Plotly (HTML) — Ogata preset and variants

### Full-width Plotly, Ogata limits
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --zeta_values 0.60 0.65 0.67 0.70 \
  --omega 0.2 12 300 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --save "$(pwd)/pidControllers/rootLocusTool/out/rl_og81_plotly.html"
```

### Force Ogata’s zero at −0.65 (match Fig. 8-12)
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --a 0.65 \
  --zeta_values 0.60 0.65 0.67 0.70 \
  --omega 0.2 12 300 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --save "$(pwd)/pidControllers/rootLocusTool/out/rl_og81_plotly_a065.html"
```

### Plotly with a custom title + precision
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --zeta_values 0.6 0.7 \
  --omega 0.2 6 120 \
  --backend plotly \
  --title "Root Locus (Ogata 8-1, compact)" \
  --precision 5 \
  --xlim -10 2 --ylim -8 8 \
  --save "$(pwd)/pidControllers/rootLocusTool/out/rl_og81_compact.html"
```

---

## 2) Matplotlib (PNG) — Ogata preset and variants

### Matplotlib PNG
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --a 0.65 \
  --backend mpl \
  --xlim -10 2 --ylim -8 8 \
  --save "$(pwd)/pidControllers/rootLocusTool/out/rl_og81_mpl.png"
```

### Matplotlib with fewer points (faster)
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --zeta_values 0.6 0.7 \
  --omega 0.2 6 120 \
  --backend mpl \
  --xlim -10 2 --ylim -8 8 \
  --save "$(pwd)/pidControllers/rootLocusTool/out/rl_og81_fast.png"
```

---

## 3) Headless scans (no figure) + exports

### Headless: JSON only
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --zeta_values 0.60 0.65 0.67 0.70 \
  --omega 0.2 12 300 \
  --no_plot \
  --export_json "$(pwd)/pidControllers/rootLocusTool/out/rl_scan.json"
```

### Headless: JSON + CSV rows
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --zeta_values 0.6 0.7 \
  --omega 0.2 6 120 \
  --no_plot \
  --export_json "$(pwd)/pidControllers/rootLocusTool/out/rl_scan_small.json" \
  --export_csv  "$(pwd)/pidControllers/rootLocusTool/out/rl_scan_small.csv"
```

### Headless + analysis summary (Mp, Ts, Tr, margins) at recommended s*
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --zeta_values 0.6 0.65 0.7 \
  --omega 0.2 8 200 \
  --no_plot \
  --analyze \
  --export_json "$(pwd)/pidControllers/rootLocusTool/out/rl_with_perf.json"
```

---

## 4) Custom plant via numerator/denominator

### Plotly HTML for Gp(s) = 1 / (s(s+1))
```bash
python -m pid_controllers.rootLocusTool.cli \
  --num 1 \
  --den "1 1 0" \
  --zeta_values 0.6 0.7 \
  --omega 0.2 6 120 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --save "$(pwd)/pidControllers/rootLocusTool/out/rl_numden_plotly.html"
```

### Headless scan for a custom plant + CSV
```bash
python -m pid_controllers.rootLocusTool.cli \
  --num 1 \
  --den "1 6 5 0" \
  --zeta_range 0.6 0.7 --zeta_n 4 \
  --omega 0.2 12 300 \
  --no_plot \
  --export_csv "$(pwd)/pidControllers/rootLocusTool/out/rl_numden.csv"
```

---

## 5) Advanced knobs (angles, rays, axes)

### Toggle k range for angle condition
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --zeta_values 0.6 0.65 0.7 \
  --omega 0.2 10 250 \
  --kmin -2 --kmax 2 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --save "$(pwd)/pidControllers/rootLocusTool/out/rl_km2_k2.html"
```

### Ray clipping controls
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --zeta_values 0.6 0.7 \
  --omega 0.2 6 120 \
  --ray_wmin 0.5 \
  --ray_scale 1.10 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --save "$(pwd)/pidControllers/rootLocusTool/out/rl_ray_clip.html"
```

### Provide explicit axes (bypass auto/ogata defaults)
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --zeta_values 0.62 0.68 \
  --omega 0.2 8 180 \
  --backend mpl \
  --xlim -12 3 --ylim -9 9 \
  --save "$(pwd)/pidControllers/rootLocusTool/out/rl_custom_axes.png"
```

---

## 6) Absolute save paths (you can also hardcode your full absolute path)

```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --zeta_values 0.6 0.65 0.7 \
  --omega 0.2 6 120 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --save "$(pwd)/pidControllers/rootLocusTool/out/rl_absolute.html"
```

---

## 7) Handy presets

### Fast preview (tiny grid, quick to iterate)
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --zeta_values 0.6 0.7 \
  --omega 0.2 3 30 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --save "$(pwd)/pidControllers/rootLocusTool/out/rl_fast_preview.html"
```

### “Book figure” look with analysis
```bash
python -m pid_controllers.rootLocusTool.cli \
  --example ogata_8_1 \
  --a 0.65 \
  --zeta_values 0.60 0.65 0.67 0.70 \
  --omega 0.2 12 300 \
  --backend plotly \
  --xlim -10 2 --ylim -8 8 \
  --analyze \
  --save "$(pwd)/pidControllers/rootLocusTool/out/rl_og81_book_with_perf.html" \
  --export_json "$(pwd)/pidControllers/rootLocusTool/out/rl_og81_book_with_perf.json"
```

---

## Notes
- We pass absolute paths using `$(pwd)` so outputs land exactly in `pidControllers/rootLocusTool/out/` (and **not** under `./out/`).
- Use quotes around paths with `$(pwd)` to protect spaces.
- Use quotes for `--den` when passing space-separated coefficients, e.g., `--den "1 6 5 0"`.
- `--no_plot` skips all plot preparation; exports still work.
- Set `MPLBACKEND=Agg` on headless servers if you call Matplotlib directly.
