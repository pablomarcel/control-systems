
# tools/tool_expr.py
# Safe expression evaluator for simple arithmetic in tuning rules JSON.
from __future__ import annotations
import ast
from typing import Any, Mapping

_ALLOWED_NODES = {
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Load, ast.Name, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd, ast.Mod, ast.FloorDiv,
    ast.Call # only for functions we explicitly allow below
}

_ALLOWED_FUNCS = {"abs": abs, "min": min, "max": max}

class SafeEvalError(ValueError):
    pass

def _validate(node: ast.AST) -> None:
    if type(node) not in _ALLOWED_NODES:
        raise SafeEvalError(f"Disallowed expression node: {type(node).__name__}")
    for child in ast.iter_child_nodes(node):
        _validate(child)

def safe_eval(expr: str, ctx: Mapping[str, Any]) -> float:
    """
    Evaluate a tiny arithmetic expression safely.
    Supports: +, -, *, /, %, //, **, parentheses, names from ctx, and abs/min/max.
    Recognizes 'inf' in ctx for infinity.
    """
    src = str(expr).strip()
    try:
        node = ast.parse(src, mode="eval")
        _validate(node)
        return _eval(node.body, dict(ctx))
    except SafeEvalError:
        raise
    except Exception as e:
        raise SafeEvalError(f"Failed to evaluate '{expr}': {e}")

def _eval(node: ast.AST, ctx: dict) -> float:
    if isinstance(node, ast.Constant):  # py>=3.8
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise SafeEvalError("Only numeric constants allowed.")
    if isinstance(node, ast.Name):
        if node.id in ctx:
            val = ctx[node.id]
            if isinstance(val, (int, float)):
                return float(val)
            raise SafeEvalError(f"Name '{node.id}' must be numeric.")
        raise SafeEvalError(f"Unknown name '{node.id}'.")
    if isinstance(node, ast.UnaryOp):
        v = _eval(node.operand, ctx)
        if isinstance(node.op, ast.UAdd):
            return +v
        if isinstance(node.op, ast.USub):
            return -v
        raise SafeEvalError("Unsupported unary op.")
    if isinstance(node, ast.BinOp):
        a = _eval(node.left, ctx)
        b = _eval(node.right, ctx)
        if isinstance(node.op, ast.Add):
            return a + b
        if isinstance(node.op, ast.Sub):
            return a - b
        if isinstance(node.op, ast.Mult):
            return a * b
        if isinstance(node.op, ast.Div):
            return a / b
        if isinstance(node.op, ast.Mod):
            return a % b
        if isinstance(node.op, ast.FloorDiv):
            return a // b
        if isinstance(node.op, ast.Pow):
            return a ** b
        raise SafeEvalError("Unsupported binary op.")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise SafeEvalError("Only simple function names allowed.")
        fname = node.func.id
        if fname not in _ALLOWED_FUNCS:
            raise SafeEvalError(f"Function '{fname}' not allowed.")
        args = [_eval(a, ctx) for a in node.args]
        return float(_ALLOWED_FUNCS[fname](*args))
    raise SafeEvalError("Unsupported expression.")
