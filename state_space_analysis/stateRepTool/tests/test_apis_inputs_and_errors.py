import pytest
from state_space_analysis.stateRepTool.apis import StateRepAPIRequest, StateRepService

def test_api_from_tf_and_numden():
    req = StateRepAPIRequest(tf="(s+3)/(s^2+3*s+2)", which="controllable")
    resp = StateRepService.run(req)
    assert "controllable" in resp.results
    req2 = StateRepAPIRequest(num="1,3", den="1,3,2", which="observable")
    resp2 = StateRepService.run(req2)
    assert "observable" in resp2.results

def test_api_errors_on_missing_inputs():
    with pytest.raises(ValueError):
        StateRepService.run(StateRepAPIRequest(which="all"))
