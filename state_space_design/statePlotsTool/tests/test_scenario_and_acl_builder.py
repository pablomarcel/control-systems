
import numpy as np
from state_space_design.statePlotsTool.io import ControllerJSON
from state_space_design.statePlotsTool.core import ScenarioDetector, ClosedLoopBuilder

def test_scenario_detector():
    assert ScenarioDetector.detect({"Acl":0,"Bcl":0,"C":0,"D":0}) == "step"
    assert ScenarioDetector.detect({"A": [[0]]}) == "ic"

def test_acl_from_controller_modes():
    cjK = ControllerJSON(
        mode="K",
        A=np.array([[0,1],[-2,-3]], float),
        B=np.array([[0],[1]], float),
        C=None, K=np.array([[0,0]], float), L=None,
        state_names=["x1","x2"]
    )
    AclK, namesK = ClosedLoopBuilder.Acl_from_controller(cjK)
    assert AclK.shape == (2,2) and namesK == ["x1","x2"]

    cjL = ControllerJSON(
        mode="L",
        A=np.array([[0,1],[-2,-3]], float),
        B=None,
        C=np.array([[1,0]], float),
        K=None,
        L=np.array([[0],[0]], float),
        state_names=["x1","x2"]
    )
    AclL, namesL = ClosedLoopBuilder.Acl_from_controller(cjL)
    assert AclL.shape == (2,2) and namesL == ["x1","x2"]
