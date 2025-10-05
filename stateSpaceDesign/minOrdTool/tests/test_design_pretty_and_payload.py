
import numpy as np
from stateSpaceDesign.minOrdTool.design import MinOrdAppService

def test_pretty_output_and_payload_json_ready(capsys):
    svc = MinOrdAppService(precision=3, verbose=False)
    A = np.array([[0,1,0],[0,0,1],[-6,-11,-6]], float)
    C = np.array([[1,0,0]], float)
    payload = svc.design_observer(A=A, C=C, poles=np.array([-10,-10]), pretty=True)
    captured = capsys.readouterr().out
    assert "Minimum-Order Observer" in captured
    assert "Characteristic polynomial match" in captured
    assert isinstance(payload["Ahat"], list)
    assert isinstance(payload["Ke"], list)
