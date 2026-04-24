
from pid_controllers.pidTool.apis import RunRequest

def test_runrequest_defaults():
    r = RunRequest(plant_form="coeff")
    assert r.structure == "pid_dz"
    assert r.objective == "itae"
    assert isinstance(r.weights, tuple)
