
from __future__ import annotations
import numpy as np
import control as ct
import sympy as sp
from pidControllers.zeroPoleTool import utils, core
from pidControllers.zeroPoleTool.apis import ZeroPoleAPI, DesignRequest

def test_utils_parsers_and_timegrid():
    assert utils.parse_list_of_floats("1, 2  3") == [1.0, 2.0, 3.0]
    cs = utils.parse_list_of_complex("1+2i  -3j  4")
    assert cs[0] == complex(1,2) and cs[1] == complex(0,-3) and cs[2] == complex(4,0)
    s = sp.Symbol("s")
    coeffs = utils.poly_from_string("s**2 + 3*s + 2", s)
    assert np.allclose(coeffs, [1.0, 3.0, 2.0])
    tf = ct.tf([1],[1,1])
    assert "Gp" in utils.pretty_tf("Gp", tf)
    # time grid falls back when poles are marginal
    t = utils.pick_tgrid_from_poles([complex(-1,0), complex(-2,0)])
    assert t[0] == 0.0 and t.ndim == 1

def test_core_plant_polys_and_tf_constructors():
    Gc = core.tf_from_coeff([1,2], [1,3,2])
    assert isinstance(Gc, ct.TransferFunction)
    s = sp.Symbol("s")
    Gp = core.tf_from_poly("s+2", "s**2 + 3*s + 2", s)
    assert isinstance(Gp, ct.TransferFunction)
    Gz = core.tf_from_zpk([ -2 ], [ -1, -2 ], 1.0)
    assert isinstance(Gz, ct.TransferFunction)
    P = core.plant_polys(ct.tf([1,2],[1,3,2]))
    assert P.Kp != 0 and len(P.A) >= 1 and len(P.B) == 3

def test_api_build_gp_forms():
    # coeff
    req1 = DesignRequest(plant_form="coeff", num="1,2", den="1,3,2")
    assert isinstance(ZeroPoleAPI.build_gp(req1), ct.TransferFunction)
    # poly
    req2 = DesignRequest(plant_form="poly", num_poly="s+2", den_poly="s**2+3*s+2")
    assert isinstance(ZeroPoleAPI.build_gp(req2), ct.TransferFunction)
    # zpk
    req3 = DesignRequest(plant_form="zpk", zeros="-2", poles="-1, -2", gain=1.0)
    assert isinstance(ZeroPoleAPI.build_gp(req3), ct.TransferFunction)
