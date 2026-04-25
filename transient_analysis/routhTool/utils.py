# transient_analysis/routhTool/utils.py
"""Utility helpers for :mod:`transient_analysis.routhTool`.

This module intentionally keeps parsing and formatting logic small and
side-effect free so it can be reused by the CLI, app façade, and API layer.
"""

from __future__ import annotations

from typing import Any, Sequence, Union

try:
    import sympy as sp
except Exception:  # pragma: no cover - SymPy is optional at import time.
    sp = None

NumericOrSymbolic = Union[float, int, "sp.Basic"]


def parse_coeffs(raw: str) -> list[str]:
    """Parse a coefficient string into individual token strings.

    Accepted separators are commas, semicolons, and whitespace. Square brackets
    are ignored so users can pass values such as ``[1, 5, 6, K]`` from the CLI.

    Args:
        raw: Coefficients in descending polynomial order.

    Returns:
        A list of non-empty coefficient tokens.
    """
    if raw is None:
        raise ValueError("Coefficient text cannot be None.")

    text = str(raw).strip()
    if not text:
        raise ValueError("Coefficient text cannot be empty.")

    text = text.replace(";", " ").replace("[", " ").replace("]", " ").replace(",", " ")
    tokens = [token for token in text.split() if token.strip()]
    if not tokens:
        raise ValueError("No coefficient tokens were found.")
    return tokens


def coerce_tokens(tokens: Sequence[str], symbol_names: Sequence[str] | None) -> list[NumericOrSymbolic]:
    """Convert coefficient tokens into numeric or symbolic objects.

    The coercion policy is deliberately conservative. Declared symbol names are
    converted to SymPy symbols. All other tokens are parsed as floats first. If
    float parsing fails and SymPy is installed, the token is parsed with
    ``sympy.nsimplify``. This keeps numeric Routh workflows numeric while still
    supporting symbolic gain parameters such as ``K``.

    Args:
        tokens: Tokenized coefficient values in descending polynomial order.
        symbol_names: Names that should be treated as symbolic parameters.

    Returns:
        A list containing floats and, when SymPy is available, symbolic values.

    Raises:
        ValueError: If a symbolic token is requested without SymPy, or if a
            non-numeric token cannot be parsed without SymPy.
    """
    symbol_set = {str(name).strip() for name in (symbol_names or []) if str(name).strip()}
    return [_to_numeric_or_symbol(str(token).strip(), symbol_set) for token in tokens]


def _to_numeric_or_symbol(token: str, symbol_set: set[str]) -> NumericOrSymbolic:
    """Coerce one token to a float, SymPy expression, or declared symbol."""
    if not token:
        raise ValueError("Encountered an empty coefficient token.")

    if token in symbol_set:
        if sp is None:
            raise ValueError(f"Token {token!r} was declared as a symbol, but SymPy is not installed.")
        return sp.Symbol(token, real=True)

    try:
        return float(token)
    except ValueError:
        pass

    if sp is not None:
        try:
            return sp.nsimplify(token, rational=True)
        except Exception:
            return sp.Symbol(token, real=True)

    raise ValueError(f"Token {token!r} is not numeric and SymPy is not available to parse it.")


def fmt_cell(x: Any) -> str:
    """Format a Routh-table cell for console and JSON-safe output."""
    if sp is not None and isinstance(x, sp.Basic):
        try:
            return str(sp.simplify(x))
        except Exception:  # pragma: no cover - defensive formatting fallback.
            return str(x)

    try:
        return f"{float(x): .6g}"
    except Exception:  # pragma: no cover - defensive formatting fallback.
        return str(x)
