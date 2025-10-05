from stateSpaceDesign.gainMatrixTool.apis import GainMatrixAPI

def test_small_K_design():
    api = GainMatrixAPI.default()
    payload = api.single(
        mode="K",
        A="0 1; -2 -3",
        B="0; 1",
        C=None,
        poles=["-2","-5"],
        method="acker",
        verify=True,
        pretty=False
    )
    assert "K" in payload and len(payload["K"][0]) == 2
    assert "poles_closed" in payload

def test_L_observer_design():
    api = GainMatrixAPI.default()
    payload = api.single(
        mode="L",
        A="0 1; -2 -3",
        B=None,
        C="1 0",
        poles=["-10","-11"],
        method="acker",
        verify=True,
        pretty=False
    )
    assert "L" in payload and len(payload["L"]) == 2
