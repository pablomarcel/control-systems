from __future__ import annotations
from dataclasses import dataclass
import logging
import numpy as np
import control as ct
from .utils import coeffs_from_tf, normalize_tf, clip_small, coerce_outputs_to_m_by_N

@dataclass
class ConversionResult:
    G: object | None = None       # ct.TransferFunction or transfer matrix
    SS: ct.StateSpace | None = None

class SystemConverter:
    """Core conversion object: TF↔SS and checks."""
    def tf_to_ss(self, num, den) -> ConversionResult:
        G = ct.TransferFunction(num, den)
        SS = ct.tf2ss(G)
        return ConversionResult(G=G, SS=SS)

    def ss_to_tf(self, A, B, C, D) -> ConversionResult:
        n = A.shape[0]
        if A.shape[1] != n:
            raise ValueError("A must be square (n x n).")
        if B.shape[0] != n:
            raise ValueError("B must have n rows.")
        if C.shape[1] != n:
            raise ValueError("C must have n columns.")
        if D.shape != (C.shape[0], B.shape[1]):
            raise ValueError("D must be (m x r) with m=C.rows and r=B.cols.")
        SS = ct.ss(A, B, C, D)
        G = ct.ss2tf(SS)
        return ConversionResult(G=G, SS=SS)

    def equivalent_siso(self, G1, G2, atol=1e-9) -> bool:
        n1, d1 = normalize_tf(*coeffs_from_tf(G1))
        n2, d2 = normalize_tf(*coeffs_from_tf(G2))
        return (np.allclose(n1, n2, atol=atol) and np.allclose(d1, d2, atol=atol))

class PrettyPrinter:
    def tf(self, G) -> str:
        try:
            m, r = G.noutputs, G.ninputs
        except AttributeError:
            try:
                m, r = G.shape
            except Exception:
                m, r = 1, 1
        out = []
        if m > 1 or r > 1:
            out.append("Transfer matrix G(s):")
            for i in range(m):
                for j in range(r):
                    gij = G[i, j]
                    num, den = normalize_tf(*coeffs_from_tf(gij))
                    num, den = clip_small(num), clip_small(den)
                    out.append(f"  G[{i+1},{j+1}](s) = ({np.array2string(num, precision=5)}) / ({np.array2string(den, precision=5)})")
            return "\n".join(out)
        num, den = normalize_tf(*coeffs_from_tf(G))
        num, den = clip_small(num), clip_small(den)
        out.append("Transfer function G(s):")
        out.append(f"  num: {np.array2string(num, precision=5)}")
        out.append(f"  den: {np.array2string(den, precision=5)}")
        return "\n".join(out)

    def sympy_tf(self, G) -> str:
        try:
            import sympy as sp
            s = sp.symbols('s')
            num, den = normalize_tf(*coeffs_from_tf(G))
            num, den = clip_small(num), clip_small(den)
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
            return str(sp.simplify(pnum/pden))
        except Exception as e:
            return f"(SymPy pretty print unavailable: {e})"

class Plotter:
    def __init__(self, backend: str = "Agg"):
        import matplotlib
        try:
            matplotlib.use(backend)
        except Exception:
            pass
        import matplotlib.pyplot as plt
        self.plt = plt

    def step_tf(self, G, tfinal=8.0, dt=1e-3, title="Step response (TF)", save=None, show=False):
        import numpy as np
        T = np.arange(0, tfinal + dt, dt)
        T, y = ct.step_response(G, T=T)
        y = np.ravel(np.asarray(y))
        fig = self.plt.figure(figsize=(8, 4.5))
        self.plt.plot(T, y)
        self.plt.title(title); self.plt.xlabel("Time (s)"); self.plt.ylabel("y(t)"); self.plt.grid(True)
        self.plt.tight_layout()
        if save:
            fig.savefig(save, dpi=150)
        if show:
            self.plt.show()
        self.plt.close(fig)

    def step_ss(self, SS, iu=0, tfinal=8.0, dt=1e-3, title="Step response (SS)", save=None, show=False):
        import numpy as np
        if not (0 <= iu < SS.ninputs):
            raise ValueError(f"--iu out of range: got {iu}, but system has {SS.ninputs} inputs")
        T = np.arange(0, tfinal + dt, dt)
        T, Y = ct.step_response(SS, T=T, input=iu)
        Y = coerce_outputs_to_m_by_N(Y, N_time=T.size)
        fig = self.plt.figure(figsize=(8, 4.5))
        for k in range(Y.shape[0]):
            self.plt.plot(T, np.ravel(Y[k, :]), label=f"y{k+1}")
        self.plt.title(f"{title}  [input u{iu+1}]"); self.plt.xlabel("Time (s)"); self.plt.ylabel("Output")
        self.plt.grid(True); self.plt.legend(); self.plt.tight_layout()
        if save:
            fig.savefig(save, dpi=150)
        if show:
            self.plt.show()
        self.plt.close(fig)
