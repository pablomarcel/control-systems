
import json
from stateSpaceDesign.minOrdTool.apis import MinOrdRunRequest
from stateSpaceDesign.minOrdTool.app import run_app

def test_app_run_writes_json(tmp_path):
    outpath = tmp_path/"payload.json"
    req = MinOrdRunRequest(
        A="0 1 0; 0 0 1; -6 -11 -6",
        B=None,
        C="1 0 0",
        poles=["-10","-10"],
        K=None,
        K_poles=None,
        allow_pinv=False,
        precision=4,
        pretty=False,
        export_json=str(outpath),
        verbose=False,
    )
    res = run_app(req)
    assert outpath.exists()
    data = json.loads(outpath.read_text())
    for k in ("Ahat","Bhat","Ctil","Dtil","Ke","charpoly_match"):
        assert k in data
