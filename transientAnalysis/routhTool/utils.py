# transientAnalysis/routhTool/utils.py
from __future__ import annotations
from typing import List, Union, Sequence

try:
    import sympy as sp
except Exception:  # pragma: no cover
    sp = None

def parse_coeffs(raw: str) -> List[str]:
    s = raw.replace(";", " ").replace("[", "").replace("]", "").replace(",", " ")
    return [t for t in s.split() if t.strip()]

def coerce_tokens(
    tokens: Sequence[str], symbol_names: Sequence[str]
) -> List[Union[float, int, "sp.Symbol"]]:
    symbol_set = set(symbol_names or [])
    coerced = []
    for tok in tokens:
        coerced.append(_to_numeric_or_symbol(tok, symbol_set))
    return coerced

def _to_numeric_or_symbol(token: str, symbol_set: set):
    if sp is not None and token in symbol_set:
        return sp.Symbol(token, real=True)
    if sp is not None:
        try:
            return sp.nsimplify(token, rational=True)
        except Exception:
            if token in symbol_set:
                return sp.Symbol(token, real=True)
    # fallback numeric
    try:
        return float(token)
    except ValueError:
        if sp is None:
            raise ValueError(
                f"Token '{token}' looks symbolic but SymPy is not installed."
            )
        return sp.Symbol(token, real=True)

def fmt_cell(x) -> str:
    if sp and isinstance(x, sp.Basic):
        try:
            return str(sp.simplify(x))
        except Exception:  # pragma: no cover
            return str(x)
    try:
        return f"{float(x): .6g}"
    except Exception:  # pragma: no cover
        return str(x)