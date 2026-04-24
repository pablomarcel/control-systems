import math, pytest
from pid_controllers.tuningTool.tools.tool_expr import safe_eval

def test_safe_eval_allowed_ops():
    ctx = {"L": 2.0, "T": 4.0, "inf": float("inf")}
    assert safe_eval("T/L", ctx) == 2.0
    assert safe_eval("2*L + 3/T", ctx) == 2*2.0 + 3/4.0
    assert math.isinf(safe_eval("inf", ctx))

@pytest.mark.parametrize("expr", [
    "__import__('os').system('echo nope')",
    "(lambda x: x)(3)",
    "[x for x in range(3)]",
    "{x: x for x in range(2)}",
    "(1).__class__",
    "open('file')",
])
def test_safe_eval_blocked(expr):
    with pytest.raises(Exception):
        safe_eval(expr, {"L":1, "T":2, "inf": float("inf")})
