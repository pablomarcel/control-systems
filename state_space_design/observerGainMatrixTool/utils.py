from __future__ import annotations

import re
from typing import Sequence, Dict, List

import numpy as np


# ---------- Parsing helpers ----------

def parse_matrix(s: str) -> np.ndarray:
    """Parse a numeric matrix string into a float numpy array."""
    rows = [r for r in s.replace("\n", ";").split(";") if r.strip()]
    out = []
    for r in rows:
        toks = [t for t in r.replace(",", " ").split() if t.strip()]
        out.append([float(t) for t in toks])
    return np.array(out, dtype=float)


def parse_vector(s: str) -> np.ndarray:
    """Parse a numeric vector string into a column vector."""
    return parse_matrix(s).reshape(-1, 1)


def _norm_cplx(tok: str) -> str:
    """Normalize a complex-number token for Python parsing."""
    return tok.strip().replace("I", "j").replace("i", "j").replace(" ", "")


def parse_cplx_tokens(tokens: Sequence[str]) -> np.ndarray:
    """Parse complex-number tokens into a complex numpy array."""
    return np.array([complex(_norm_cplx(t)) for t in tokens], dtype=complex)


def parse_cplx_csv(s: str) -> np.ndarray:
    """Parse comma-separated complex-number tokens."""
    toks = [t for t in s.split(",") if t.strip()]
    return parse_cplx_tokens(toks)


CSV_CPLX_RE = re.compile(
    r"""^\s*
        [-+]?\d+(?:\.\d+)?              # real1
        (?:[+-]\d+(?:\.\d+)?[ij])?      # optional imag1
        (?:,[-+]?\d+(?:\.\d+)?(?:[+-]\d+(?:\.\d+)?[ij])?)*   # ,real2(±imag2)...
        \s*$""",
    re.IGNORECASE | re.VERBOSE,
)


# ---------- Convenience pretty helpers ----------

def pretty_poly(coeffs: np.ndarray, var: str = "s") -> str:
    """Format polynomial coefficients as a compact plain text expression."""
    terms = []
    n = len(coeffs) - 1
    for i, a in enumerate(coeffs):
        p = n - i
        a = float(np.real_if_close(a))
        if p == 0:
            terms.append(f"{a:.6g}")
        elif p == 1:
            terms.append(f"{a:.6g}{var}")
        else:
            terms.append(f"{a:.6g}{var}^{p}")
    s = " + ".join(terms).replace("1" + var + "^", var + "^").replace("1" + var, var).replace("+ -", "- ")
    return s


def pole_multiplicities(poles: np.ndarray, tol: float = 0.0) -> Dict[float, int]:
    """Count repeated real pole values within a tolerance."""
    p_sorted = np.sort(np.real(np.real_if_close(poles)).astype(float))
    groups: Dict[float, int] = {}
    if p_sorted.size == 0:
        return groups
    ref = p_sorted[0]
    count = 1
    for v in p_sorted[1:]:
        if abs(v - ref) <= tol:
            count += 1
        else:
            groups[float(ref)] = count
            ref = v
            count = 1
    groups[float(ref)] = count
    return groups


def jitter_repeated_poles(poles: np.ndarray, eps: float) -> np.ndarray:
    """Spread repeated real poles by a small amount for pole placement."""
    p_sorted = np.sort(np.real(np.real_if_close(poles)).astype(float))
    idx_map: Dict[float, List[int]] = {}
    for i, v in enumerate(p_sorted):
        idx_map.setdefault(v, []).append(i)
    out = p_sorted.copy()
    for v, idxs in idx_map.items():
        if len(idxs) > 1:
            center = (len(idxs) - 1) / 2.0
            for k, ix in enumerate(idxs):
                out[ix] = v + (k - center) * eps
    return out
