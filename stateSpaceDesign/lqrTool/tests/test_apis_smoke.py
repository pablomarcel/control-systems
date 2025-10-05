from stateSpaceDesign.lqrTool.apis import LQRRunRequest

def test_runrequest_to_jsonable_smoke():
    req = LQRRunRequest(
        A="0 1; 0 -1", B="0; 1", C="1 0", D="0",
        Q="eye:2", R="1", x0="1 0", step=True, step_amp=2.0,
        prefilter="dcgain", tfinal=2.0, dt=0.1, plots="none"
    )
    d = req.to_jsonable()
    assert isinstance(d, dict)
    assert d["A"].startswith("0")
    assert d["plots"] == "none"
