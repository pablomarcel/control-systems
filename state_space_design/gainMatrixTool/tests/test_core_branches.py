import numpy as np
from state_space_design.gainMatrixTool.core import GainMatrixDesigner, parse_poles_arg

def test_core_design_K_verify_and_companion():
    A = np.array([[0,1,0],[0,0,1],[-6,-5,-1]], dtype=float)
    B = np.array([[0],[0],[1]], dtype=float)
    poles = parse_poles_arg(["-2+4j","-2-4j","-10"])
    res = GainMatrixDesigner().design_K(A,B,poles,method="auto",verify=True,pretty=False).payload
    assert "K" in res and "poles_closed" in res

def test_core_design_L_and_place():
    A = np.array([[0,1],[-2,-3]], dtype=float)
    C = np.array([[1,0]], dtype=float)
    poles = parse_poles_arg(["-8","-9"])
    res = GainMatrixDesigner().design_L(A,C,poles,method="place",verify=True,pretty=False).payload
    assert "L" in res

def test_core_design_KI_servo():
    A = np.array([[0,1],[0,-1]], dtype=float)
    B = np.array([[0],[1]], dtype=float)
    C = np.array([[1,0]], dtype=float)
    poles = parse_poles_arg(["-2","-5","-8"])
    res = GainMatrixDesigner().design_KI(A,B,C,poles,method="auto",verify=True,pretty=False).payload
    assert "K" in res and "kI" in res and "poles_closed" in res

def test_core_auto_selects_place_for_mimo():
    A = np.array([[0,1],[-2,-3]], dtype=float)
    B = np.array([[1,0],[0,1]], dtype=float)
    poles = parse_poles_arg(["-3","-4"])
    res = GainMatrixDesigner().design_K(A,B,poles,method="auto",verify=True,pretty=False).payload
    assert "K" in res
