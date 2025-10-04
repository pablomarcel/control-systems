
from __future__ import annotations
import math
import pytest
from pidControllers.tuningTool.utils import fmt_num, TuningInputs
from pidControllers.tuningTool.tools.tool_expr import safe_eval, SafeEvalError

def test_fmt_num_and_inputs():
    assert fmt_num(float("inf")) == "inf"
    assert fmt_num(3.14159, 3) == "3.14"
    ti = TuningInputs(L=0.5, T=None, Kcr=10, Pcr=2.2)
    ctx = ti.to_ctx()
    assert ctx["L"] == 0.5 and "T" not in ctx and ctx["inf"] == float("inf")

def test_safe_eval_happy_and_errors():
    ctx = {"x": 2.0, "y": 3.0, "inf": float("inf")}
    assert safe_eval("x + y*2", ctx) == 8.0
    assert safe_eval("max(x, y)", ctx) == 3.0
    with pytest.raises(SafeEvalError):
        safe_eval("__import__('os').system('echo hack')", ctx)
    with pytest.raises(SafeEvalError):
        safe_eval("open('x')", ctx)
