# =============================
# File: transientAnalysis/hurwitzTool/utils.py
# =============================
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Optional, Dict
import sympy as sp
import numpy as np


# --- parsing ---
def sympify_list(seq: List[str]) -> List[sp.Expr]:
    return [sp.sympify(t, convert_xor=True) for t in seq]

def parse_coeffs(s: str) -> List[sp.Expr]:
    toks = [t for t in re.split(r"[,\s;]+", s.strip()) if t]
    return sympify_list(toks)

def parse_symbols_arg(symbols: Optional[str]) -> List[sp.Symbol]:
    if not symbols:
        return []
    names = [n.strip() for n in symbols.split(",") if n.strip()]
    return [sp.Symbol(n) for n in names]

def detect_free_symbols(a: List[sp.Expr]) -> List[sp.Symbol]:
    fs = set()
    for ai in a:
        fs |= set(ai.free_symbols)
    return sorted(fs, key=lambda s: s.name)

def parse_subs_list(s: Optional[str]) -> Dict[sp.Symbol, float]:
    if not s:
        return {}
    subs: Dict[sp.Symbol, float] = {}
    for part in re.split(r"[,\s;]+", s.strip()):
        if not part:
            continue
        if "=" not in part:
            raise ValueError(f"Bad --subs item '{part}', expected NAME=value")
        name, val = part.split("=", 1)
        subs[sp.Symbol(name.strip())] = float(val.strip())
    return subs


# --- intervals / pretty printing ---
def one_dim_interval_set(expr_bool: sp.Boolean | sp.Rel, sym: sp.Symbol):
    try:
        S = sp.calculus.util.solve_univariate_inequality(sp.And(expr_bool), sym, relational=False)
        return sp.simplify(S)
    except Exception:
        try:
            return sp.solveset(sp.And(expr_bool), sym, domain=sp.S.Reals)
        except Exception:
            return None


def interval_to_string(I: sp.Interval, latex: bool = False) -> str:
    if latex:
        return f"{'(' if I.left_open else '['}{sp.latex(I.start)},{sp.latex(I.end)}{')' if I.right_open else ']'}"
    return f"{'(' if I.left_open else '['}{sp.sstr(I.start)},{sp.sstr(I.end)}{')' if I.right_open else ']'}"


def set_to_pretty_intervals(S: sp.Set, latex: bool = False) -> str:
    if S is sp.S.Reals:
        return r"(-\infty,\infty)" if latex else "(-∞, ∞)"
    if isinstance(S, sp.Interval):
        return interval_to_string(S, latex=latex)
    if isinstance(S, sp.Union):
        sep = r" \cup " if latex else " ∪ "
        return sep.join(set_to_pretty_intervals(arg, latex=latex) for arg in S.args)
    if isinstance(S, sp.FiniteSet):
        return (r"\{" + ", ".join(sp.latex(x) for x in S) + r"\}") if latex else ("{" + ", ".join(sp.sstr(x) for x in S) + "}")
    return sp.latex(S) if latex else str(S)


# --- ascii heatmap ---
def ascii_heatmap(xs: np.ndarray, ys: np.ndarray, Z: np.ndarray, invert_y: bool = True) -> str:
    rows = []
    yrange = range(len(ys) - 1, -1, -1) if invert_y else range(len(ys))
    for iy in yrange:
        row = "".join("█" if Z[iy, ix] else "·" for ix in range(len(xs)))
        rows.append(row)
    return "\n".join(rows)