# =============================
# File: transient_analysis/hurwitzTool/design.py
# =============================
from __future__ import annotations
from dataclasses import dataclass
from typing import List
import sympy as sp

from .core import Polynomial


@dataclass(slots=True)
class Preset:
    name: str
    coeffs: List[sp.Expr]


def example_numeric() -> Preset:
    return Preset("example_numeric", [1, 5, 6, 7])


def example_symbolic_K() -> Preset:
    K = sp.Symbol("K")
    return Preset("example_symbolic_K", [1, 5, 6, K])