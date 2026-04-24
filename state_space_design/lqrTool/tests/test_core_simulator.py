import numpy as np
from state_space_design.lqrTool.core import StateSpaceModel, Simulator
from state_space_design.lqrTool.design import LQRDesigner
from state_space_design.lqrTool.io import parse_Q, parse_R

def test_simulator_initial_and_forced():
    A = np.array([[0,1],[0,-1]], float)
    B = np.array([[0],[1]], float)
    C = np.array([[1,0]], float)
    D = np.zeros((1,1))
    model = StateSpaceModel(A,B,C,D)
    des = LQRDesigner(model)
    Kres = des.design(parse_Q("eye", 2), parse_R("1"))
    t = np.linspace(0, 1.0, 51)
    x0 = np.array([[1.0],[0.0]])
    tr_ic = Simulator.initial(model, Kres.K, x0, t)
    assert tr_ic.T.shape[0] == t.shape[0]
    tr_st = Simulator.forced_step(model, Kres.K, 0.0, t, amp=1.0)
    assert tr_st.U.shape[1] == t.shape[0]
