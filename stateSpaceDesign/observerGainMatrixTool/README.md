# observerGainMatrixTool (stateSpaceDesign)

Object‑oriented refactor of the standalone `observer_gain_matrix.py`.

## CLI

Run from **repo root** (so outputs land in `stateSpaceDesign/observerGainMatrixTool/out/`):

```bash
python -m stateSpaceDesign.observerGainMatrixTool.cli --A "0 1; -2 -3" --C "1 0" --poles -5 -6 --pretty --export_json observer_basic.json
```

Add controller and closed loop:

```bash
python -m stateSpaceDesign.observerGainMatrixTool.cli   --A "0 1; -2 -3" --B "0;1" --C "1 0"   --poles -8 -9   --K_poles "-3,-4"   --compute_closed_loop --x0 "1,0" --e0 "0,0" --t_final 2 --dt 0.01   --export_json observer_closed.json --latex observer_eq.tex --pretty
```
