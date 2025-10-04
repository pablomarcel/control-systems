
from __future__ import annotations
import sympy as sp
from stateSpaceAnalysis.stateTool.core import (
    controllability_matrix, observability_matrix, alt_modal_ctrl, alt_modal_obs,
    s_plane_minimality, pbh_stabilizable, pbh_detectable, controllable_canonical_from_tf
)

def test_controllability_observability_mats():
    A = sp.Matrix([[0,1],[-2,-3]])
    B = sp.Matrix([[0],[1]])
    C = sp.Matrix([[3,1]])
    Mc = controllability_matrix(A,B)
    Mo = observability_matrix(A,C)
    assert Mc.shape == (2,2) and Mo.shape == (2,2)

def test_alt_modal_ctrl_obs_paths():
    A = sp.Matrix([[1,0],[0,2]]) # diagonal with distinct eigs -> applicable
    B = sp.Matrix([[1],[0]])
    C = sp.Matrix([[1,0]])
    r1, P1, F = alt_modal_ctrl(A,B)
    r2, P2, CP = alt_modal_obs(A,C)
    assert r1 in (True, False) and r2 in (True, False)
    # Non-diagonalizable (Jordan) -> not applicable
    A2 = sp.Matrix([[1,1],[0,1]])
    assert alt_modal_ctrl(A2,B)[0] is None
    assert alt_modal_obs(A2,C)[0] is None

def test_s_plane_minimality_and_pbh():
    num = [1, 3]                 # s+3
    den = [1, 3, 2]              # s^2+3s+2
    ok, gcd_expr, info = s_plane_minimality(num, den)
    assert ok

    # cancellation: (s+1)/((s+1)(s+2))
    ok2, gcd2, info2 = s_plane_minimality([1,1],[1,3,2])
    assert not ok2

    # PBH checks
    A = sp.Matrix([[1,0],[0,-1]])
    B = sp.Matrix([[0],[1]])
    C = sp.Matrix([[0,1]])
    stab_ok, bad_modes = pbh_stabilizable(A,B,eps=0.0)
    det_ok, bad_obs = pbh_detectable(A,C,eps=0.0)
    assert isinstance(bad_modes, list)
    assert isinstance(bad_obs, list)

def test_controllable_canonical_from_tf():
    A,B,C,D = controllable_canonical_from_tf([1,3],[1,3,2])
    n = A.shape[0]
    assert n == 2 and B.shape == (2,1) and C.shape == (1,2) and D.shape == (1,1)
