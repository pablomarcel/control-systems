# -*- coding: utf-8 -*-
"""Utility helpers for state_space_design.minOrdTool."""

from __future__ import annotations

from typing import Any
import numpy as np
import sympy as sp

__all__ = [
    "array2str",
    "pretty_poly",
    "mat_inline",
    "complex_list_to_pairs",
    "sympy_pretty_observer",
    "_complex_to_pair",
    "to_jsonable",
]


# ------------------------- Pretty-print helpers ------------------------- #

def array2str(M: Any, precision: int = 4) -> str:
    """Return a compact string for a matrix or array."""
    arr = np.asarray(M)
    arr = np.real_if_close(arr, tol=1e8)
    if np.iscomplexobj(arr):
        fmt = {
            "complex_kind": lambda z: (
                f"{z.real:.{precision}f}"
                f"{'+' if z.imag >= 0 else ''}{z.imag:.{precision}f}j"
            )
        }
        return np.array2string(arr, formatter=fmt)
    return np.array2string(
        np.asarray(arr, float),
        precision=precision,
        suppress_small=True,
        floatmode="maxprec_equal",
    )


def pretty_poly(coeffs: Any, var: str = "s") -> str:
    """Return a readable polynomial string from descending coefficients."""
    coeffs = np.asarray(coeffs, float).ravel()
    n = len(coeffs) - 1
    terms = []
    for i, a in enumerate(coeffs):
        p = n - i
        if p == 0:
            terms.append(f"{a:.6g}")
        elif p == 1:
            terms.append(f"{a:.6g}{var}")
        else:
            terms.append(f"{a:.6g}{var}^{p}")
    s = " + ".join(terms)
    s = s.replace(f"1{var}^", f"{var}^").replace(f"1{var}", var).replace("+ -", "- ")
    return s


def mat_inline(M: Any, precision: int = 4) -> str:
    """Return a one-line matrix representation for console output."""
    A = np.asarray(np.real_if_close(M, 1e8))
    if A.ndim == 1:
        A = A.reshape(1, -1)

    def _fmt_num(x: float, precision: int) -> str:
        y = float(np.real_if_close(x, 1e8))
        s = f"{y:.{precision}f}"
        s = s.rstrip("0").rstrip(".") if "." in s else s
        if s == "-0":
            s = "0"
        return s

    rows = []
    for i in range(A.shape[0]):
        row = " ".join(_fmt_num(v, precision) for v in A[i, :])
        rows.append(row)
    return "[[" + "]; ".join(rows) + "]]"


def complex_list_to_pairs(zs: Any) -> list[list[float]]:
    """Convert complex values into real-imaginary pairs."""
    out: list[list[float]] = []
    for z in np.asarray(zs).ravel():
        zc = complex(z)
        out.append([float(np.real(zc)), float(np.imag(zc))])
    return out


def sympy_pretty_observer(
    Ahat: np.ndarray,
    Bhat: np.ndarray,
    Fhat: np.ndarray | None,
    Ctil: np.ndarray,
    Dtil: np.ndarray,
    m_inputs: int | None,
) -> None:
    """Print the observer equations using SymPy pretty printing."""
    r = Ahat.shape[0]
    n = Ctil.shape[0]
    y = sp.Symbol("y")
    et = sp.MatrixSymbol("et", r, 1)
    et_dot = sp.MatrixSymbol("et_dot", r, 1)

    Ahs = sp.Matrix(np.asarray(Ahat, float))
    Bhs = sp.Matrix(np.asarray(Bhat, float))
    rhs = Ahs * et + Bhs * y

    if Fhat is not None and (m_inputs is None or m_inputs > 0):
        m = Fhat.shape[1]
        u = sp.MatrixSymbol("u", m, 1)
        Fhs = sp.Matrix(np.asarray(Fhat, float))
        rhs = rhs + Fhs * u

    print("\nSymPy pretty (ASCII):")
    sp.pprint(sp.Eq(et_dot, rhs), use_unicode=True)

    x_hat = sp.MatrixSymbol("x_hat", n, 1)
    Cts = sp.Matrix(np.asarray(Ctil, float))
    Dts = sp.Matrix(np.asarray(Dtil, float))
    rhs2 = Cts * et + Dts * y
    sp.pprint(sp.Eq(x_hat, rhs2), use_unicode=True)


# ------------------------- JSON-safe conversion ------------------------- #

def _complex_to_pair(z: complex | np.complexfloating) -> float | list[float]:
    """Convert a complex scalar into a JSON-safe value."""
    zc = complex(z)
    zr = float(np.real(zc))
    zi = float(np.imag(zc))
    if abs(zi) < 1e-12:
        return zr
    return [zr, zi]


def _map_complex_in_container(x: Any) -> Any:
    """Convert complex scalar leaves inside a nested container."""
    if isinstance(x, list):
        return [_map_complex_in_container(v) for v in x]
    if isinstance(x, tuple):
        return tuple(_map_complex_in_container(v) for v in x)
    if isinstance(x, complex):
        return _complex_to_pair(x)
    try:
        if isinstance(x, np.complexfloating):  # type: ignore[attr-defined]
            return _complex_to_pair(x)
    except Exception:
        pass
    return x


def to_jsonable(obj: Any) -> Any:
    """Recursively convert NumPy and complex values into JSON-safe types."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, np.ndarray):
        if np.iscomplexobj(obj):
            return _map_complex_in_container(obj.tolist())
        return obj.tolist()

    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.complexfloating):
        return _complex_to_pair(obj)

    if isinstance(obj, complex):
        return _complex_to_pair(obj)

    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]

    return obj
