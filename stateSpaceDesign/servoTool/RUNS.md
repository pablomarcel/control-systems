# stateSpaceDesign.servoTool — RUNS.md (inside‑package edition)

This cookbook assumes you **cd into** the package folder first:

```bash
cd stateSpaceDesign/servoTool
```

Every command below uses `python cli.py ...` and writes outputs into **./out/**.  
(You can still run from repo root via `python -m stateSpaceDesign.servoTool.cli`, but this file focuses on the *inside‑package* workflow.)

---

## 0) Quick help
```bash
python cli.py --help
```

---

## 1) K mode — plant already type‑1 (prefilter k_r computed)
Controller JSON may or may not include `C`. If it doesn’t, provide it via `--C`.

### 1.1 Minimal K mode (C from CLI), JSON + CSV
```bash
python cli.py   --data in/K_controller.sample.json   --C "1 0"   --r 1   --export_json k_mode_io.json   --t "0:0.01:5"   --save_csv k_mode_step.csv   --backend none
```

### 1.2 K mode with Plotly preview (writes `out/servo_plot.html`)
```bash
python cli.py   --data in/K_controller.sample.json   --C "1 0"   --r 1   --t "0:0.05:6"   --backend plotly   --export_json k_mode_io.json
```
*Note:* Plot file auto-saves to `out/servo_plot.html`.

### 1.3 K mode with Matplotlib preview (no file save, just a peek)
```bash
python cli.py   --data in/K_controller.sample.json   --C "1 0"   --r 1   --t "0:0.1:5"   --backend mpl   --no_show
```

### 1.4 K mode — override prefilter `k_r` explicitly
```bash
python cli.py   --data in/K_controller.sample.json   --C "1 0"   --k_r 2.5   --r 1   --export_json k_mode_krovr_io.json   --t "0, 0.5, 1.0, 1.5, 2.0"   --save_csv k_mode_krovr_step.csv   --backend none
```

---

## 2) KI mode — plant is type‑0 (controller JSON includes C, K, kI)
### 2.1 Minimal KI mode, JSON + CSV
```bash
python cli.py   --data in/KI_controller.sample.json   --r 1   --export_json ki_mode_io.json   --t "0:0.01:5"   --save_csv ki_mode_step.csv   --backend none
```

### 2.2 KI mode with Plotly preview
```bash
python cli.py   --data in/KI_controller.sample.json   --r 1   --t "0:0.05:6"   --backend plotly   --export_json ki_mode_io.json
```
*Note:* Plot file auto-saves to `out/servo_plot.html` (same name as in K mode; last run wins).

---

## 3) Notes & paths
- **Inputs**: place controller JSON under `./in/` (e.g., `in/K_controller.json`, `in/KI_controller.json`).  
  You can use the sample files we shipped: `in/K_controller.sample.json`, `in/KI_controller.sample.json` (copy/rename as needed).
- **Outputs**: when you pass bare filenames (e.g., `k_mode_io.json`), they are written into `./out/` automatically.
- **Time vector**: use either a range `"t0:dt:tfinal"` or an explicit list `"t0, t1, t2, ..."`.


## 4) From project root (alternative)
If you prefer running from repo root, the equivalent command is:
```bash
python -m stateSpaceDesign.servoTool.cli --data stateSpaceDesign/servoTool/in/K_controller.json --C "1 0" --export_json k_mode_io.json --save_csv k_mode_step.csv --backend none
```
Outputs still appear in `stateSpaceDesign/servoTool/out/`.
