
from __future__ import annotations
import types
import numpy as np
import control as ct
import sys
from pid_controllers.zeroPoleTool import utils

def test_utils_parsers_and_outdir_and_poly():
    tmp = utils.ensure_out_dir()  # package-local out
    assert tmp.endswith("pid_controllers/zeroPoleTool/out")
    assert utils.parse_list_of_floats("1, 2  3") == [1.0,2.0,3.0]
    assert utils.parse_list_of_complex("1+2j, -3i  4") == [complex(1,2), complex(0,-3), complex(4,0)]
    # poly_from_string
    s = __import__("sympy").symbols("s")
    coeffs = utils.poly_from_string("(s+1)*(s+2)", s)
    assert coeffs == [1.0, 3.0, 2.0]

def test_utils_forced_xy_tuple_path(monkeypatch):
    # Build a simple system and fake forced_response to return tuple/list path
    G = ct.tf([1.0],[1.0,1.0])
    t = np.linspace(0, 1, 11)
    u = np.ones_like(t)

    class Dummy:
        pass

    def fake_forced_response(sys, tt, uu):
        # Return (t,y) with y as shape (1,N) to hit squeeze logic
        return (tt, np.array([np.sin(tt)]))

    import control.timeresp as tr
    monkeypatch.setattr(tr, "forced_response", fake_forced_response, raising=True)
    tout, yout = utils.forced_xy(G, t, u)
    assert tout.shape == yout.shape == t.shape
