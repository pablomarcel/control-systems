from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional
import json
import sympy as sp
from .utils import pretty_matrix, to_numeric

def export_json_phi(path: str, Phi: sp.Matrix, Phi_inv: sp.Matrix | None):
    out: Dict[str, List[List[str]]] = {
        "Phi(t)": [[str(sp.simplify(Phi[i, j])) for j in range(Phi.shape[1])] for i in range(Phi.shape[0])]
    }
    if Phi_inv is not None:
        out["Phi_inv(t)"] = [[str(sp.simplify(Phi_inv[i, j])) for j in range(Phi_inv.shape[1])] for i in range(Phi_inv.shape[0])]
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return str(p.resolve())

def format_matrix(M: sp.Matrix, numeric: bool = False, digits: int = 8, pretty: bool = False) -> str:
    if numeric:
        return str(to_numeric(M, digits))
    if pretty:
        return pretty_matrix(M)
    return str(sp.Matrix(M))
