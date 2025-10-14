import numpy as np
import sympy as sp

from modelingSystems.systemTool.design import monic_fraction, charpoly_monic, symbolic_G
from modelingSystems.systemTool.io import parse_list, parse_matrix, ensure_1d
from modelingSystems.systemTool.core import build_mass_spring_damper
from modelingSystems.systemTool.utils import forced_response_safe, normalize_rows

def test_design_helpers_and_charpoly():
    A = np.array([[0.0, 1.0], [-10.0, -1.0]])
    B = np.array([[0.0],[1.0]])
    C = np.array([[1.0,0.0]])
    D = np.array([[0.0]])
    Gs, s = symbolic_G(A,B,C,D)
    num, den = monic_fraction(Gs[0,0], s)
    assert isinstance(num, sp.Expr) and isinstance(den, sp.Expr)
    cp = charpoly_monic(A)
    assert "s**2" in str(cp)

def test_io_parsers_and_utils():
    a = parse_list("[1, 2, 3]")
    assert a == [1,2,3]
    M = parse_matrix("[[1,2],[3,4]]")
    assert M.shape == (2,2)
    v = ensure_1d([1,2,3])
    assert v.shape == (3,)

    sys = build_mass_spring_damper(1.0, 1.0, 10.0)
    T = np.linspace(0, 0.1, 5)
    U = np.ones_like(T)
    t, y, x = forced_response_safe(sys, T, U)
    Y = normalize_rows(t, y)
    assert Y.shape[1] == t.size
