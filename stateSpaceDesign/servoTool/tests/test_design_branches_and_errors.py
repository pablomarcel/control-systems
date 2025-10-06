import json, numpy as np, pathlib, pytest
from stateSpaceDesign.servoTool.apis import run, RunRequest
from stateSpaceDesign.servoTool.core import ControllerPayload, ServoMode
from stateSpaceDesign.servoTool.design import ServoSynthesizer

def test_k_mode_k_r_override(tmp_path):
    ctrl = {"mode":"K","A":[[0,1],[0,-2]],"B":[[0],[1]],"K":[2,3]}
    p = tmp_path / "ctrl.json"
    p.write_text(json.dumps(ctrl), encoding="utf-8")

    req = RunRequest(data_path=str(p), mode_C="1 0", k_r_override=2.5, backend="none")
    resp = run(req)
    assert abs(resp.model.k_r - 2.5) < 1e-12

def test_k_mode_missing_C_raises():
    cp = ControllerPayload(
        mode=ServoMode.K,
        A=np.array([[1.0]]),
        B=np.array([[1.0]]),
        K=np.array([1.0]),
    )
    syn = ServoSynthesizer(cp)
    with pytest.raises(ValueError):
        syn.build()

def test_k_mode_den_zero_raises():
    cp = ControllerPayload(
        mode=ServoMode.K,
        A=np.eye(2),
        B=np.array([[1.0],[0.0]]),
        K=np.array([0.0,0.0]),
        C=np.array([[0.0,1.0]])
    )
    syn = ServoSynthesizer(cp)
    with pytest.raises(ValueError):
        syn.build()

def test_ki_mode_missing_fields_raise():
    # Missing C
    cp = ControllerPayload(
        mode=ServoMode.KI,
        A=np.eye(1),
        B=np.ones((1,1)),
        K=np.array([1.0]),
        kI=1.0
    )
    with pytest.raises(ValueError):
        ServoSynthesizer(cp).build()
    # Missing K
    cp2 = ControllerPayload(
        mode=ServoMode.KI,
        A=np.eye(1),
        B=np.ones((1,1)),
        C=np.ones((1,1)),
        kI=1.0
    )
    with pytest.raises(ValueError):
        ServoSynthesizer(cp2).build()
    # Missing kI
    cp3 = ControllerPayload(
        mode=ServoMode.KI,
        A=np.eye(1),
        B=np.ones((1,1)),
        C=np.ones((1,1)),
        K=np.array([1.0])
    )
    with pytest.raises(ValueError):
        ServoSynthesizer(cp3).build()
