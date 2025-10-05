# statePlotsTool (stateSpaceDesign)

Object‑oriented refactor of `state_plots.py` with clean, testable architecture.

## Layout
```
stateSpaceDesign/statePlotsTool/
  app.py      # App orchestration and CLI arg→kwargs adapter
  apis.py     # Public API surface: RunRequest and StatePlotsAPI
  core.py     # Pure logic: parsing, closed-loop builder, simulator
  design.py   # IO/plot exports (CSV, Matplotlib, Plotly)
  io.py       # JSON loaders and typed payloads
  utils.py    # Paths, decorators
  tools/
    class_diagram.py
  tests/
    test_ic_csv.py
    test_step_csv.py
  in/         # sample inputs (you can add more)
  out/        # outputs land here
  cli.py      # CLI entry: python -m stateSpaceDesign.statePlotsTool.cli
```

## CLI
```bash
python -m stateSpaceDesign.statePlotsTool.cli --help
```

### IC from controller JSON
```bash
python -m stateSpaceDesign.statePlotsTool.cli   --data controller_K.json   --scenario ic   --x0 "1 0"   --t "0:0.01:4"   --backend both   --save_csv ic_states.csv   --save_png ic.png   --save_html ic.html   --no_show
```

Put your `controller_K.json` in `stateSpaceDesign/statePlotsTool/in/` (or pass an absolute path).

### STEP from IO JSON
```bash
python -m stateSpaceDesign.statePlotsTool.cli   --data io.json   --scenario step   --what both   --t "0:0.01:4"   --backend both   --save_csv step.csv   --save_png step.png   --save_html step.html   --no_show
```

## Programmatic API
```python
from pathlib import Path
from stateSpaceDesign.statePlotsTool.apis import StatePlotsAPI, RunRequest

api = StatePlotsAPI()
req = RunRequest(data=Path("stateSpaceDesign/statePlotsTool/in/io.json"),
                 scenario="step", what="y", t="0:0.1:1.0",
                 backend="none", save_csv="step.csv")
res = api.run(req)
print(res)
```

## Class diagram (optional)
```bash
python - << 'PY'
from stateSpaceDesign.statePlotsTool.tools.class_diagram import generate_class_diagram
from stateSpaceDesign.statePlotsTool.utils import DEFAULT_OUT_DIR
print(generate_class_diagram(DEFAULT_OUT_DIR / "uml"))
PY
```
