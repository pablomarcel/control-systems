from __future__ import annotations
import numpy as np

def parse_mat(s: str | None) -> np.ndarray | None:
    if s is None:
        return None
    rows = [r.strip() for r in s.replace(",", " ").split(";")]
    data = []
    for r in rows:
        if not r:
            continue
        toks = [t for t in r.split() if t]
        data.append([complex(t.replace("i", "j")) for t in toks])
    M = np.array(data, dtype=complex)
    M = np.real_if_close(M, tol=1e8)
    return M

def _split_list_any(s: str) -> list[str]:
    parts: list[str] = []
    for chunk in s.split(","):
        parts.extend([t for t in chunk.strip().split() if t])
    return parts

def _expand_imag_coeffs(expr: str) -> str:
    e = expr.replace("sqrt", "np.sqrt").replace("i", "j")
    e = e.replace("j", "*1j").replace("**1j", "*1j")
    return e

def parse_poles_tokens(tokens: list[str]) -> np.ndarray:
    import numpy as np
    env = {"np": np}
    vals = []
    for t in tokens:
        try:
            v = eval(_expand_imag_coeffs(t), {"__builtins__": {}}, env)
        except Exception:
            v = complex(t.replace("i", "j"))
        vals.append(complex(v))
    return np.asarray(vals, dtype=complex)

def parse_poles_any(s: str) -> np.ndarray:
    return parse_poles_tokens(_split_list_any(s))
