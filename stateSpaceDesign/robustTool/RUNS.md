# RUNS — `stateSpaceDesign.robustTool` (Ogata §10‑9)

You can run **from inside this folder** (import shim enabled) *or* from the repo root.

- Inside this folder:
  ```bash
  python cli.py --help
  ```

- From repo root:
  ```bash
  python -m stateSpaceDesign.robustTool.cli --help
  ```

Outputs default to `./out/` (when running inside this folder) or `stateSpaceDesign/robustTool/out/` (when run as a module).

> **Oh My Zsh tip:** use the `--flag=value` form to avoid parsing surprises (e.g., values starting with `-`).

---

## A) Quick loop‑shaping with PID + mixed‑sensitivity checks (run *inside* this folder)
```bash
python cli.py \
  --num="10 20" --den="1 10 24 0" \
  --pid="2,5,0.1,20" \
  --Wm_num="0.2 1" --Wm_den="0.02 1" \
  --Ws_num="0.5 0" --Ws_den="1 0.05 0" \
  --wmin=0.01 --wmax=100 --plots=mpl --step \
  --export-json="ex_pid_mixed.json"
```

## B) Use explicit lead‑lag K (Ogata §10‑7 style)
```bash
python cli.py \
  --num="10 20" --den="1 10 24 0" \
  --K_num="1 6 2.140625" --K_den="1 6 0" \
  --Wm_num="0.3 1" --Wm_den="0.03 1" \
  --Ws_num="2 0" --Ws_den="1 0.2 0" \
  --plots=plotly \
  --export-json="ex_leadlag.json"
```

## C) Minimal SISO demo (integrator+lag, unity K) — performance weight only
```bash
python cli.py \
  --num="1" --den="1 1 0" \
  --Ws_num="1 0" --Ws_den="1 0.1 0" \
  --plots=both \
  --export-json="ex_minimal.json"
```

---

## The same, from repo root
```bash
python -m stateSpaceDesign.robustTool.cli \
  --num="10 20" --den="1 10 24 0" \
  --pid="2,5,0.1,20" \
  --Wm_num="0.2 1" --Wm_den="0.02 1" \
  --Ws_num="0.5 0" --Ws_den="1 0.05 0" \
  --wmin=0.01 --wmax=100 --plots=mpl --step \
  --export-json="ex_pid_mixed.json"
```

---

## Testing (pytest from repo root)
```bash
pytest stateSpaceDesign/robustTool/tests \
  --override-ini addopts= \
  --cov \
  --cov-config=stateSpaceDesign/robustTool/.coveragerc \
  --cov-report=term-missing
```

Notes:
- If a filename is passed to `--export-json` without a directory, it’s written under `./out/` when run here, or under `stateSpaceDesign/robustTool/out/` when run as a module.
- Prefer `--flag=value` (with quotes if needed) on zsh.
