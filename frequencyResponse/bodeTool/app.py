from __future__ import annotations
from typing import List
import os, json
import numpy as np
import control as ct

from .utils import build_logger, tf_arrays, pretty_tf
from .core import TFBuilder, FrequencyGrid, Analyzer
from .design import BodePlotter, ClassicalPlotters
from .apis import BodeConfig, AnalysisResult

IN_DIR = os.path.join(os.path.dirname(__file__), "in")
OUT_DIR = os.path.join(os.path.dirname(__file__), "out")

class BodeApp:
    def __init__(self, *, level="INFO"):
        self.log = build_logger(level=level)

    def run(self, cfg: BodeConfig) -> AnalysisResult:
        tfb = TFBuilder()
        G = tfb.build_from_modes(cfg.num, cfg.den, cfg.gain, cfg.zeros, cfg.poles,
                                 cfg.fnum, cfg.fden, cfg.K)
        h_mode_count = sum([
            1 if (cfg.hnum or cfg.hden) else 0,
            1 if ((cfg.hgain is not None) or (cfg.hzeros is not None) or (cfg.hpoles is not None)) else 0,
            1 if (cfg.hfnum or cfg.hfden) else 0,
        ])
        if h_mode_count == 0:
            H = ct.tf([1],[1])
        elif h_mode_count == 1:
            H = tfb.build_from_modes(cfg.hnum, cfg.hden, cfg.hgain, cfg.hzeros, cfg.hpoles,
                                     cfg.hfnum, cfg.hfden, cfg.hK)
        else:
            raise ValueError("Specify at most ONE input mode for H(s).")

        L = ct.minreal(G*H, verbose=False)

        grid = FrequencyGrid()
        w = grid.make(L, cfg.wmin, cfg.wmax, cfg.npts)

        analyzer = Analyzer()
        margins = analyzer.compute_margins(L, w)
        cl = analyzer.closedloop_metrics(L, w)

        poles = np.roots(tf_arrays(L)[1])
        P = int(np.sum(np.real(poles) > 1e-12))
        hints: List[str] = []
        hints.append(f"Open-loop RHP poles P = {P}.")
        if np.isfinite(margins.pm) and np.isfinite(margins.gm) and margins.gm>1.0 and margins.pm>0.0 and P==0:
            hints.append("PM>0 and GM>1 with P=0 ⇒ closed-loop likely stable (unity FB, minimum-phase assumption).")
        else:
            hints.append("Margins not strictly positive and/or P>0 — check Nyquist for certainty.")
        try:
            N = analyzer.nyq_encirclements(L, w)
            hints.append(f"Coarse Nyquist encirclements of -1+j0: N = {N}. Closed-loop RHP zeros Z = N + P.")
        except Exception as e:
            hints.append(f"Nyquist encirclement estimate unavailable: {e}")

        return AnalysisResult(pretty_tf=pretty_tf(L), margins=margins, closedloop=cl, P=P, hints=hints)

    def render(self, cfg: BodeConfig, result: AnalysisResult, L=None, w=None):
        if cfg.bode or cfg.nyquist or cfg.nichols or cfg.step or cfg.save_json:
            tfb = TFBuilder()
            import control as ct, numpy as np
            G = tfb.build_from_modes(cfg.num, cfg.den, cfg.gain, cfg.zeros, cfg.poles,
                                     cfg.fnum, cfg.fden, cfg.K)
            h_mode_count = sum([
                1 if (cfg.hnum or cfg.hden) else 0,
                1 if ((cfg.hgain is not None) or (cfg.hzeros is not None) or (cfg.hpoles is not None)) else 0,
                1 if (cfg.hfnum or cfg.hfden) else 0,
            ])
            if h_mode_count == 0:
                H = ct.tf([1],[1])
            elif h_mode_count == 1:
                H = tfb.build_from_modes(cfg.hnum, cfg.hden, cfg.hgain, cfg.hzeros, cfg.hpoles,
                                         cfg.hfnum, cfg.hfden, cfg.hK)
            else:
                raise ValueError("Specify at most ONE input mode for H(s).")
            L = ct.minreal(G*H, verbose=False)
            grid = FrequencyGrid()
            w = grid.make(L, cfg.wmin, cfg.wmax, cfg.npts)

        def _png(name: str) -> str | None:
            if not cfg.save_png: return None
            if cfg.save_png.lower().endswith(".png"):
                return cfg.save_png if name == "bode" else None
            os.makedirs(cfg.save_png, exist_ok=True)
            return os.path.join(cfg.save_png, f"{name}.png")

        if cfg.bode:
            bp = BodePlotter()
            if cfg.plotly:
                try:
                    bp.plotly(L, w, result.margins, cfg.title, cfg.save_html)
                except Exception:
                    bp.matplotlib(L, w, result.margins, cfg.title, _png("bode"))
            else:
                bp.matplotlib(L, w, result.margins, cfg.title, _png("bode"))

        if cfg.nyquist:
            ClassicalPlotters().nyquist_matplotlib(L, w, _png("nyquist"))
        if cfg.nichols:
            ClassicalPlotters().nichols_matplotlib(L, w, _png("nichols"))
        if cfg.step:
            import matplotlib
            import platform
            _backend = (matplotlib.get_backend() or "").lower()
            if _backend in {"agg","pdf","svg","template","cairo"}:
                try:
                    if platform.system() == "Darwin":
                        matplotlib.use("MacOSX", force=True)
                    else:
                        matplotlib.use("TkAgg", force=True)
                except Exception:
                    pass
            import matplotlib.pyplot as plt
            T = ct.minreal(ct.feedback(L, 1), verbose=False)
            t, y = ct.step_response(T)
            fig, ax = plt.subplots(1,1, figsize=(6.4,3.2))
            ax.plot(t, y, lw=2); ax.grid(True, ls=":")
            ax.set_xlabel("t (s)"); ax.set_ylabel("y(t)")
            ax.set_title("Closed-loop step response")
            pth = _png("step")
            if pth: fig.savefig(pth, dpi=150)
            plt.show()

        if cfg.save_json:
            payload = dict(
                L=result.pretty_tf,
                margins=dict(gm=result.margins.gm, gm_db=result.margins.gm_db,
                             pm=result.margins.pm, wgc=result.margins.wgc, wpc=result.margins.wpc),
                closedloop=dict(Mr_db=result.closedloop.Mr_db, wr=result.closedloop.wr, wb=result.closedloop.wb),
                P=int(result.P), hints=result.hints
            )
            with open(cfg.save_json, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
