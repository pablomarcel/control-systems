# observerStatePlotTool — RUNS.md (inside‑package edition)

These examples are designed to be executed **from inside** the folder:
```
modernControl/stateSpaceDesign/observerStatePlotTool/
```
Call the CLI shim directly:
```
python cli.py <args...>
```

> Notes
> - When you pass a **basename** to `--save_png`, `--save_html`, or `--save_csv` (e.g., `--save_png demo.png`),
>   the file is saved under this package’s `./out/` folder.
> - The input JSONs should live under `./in/` (e.g., `stateSpaceDesign/observerStatePlotTool/in/ex107.json`).
> - Add `--no_show` to suppress interactive figure windows in automated runs.
> - Backends: `--backend mpl|plotly|both|none`.
> - You can also run from **project root** using the module entrypoint; see Section 9.

---

## 0) Help

```bash
python cli.py --help
```

---

## 1) Plot everything (x, e, y, u) from a JSON with `simulation`

```bash
python cli.py   --data in/ex107.json   --what auto   --backend both   --subplots   --save_png ex107.png   --save_html ex107.html   --save_csv ex107.csv   --no_show
```
> `ex107.png`, `ex107.html`, and `ex107.csv` will be written to `./out/`.

### 1.1) Minimal smoke (no plots, CSV only)

```bash
python cli.py   --data in/ex107.json   --what x,e,err,y,u   --backend none   --save_csv ex107_series.csv
```

### 1.2) Plotly only, overlay `x` and `e` on a single axes

```bash
python cli.py   --data in/ex107.json   --what x,e   --backend plotly   --save_html ex107_xe.html   --no_show
```

### 1.3) Matplotlib only, single figure (no subplots)

```bash
python cli.py   --data in/ex107.json   --what x,e,y,u   --backend mpl   --save_png ex107_mpl.png   --no_show
```

---

## 2) JSON missing `simulation`? Simulate from `A_augmented`

Requires SciPy (`scipy.linalg.expm`). You provide timebase and initial conditions for `x(0)` and `e(0)`.

```bash
python cli.py   --data in/ex107_tf_only.json   --simulate_if_missing   --t 0:0.01:4   --x0 "1 0"   --e0 "0.5 0"   --what x,e,err,y,u   --backend mpl   --subplots   --save_png ex107_sim.png   --no_show
```
> If `u` or `y` are missing, they are reconstructed as `u = -K(x-e)` and `y = Cx` (when `K`/`C` exist in JSON).

---

## 3) Headless/CI‑friendly runs

### 3.1) CSV only (fast)

```bash
python cli.py   --data in/ex107.json   --backend none   --what auto   --save_csv ci_quick.csv
```

### 3.2) Plotly artifacts without opening windows

```bash
python cli.py   --data in/ex107.json   --backend plotly   --what auto   --save_html ci_plot.html   --no_show
```

---

## 4) Subplots vs. overlays

### 4.1) Subplots (Ogata‑style stacks)

```bash
python cli.py   --data in/ex107.json   --what x,e,err   --subplots   --backend mpl   --save_png stacks.png   --no_show
```

### 4.2) Overlay (single axes)

```bash
python cli.py   --data in/ex107.json   --what x,e,err   --backend mpl   --save_png overlay.png   --no_show
```

---

## 5) MIMO output (multiple y’s) example

If your JSON contains multi‑row `C` and a state trajectory `x`, multiple `y_i` traces are emitted.
Assuming `in/mimo.json` has `C` with `p>1` rows and `simulation.x` present:

```bash
python cli.py   --data in/mimo.json   --what y   --backend both   --subplots   --save_png mimo_y.png   --save_html mimo_y.html   --no_show
```

---

## 6) Custom selections

### 6.1) Only the control input `u`

```bash
python cli.py   --data in/ex107.json   --what u   --backend mpl   --save_png u_only.png   --no_show
```

### 6.2) Only estimation error

```bash
python cli.py   --data in/ex107.json   --what err   --backend plotly   --save_html err_only.html   --no_show
```

---

## 7) Absolute save paths (avoid `./out/`)

If you pass an absolute path, that exact path is used:

```bash
python cli.py   --data in/ex107.json   --what auto   --backend mpl   --save_png "/tmp/observer_plot.png"   --save_csv "/tmp/observer_series.csv"   --no_show
```

---

## 8) Sample data included

A tiny sample input is provided to verify the wiring:

```bash
python cli.py   --data in/ex_sample.json   --what auto   --backend both   --save_png sample.png   --save_html sample.html   --no_show
```

---

## 9) Running from **project root** via module entry

From `modernControl/` you can run the package with `-m`:

```bash
python -m stateSpaceDesign.observerStatePlotTool   --data stateSpaceDesign/observerStatePlotTool/in/ex_sample.json   --what auto   --backend plotly   --save_html ex_sample_root.html   --no_show
```

Or target the CLI module explicitly:

```bash
python -m stateSpaceDesign.observerStatePlotTool.cli   --data stateSpaceDesign/observerStatePlotTool/in/ex_sample.json   --backend none   --what x,e,err,y,u   --save_csv ex_sample_root.csv
```

> The module entry sanitizes `-m ...` argv tokens internally, so both invocations behave the same as `python cli.py` inside the package.

---

## 10) Troubleshooting

- **Plotly not installed** → Use `--backend mpl` or `--backend none`, or `pip install plotly`.
- **SciPy not installed** and you requested `--simulate_if_missing` → install SciPy or re‑export JSON with a `simulation` block.
- **Nothing selected to plot** → ensure `--what` matches available series in your JSON (e.g., if there’s no `e`, `err` can’t be plotted).
- **Files not showing up under `out/`** → when using basenames for `--save_*`, artifacts are saved to this package’s `./out/` directory.

