# transient_analysis/routhTool/utils.py
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
    """Coerce a list of string tokens into floats (when possible) or SymPy Symbols for declared symbols.

    Design choice:
    - If *no* symbols are declared, we prefer **pure numeric** (floats) to keep downstream logic numeric,
      so Routh sign-change counting remains available.
    - Only when a token cannot be parsed as a float and SymPy is available do we fall back to nsimplify.
    - If a token is explicitly declared as a symbol, return a SymPy Symbol regardless.
    """
    symbol_set = set(symbol_names or [])
    coerced = []
    for tok in tokens:
        coerced.append(_to_numeric_or_symbol(tok, symbol_set))
    return coerced

def _to_numeric_or_symbol(token: str, symbol_set: set):
    # If explicitly marked as a symbol, return SymPy Symbol (if available) or raise.
    if token in symbol_set:
        if sp is None:
            raise ValueError(f"Token '{token}' declared as symbol but SymPy is not installed.")
        return sp.Symbol(token, real=True)

    # Prefer numeric first: keep numerics as floats when possible.
    try:
        # int-like strings become floats (consistent with downstream float usage)
        return float(token)
    except ValueError:
        pass

    # Non-numeric: try SymPy if available (e.g., rational expressions like '3/5')
    if sp is not None:
        try:
            return sp.nsimplify(token, rational=True)
        except Exception:
            # last resort: a symbol-like token that wasn't declared; create a Symbol to avoid crash
            return sp.Symbol(token, real=True)

    # No SymPy available and not numeric -> cannot coerce
    raise ValueError(f"Token '{token}' is not numeric and SymPy is not available to parse it.")

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
