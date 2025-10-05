import json, os, tempfile, numpy as np
from stateSpaceDesign.observerStatePlotTool.app import ObserverStatePlotApp
from stateSpaceDesign.observerStatePlotTool.apis import PlotRequest, SimulateOptions

def make_payload(path):
    payload = {
        "A": [[0,1],[-2,-3]],
        "B": [[0],[1]],
        "C": [[1,0]],
        "K": [1.0, 2.0],
        "simulation": {
            "t": [0, 0.5, 1.0],
            "x": [[1.0, 0.6, 0.2],
                  [0.0, -0.3, -0.1]],
            "e": [[0.8, 0.5, 0.2],
                  [0.1, -0.2, -0.1]]
        }
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)

def test_app_csv_only():
    with tempfile.TemporaryDirectory() as td:
        data = os.path.join(td, "ex.json")
        make_payload(data)
        csv_path = os.path.join(td, "series.csv")
        req = PlotRequest(
            data_path=data, what="x,e,err,y,u",
            backend="none", subplots=False, save_csv=csv_path,
            simulate=SimulateOptions(enabled=False)
        )
        app = ObserverStatePlotApp()
        resp = app.run(req)
        assert os.path.exists(resp.csv_path)
        # verify header exists
        with open(resp.csv_path, "r", encoding="utf-8") as f:
            head = f.readline().strip()
        assert head.startswith("t,")
