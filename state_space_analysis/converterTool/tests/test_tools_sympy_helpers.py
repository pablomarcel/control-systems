from __future__ import annotations
import math
from state_space_analysis.converterTool.tools.sympy_helpers import safe_nsimplify

def test_safe_nsimplify_basic():
    r = safe_nsimplify(0.5)
    assert "1/2" in str(r)
