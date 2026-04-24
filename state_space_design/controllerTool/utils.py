# -*- coding: utf-8 -*-
"""
Utility helpers for parsing, math snippets, and transfer-function evaluation.
Kept dependency-light for easy testing.
"""
from __future__ import annotations
from typing import Tuple
import numpy as np
import control as ct

def parse_real_vec(s: str) -> np.ndarray:
    return np.array([float(x) for x in s.replace(",", " ").split()], float)

def parse_complex_list(s: str) -> np.ndarray:
    out = []
    for w in s.replace(",", " ").split():
        w = w.replace("i", "j").replace("I", "j")
        val = complex(eval(w, {"__builtins__": {}}, {}))
        out.append(val)
    return np.array(out, dtype=complex)

def array2str(M: np.ndarray, p: int = 6) -> str:
    A = np.real_if_close(M, 1e8)
    return np.array2string(np.asarray(A, float), precision=p, suppress_small=True)

def mat_inline(M: np.ndarray, precision: int = 4) -> str:
    M = np.atleast_2d(np.asarray(np.real_if_close(M, 1e8), float))
    rows = [" ".join(f"{float(v):.{precision}g}" for v in row) for row in M]
    return "[[" + "]; ".join(rows) + "]]"

def poly_from_roots(roots: np.ndarray) -> np.ndarray:
    return np.real_if_close(np.poly(roots), 1e8).astype(float)

def phi_of_A(A: np.ndarray, coeff: np.ndarray) -> np.ndarray:
    r = len(coeff) - 1
    out = np.linalg.matrix_power(A, r)
    for k in range(1, r):
        out += coeff[k] * np.linalg.matrix_power(A, r - k)
    out += coeff[-1] * np.eye(A.shape[0])
    return out

def tf_coeffs(tf: ct.TransferFunction) -> tuple[np.ndarray, np.ndarray]:
    num = np.atleast_1d(np.squeeze(np.array(tf.num[0][0], float)))
    den = np.atleast_1d(np.squeeze(np.array(tf.den[0][0], float)))
    return num, den

def tf_eval_jw(tf: ct.TransferFunction, w: np.ndarray) -> np.ndarray:
    num, den = tf_coeffs(tf)
    s = 1j * w
    return np.polyval(num, s) / np.polyval(den, s)

def bode_data(tf: ct.TransferFunction, w: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    H = tf_eval_jw(tf, w)
    mag_db = 20 * np.log10(np.maximum(np.abs(H), 1e-16))
    phase_deg = np.unwrap(np.angle(H)) * 180 / np.pi
    return mag_db, phase_deg
