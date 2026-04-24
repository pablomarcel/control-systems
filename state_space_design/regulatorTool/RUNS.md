# regulatorTool — RUNS.md (macOS/zsh friendly)

This tool supports **two ways to run**:

- **From project root (package mode):**
  ```bash
  python -m state_space_design.regulatorTool.cli --help
  ```

- **From *inside* this `regulatorTool/` folder (script mode):**
  ```bash
  python cli.py --help
  ```

When running inside this folder, if you pass `--save_prefix` as a **basename** (e.g., `sys_explicit`), artifacts are saved under `./out/` automatically
(e.g., `out/sys_explicit_root_locus.html`). If you pass a path like `figs/run1`, that directory is created and used as-is.

> **Shell tip (macOS / zsh / oh-my-zsh):** Use **single quotes** and the **`=` form** for any option whose value contains leading `-` or commas.
> Example: `--K_poles='-1+2j,-1-2j,-5'` and `--obs_poles='-4.5,-4.5'`.

---

## Typical runs (from **inside** `stateSpaceDesign/regulatorTool/`)

### 1) Explicit poles (plots on, save under `out/`)
```bash
python cli.py \
  --num='10 20' --den='1 10 24 0' \
  --K_poles='-1+2j,-1-2j,-5' \
  --obs_poles='-10,-10' \
  --x0='1 0 0' --e0='1 0' \
  --pretty --plots=both --save_prefix=sys_explicit
```

### 2) Ogata’s “second trial” observer poles −4.5, −4.5
```bash
python cli.py \
  --num='10 20' --den='1 10 24 0' \
  --K_poles='-1+2j,-1-2j,-5' \
  --obs_poles='-4.5,-4.5' \
  --x0='1 0 0' --e0='1 0' \
  --pretty --plots=both --save_prefix=sys_second
```

### 3) Auto-suggest poles from specs (MPL plots)
```bash
python cli.py \
  --num='10 20' --den='1 10 24 0' \
  --ts=4.0 --undershoot='0.25,0.35' --obs_speed_factor=5 \
  --x0='1 0 0' --e0='1 0' \
  --pretty --plots=mpl --save_prefix=sys_auto_mpl
```

### 4) Auto-suggest (Plotly plots)
```bash
python cli.py \
  --num='10 20' --den='1 10 24 0' \
  --ts=4.0 --undershoot='0.25,0.35' --obs_speed_factor=5 \
  --x0='1 0 0' --e0='1 0' \
  --pretty --plots=plotly --save_prefix=sys_auto_ply
```

### 5) Root-locus with custom axes
```bash
python cli.py \
  --num='10 20' --den='1 10 24 0' \
  --K_poles='-1+2j,-1-2j,-5' --obs_poles='-4.5,-4.5' \
  --x0='1 0 0' --e0='1 0' \
  --plots=mpl --rl_axes='-20,5,-12,12' --save_prefix=sys_mpl_axes
```

### 6) JSON export (written wherever you point it)
```bash
python cli.py \
  --num='10 20' --den='1 10 24 0' \
  --ts=4.0 --undershoot='0.25,0.35' \
  --x0='1 0 0' --e0='1 0' \
  --plots=none \
  --export_json=out/sys_auto_summary.json
```

---

## Same runs from **project root** (optional)

Replace `python cli.py` with:
```bash
python -m state_space_design.regulatorTool.cli
```
Examples:

```bash
python -m state_space_design.regulatorTool.cli \
  --num='10 20' --den='1 10 24 0' \
  --K_poles='-1+2j,-1-2j,-5' \
  --obs_poles='-10,-10' \
  --x0='1 0 0' --e0='1 0' \
  --pretty --plots=both --save_prefix=out/sys_explicit
```

```bash
python -m state_space_design.regulatorTool.cli \
  --num='10 20' --den='1 10 24 0' \
  --ts=4.0 --undershoot='0.25,0.35' \
  --x0='1 0 0' --e0='1 0' \
  --plots=none --export_json=out/sys_auto_summary.json
```
