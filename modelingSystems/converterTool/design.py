
from __future__ import annotations
from dataclasses import dataclass
import logging
import numpy as np
import control as ct
import matplotlib.pyplot as plt
from .utils import clip_small

def pretty_tf_any(G) -> str:
    try:
        m, r = G.noutputs, G.ninputs
    except AttributeError:
        try:
            m, r = G.shape
        except Exception:
            m, r = 1, 1

    lines = []
    if m > 1 or r > 1:
        lines.append("Transfer matrix G(s):")
        for i in range(m):
            for j in range(r):
                gij = G[i, j]
                num, den = ConverterPretty.coeffs(gij)
                num, den = clip_small(num), clip_small(den)
                lines.append(f"  G[{i+1},{j+1}](s) = ({np.array2string(num, precision=5)}) / ({np.array2string(den, precision=5)})")
    else:
        num, den = ConverterPretty.coeffs(G)
        num, den = clip_small(num), clip_small(den)
        lines.append("Transfer function G(s):")
        lines.append(f"  num: {np.array2string(num, precision=5)}")
        lines.append(f"  den: {np.array2string(den, precision=5)}")
    return "\n".join(lines)

class ConverterPretty:
    @staticmethod
    def coeffs(G):
        try:
            num, den = ct.tfdata(G, squeeze=True)
        except TypeError:
            num, den = ct.tfdata(G)
            def _flat(a):
                while isinstance(a, (list, tuple)) and len(a) > 0:
                    a = a[0]
                return a
            num, den = _flat(num), _flat(den)
        return np.asarray(num, float).ravel(), np.asarray(den, float).ravel()

    @staticmethod
    def sympy_rat(G) -> str:
        try:
            import sympy as sp
            s = sp.symbols('s')
            num, den = ConverterPretty.coeffs(G)
            def rat(c):
                try:
                    return sp.nsimplify(c, rational=True, tolerance=1e-12)
                except TypeError:
                    return sp.nsimplify(c, rational=True)
            pnum = sum(rat(c)*s**k for k, c in enumerate(num[::-1]))
            pden = sum(rat(c)*s**k for k, c in enumerate(den[::-1]))
            try:
                lc = sp.LC(sp.Poly(pden, s))
                pnum, pden = sp.simplify(pnum/lc), sp.simplify(pden/lc)
            except Exception:
                pass
            return sp.sstr(sp.simplify(pnum/pden))
        except Exception as e:
            logging.debug("SymPy not available or failed: %s", e)
            return ""

def plot_step_tf(G, tfinal=8.0, dt=1e-3, title="Step response (TF)") -> None:
    T = np.arange(0, tfinal + dt, dt)
    T, y = ct.step_response(G, T=T)
    y = np.ravel(np.asarray(y))
    plt.figure(figsize=(8, 4.5))
    plt.plot(T, y)
    plt.title(title); plt.xlabel("Time (s)"); plt.ylabel("y(t)")
    plt.grid(True); plt.tight_layout(); plt.show()

def _coerce_outputs_to_m_by_N(Y, N_time) -> np.ndarray:
    Y = np.asarray(Y)
    Y = np.squeeze(Y)
    if Y.ndim == 1:
        Y = Y.reshape(1, -1)
    elif Y.ndim == 2:
        if Y.shape[0] == N_time:
            Y = Y.T
    elif Y.ndim == 3:
        if Y.shape[-1] == N_time:
            if Y.shape[1] == 1: Y = Y[:,0,:]
            elif Y.shape[0] == 1: Y = Y[0,:,:]
        else:
            Y = np.squeeze(Y)
            if Y.ndim == 2 and Y.shape[0] == N_time: Y = Y.T
    else:
        Y = Y.reshape(Y.shape[0], -1)
    return Y

def plot_step_ss(ssys, iu=0, tfinal=8.0, dt=1e-3, title="Step response (SS)") -> None:
    if not (0 <= iu < ssys.ninputs):
        raise ValueError(f"--iu out of range: got {iu}, but system has {ssys.ninputs} inputs")
    T = np.arange(0, tfinal + dt, dt)
    T, Y = ct.step_response(ssys, T=T, input=iu)
    Y = _coerce_outputs_to_m_by_N(Y, N_time=T.size)
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 4.5))
    for k in range(Y.shape[0]):
        plt.plot(T, np.ravel(Y[k, :]), label=f"y{k+1}")
    plt.title(f"{title}  [input u{iu+1}]"); plt.xlabel("Time (s)"); plt.ylabel("Output")
    plt.grid(True); plt.legend(); plt.tight_layout(); plt.show()
