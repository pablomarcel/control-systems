
from __future__ import annotations
from pathlib import Path
from pidControllers.tuningTool.core import TuningEngine
from pidControllers.tuningTool.utils import TuningInputs

RULES = {
  "methods": {
    "ZN_step": {
      "controllers": {
        "PID": {
          "formula": {"Kp": "1.2*T/L", "Ti": "2*L", "Td": "0.5*L"},
          "derived": {"Ki": "Kp/Ti", "Kd": "Kp*Td"},
          "implied_zero_info": {"location": "-1/L", "multiplicity": 2}
        }
      }
    },
    "ZN_simple": {
      "controllers": {
        "PI": {
          "formula": {"Kp": "0.9*T/L", "Ti": "3*L", "Td": "0"},
          # no 'derived' block -> engine should fall back
        }
      }
    }
  }
}

def test_engine_compute_with_derived_and_zeros():
    eng = TuningEngine()
    inputs = TuningInputs(L=0.8, T=3.0)
    res = eng.compute(RULES, "ZN_step", "PID", inputs)
    assert res.Kp > 0 and res.Ti > 0 and res.Td > 0
    assert res.Ki == res.Kp / res.Ti
    assert res.Kd == res.Kp * res.Td
    assert res.controller_zeros_location == -1.0 / 0.8
    assert res.controller_zeros_multiplicity == 2

def test_engine_fallback_when_no_derived():
    eng = TuningEngine()
    inputs = TuningInputs(L=1.0, T=2.0)
    res = eng.compute(RULES, "ZN_simple", "PI", inputs)
    assert res.Ki == res.Kp / res.Ti
    assert res.Kd == res.Kp * res.Td
