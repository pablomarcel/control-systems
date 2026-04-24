# RUNS — statePlotsTool (run **inside** the package folder)

These commands are designed to be executed **from within** the package:
```
cd stateSpaceDesign/statePlotsTool
```

The CLI supports both modes:

- **Inside the folder (this file’s commands)**: `python cli.py ...`
- **From project root**: `python -m stateSpaceDesign.statePlotsTool.cli ...`

When running **inside** `statePlotsTool/`:
- Inputs default to `./in/`
- Outputs default to `./out/`
- If you pass `--save_*` with only a filename (no directory), it is written under `./out/` automatically.

---

## 0) Quick help
```bash
python cli.py --help
```

---

## 1) Initial Condition (IC) from controller JSON (mode K)

### 1.1 Minimal (CSV only; headless)
```bash
python cli.py \
  --data controller_K.json \
  --scenario ic \
  --x0 "1 0" \
  --t "0:0.1:1.0" \
  --backend none \
  --save_csv ic_states.csv \
  --no_show
# -> writes ./out/ic_states.csv
```

### 1.2 With Matplotlib and Plotly, overlays
```bash
python cli.py \
  --data controller_K.json \
  --scenario ic \
  --x0 "1 0" \
  --t "0:0.01:4" \
  --backend both \
  --save_png ic.png \
  --save_html ic.html \
  --save_csv ic_states.csv \
  --no_show
# -> writes ./out/ic.png, ./out/ic.html, ./out/ic_states.csv
```

### 1.3 Ogata-style stacked subplots
```bash
python cli.py \
  --data controller_K.json \
  --scenario ic \
  --x0 "1 0" \
  --t "0:0.01:4" \
  --subplots \
  --backend mpl \
  --save_png ic_subplots.png \
  --no_show
# -> writes ./out/ic_subplots.png
```

---

## 2) STEP from IO JSON (Acl, Bcl, C, D)

### 2.1 Outputs only (`--what y`)
```bash
python cli.py \
  --data io.json \
  --scenario step \
  --what y \
  --t "0:0.02:4" \
  --backend both \
  --save_csv step_y.csv \
  --save_png step_y.png \
  --save_html step_y.html \
  --no_show
# -> writes ./out/step_y.csv, ./out/step_y.png, ./out/step_y.html
```

### 2.2 States only (`--what states`)
```bash
python cli.py \
  --data io.json \
  --scenario step \
  --what states \
  --t "0:0.02:4" \
  --backend mpl \
  --save_png step_states.png \
  --no_show
# -> writes ./out/step_states.png
```

### 2.3 Outputs + states together (`--what both`, overlay)
```bash
python cli.py \
  --data io.json \
  --scenario step \
  --what both \
  --t "0:0.02:4" \
  --backend mpl \
  --save_png step_both_overlay.png \
  --no_show
```

### 2.4 Outputs + states as stacked subplots
```bash
python cli.py \
  --data io.json \
  --scenario step \
  --what both \
  --subplots \
  --t "0:0.02:4" \
  --backend plotly \
  --save_html step_both_subplots.html \
  --no_show
```

### 2.5 Headless CSV export only
```bash
python cli.py \
  --data io.json \
  --scenario step \
  --what y \
  --t "0:0.05:2" \
  --backend none \
  --save_csv step_headless.csv \
  --no_show
```

---

## 3) Time vector examples

Explicit list:
```bash
python cli.py --data controller_K.json --scenario ic --x0 "1 0" \
  --t "0, 0.05, 0.1, 0.15, 0.2" --backend none --save_csv ic_list.csv --no_show
```

Colon form `t0:dt:tf`:
```bash
python cli.py --data io.json --scenario step --what y \
  --t "0:0.1:3" --backend none --save_csv step_colon.csv --no_show
```

---

## 4) Absolute paths (bypass `./in/`)

You can pass an absolute path for `--data`:
```bash
python cli.py \
  --data "io.json" \
  --scenario step --what y --backend none --save_csv step_abs.csv --no_show
# -> writes ./out/step_abs.csv (unless you provide a directory in the filename)
```

---

## 5) Generate class diagram (optional)

If Graphviz is installed, generate a simple UML diagram **from inside the package**:
```bash
python - << 'PY'
from stateSpaceDesign.statePlotsTool.tools.class_diagram import generate_class_diagram
print(generate_class_diagram("out/uml"))
PY
# -> writes ./out/uml.png
```

---

## 6) From project root (alternative)

Everything above also works from the repo root using the module entry:
```bash
python -m state_space_design.statePlotsTool.cli --data state_space_design/statePlotsTool/in/io.json --scenario step --what y --backend none --save_csv step.csv --no_show
```
