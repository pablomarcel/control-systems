# README — `stateSpaceDesign.robustTool` (Ogata §10‑9)

Run all commands from the **repo root** (e.g., `.../modernControl/`).  
Entry point:
```bash
python -m stateSpaceDesign.robustTool.cli [OPTIONS]
```

Outputs (JSON) default to: `stateSpaceDesign/robustTool/out/`

---

## Quick help
```bash
python -m stateSpaceDesign.robustTool.cli --help
```

## A) Quick loop‑shaping with PID + mixed‑sensitivity checks
```bash
python -m stateSpaceDesign.robustTool.cli   --num "10 20" --den "1 10 24 0"   --pid "2,5,0.1,20"   --Wm_num "0.2 1" --Wm_den "0.02 1"   --Ws_num "0.5 0" --Ws_den "1 0.05 0"   --wmin 0.01 --wmax 100 --plots mpl --step   --export-json ex_pid_mixed.json
```
*`Wm` makes uncertainty grow at high‑ω; `Ws` penalizes low‑ω error.*

## B) Use explicit lead‑lag K (Ogata §10‑7 style)
```bash
python -m stateSpaceDesign.robustTool.cli   --num "10 20" --den "1 10 24 0"   --K_num "1 6 2.140625" --K_den "1 6 0"   --Wm_num "0.3 1" --Wm_den "0.03 1"   --Ws_num "2 0" --Ws_den "1 0.2 0"   --plots plotly   --export-json ex_leadlag.json
```

## C) Minimal SISO demo (integrator+lag, unity K) — performance weight only
```bash
python -m stateSpaceDesign.robustTool.cli   --num "1" --den "1 1 0"   --Ws_num "1 0" --Ws_den "1 0.1 0"   --plots both   --export-json ex_minimal.json
```

---

## Testing (pytest)
```bash
pytest stateSpaceDesign/robustTool/tests   --override-ini addopts=   --cov   --cov-config=stateSpaceDesign/robustTool/.coveragerc   --cov-report=term-missing
```
(You can start with: `pytest stateSpaceDesign/robustTool/tests -q`)

---

## Notes
- Inputs go in `stateSpaceDesign/robustTool/in/` if needed later.  
- Outputs (JSON/plots you save) should go in `stateSpaceDesign/robustTool/out/`.  
- Design is OOP and testable. Future extensions (MIMO, μ‑analysis, synthesis) can be added by extending `core.py` and `design.py`.
