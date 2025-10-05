# observerStatePlotTool — OOP Observer State Plots

**Module path:** `stateSpaceDesign/observerStatePlotTool`  
**CLI entrypoint:** `python -m stateSpaceDesign.observerStatePlotTool.cli`  
**Inputs dir:** `stateSpaceDesign/observerStatePlotTool/in/`  
**Outputs dir:** `stateSpaceDesign/observerStatePlotTool/out/`

This is an object‑oriented refactor of `observer_state_plots.py`. It consumes JSON exported by
`observer_gain_matrix.py` and produces Matplotlib and/or Plotly plots, plus optional CSV exports.

## Install deps (minimal)
```
pip install numpy
# optional:
pip install matplotlib plotly scipy
```

## Quick help
```
python -m stateSpaceDesign.observerStatePlotTool.cli --help
```

## Run commands (ready to paste)

### 1) Plot everything (x, e, y, u) from your `ex107.json`
```
python -m stateSpaceDesign.observerStatePlotTool.cli   --data stateSpaceDesign/observerStatePlotTool/in/ex107.json   --what auto   --backend both   --subplots   --save_png ex107.png   --save_html ex107.html   --save_csv ex107.csv   --no_show
```
> Note: relative filenames like `ex107.png`/`ex107.html`/`ex107.csv` will be saved under
> `stateSpaceDesign/observerStatePlotTool/out/` automatically.

### 2) Overlay only `x` and `e` (no subplots), Plotly only
```
python -m stateSpaceDesign.observerStatePlotTool.cli   --data stateSpaceDesign/observerStatePlotTool/in/ex107.json   --what x,e   --backend plotly   --save_html ex107_xe.html   --no_show
```

### 3) No `simulation` in JSON? Simulate on the fly using `A_augmented`
```
python -m stateSpaceDesign.observerStatePlotTool.cli   --data stateSpaceDesign/observerStatePlotTool/in/ex107_tf_only.json   --simulate_if_missing   --t 0:0.01:4   --x0 "1 0"   --e0 "0.5 0"   --what x,e,err,y,u   --backend mpl   --subplots   --save_png ex107_sim.png   --no_show
```
> This path requires `scipy` for `scipy.linalg.expm`.

## Programmatic use
```python
from stateSpaceDesign.observerStatePlotTool.app import ObserverStatePlotApp
from stateSpaceDesign.observerStatePlotTool.apis import PlotRequest, SimulateOptions

app = ObserverStatePlotApp()
req = PlotRequest(
    data_path="stateSpaceDesign/observerStatePlotTool/in/ex107.json",
    what="auto",
    backend="none",
    save_csv="ex107.csv",
    simulate=SimulateOptions(enabled=False),
    no_show=True,
)
resp = app.run(req)
print(resp)
```
