import numpy as np
from stateSpaceDesign.lqrTool.core import StateSpaceModel
from stateSpaceDesign.lqrTool.design import LQRDesigner
from stateSpaceDesign.lqrTool.io import parse_Q, parse_R

def test_lqr_designer_shapes():
    A = np.array([[0,1],[0,-1]], float)
    B = np.array([[0],[1]], float)
    C = np.array([[1,0]], float)
    D = np.zeros((1,1))
    model = StateSpaceModel(A,B,C,D)
    des = LQRDesigner(model)
    Q = parse_Q("eye", 2)
    R = parse_R("1")
    res = des.design(Q, R)
    assert res.K.shape == (1,2)
    assert res.P.shape == (2,2)
    assert res.eig_cl.size == 2
