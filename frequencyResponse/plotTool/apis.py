from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple
import numpy as np
import control as ct

from .app import PlotToolApp
from .design import build_L_from_args, tf_arrays
from .core import make_grid, compute_margins, closedloop_metrics, nyq_encirclements, CLMetrics, Margins, nichols_defaults
from .io import ensure_dir, save_json
from .utils import parse_csv_vals, parse_range4

@dataclass(slots=True)
class PlotRequest:
    bode: bool = False
    nyquist: bool = False
    nichols: bool = False
    nichols_grid: bool = False
    nichols_closedloop: bool = False
    plotly: bool = False
    nyq_markers: bool = False
    nyq_samples: int = 0
    wmin: float | None = None
    wmax: float | None = None
    npts: int = 400
    wmarks: Optional[List[float]] = None
    nichols_range: Optional[Tuple[float,float,float,float]] = None
    nichols_Mdb: Optional[Sequence[float]] = None
    nichols_Ndeg: Optional[Sequence[float]] = None
    nichols_no_grid_labels: bool = False
    save_png_dir: Optional[str] = None
    save_html_base: Optional[str] = None
    save_json_path: Optional[str] = None
    title: str = "Frequency Response"

class PlotService:
    def __init__(self, app: PlotToolApp):
        self.app = app
        self.log = app.logger()
        self.debug = bool(os.environ.get("PLOTTOOL_DEBUG", ""))
        self.debug = bool(os.environ.get("PLOTTOOL_DEBUG", ""))

    def _fname(self, base: Optional[str], stub: str, suffix: str, chan_idx: int, total: int):
        if not base: return None
        base_noext = base.rsplit(".", 1)[0]
        tail = f"_{stub}{'' if total==1 else f'_c{chan_idx+1}'}"
        return f"{base_noext}{tail}.{suffix}"

    def run_channel(self, idx: int, total: int, args, L: ct.TransferFunction, w: np.ndarray, name: str, req: PlotRequest):
        margins: Margins = compute_margins(L, w)
        cl: CLMetrics = closedloop_metrics(L, w)
        P = int(np.sum(np.real(np.roots(tf_arrays(L)[1])) > 1e-12))
        try: N = nyq_encirclements(L, w)
        except Exception: N = 0
        Z = N + P

        print("\n== Channel Summary ==")
        if self.debug:
            print("[plotTool DEBUG] Running channel", idx+1, "of", total, "name=", name)
            print("[plotTool DEBUG] w[0], w[-1], npts:", float(w[0]), float(w[-1]), len(w))
        if self.debug:
            print("[plotTool DEBUG] Running channel", idx+1, "of", total, "name=", name)
            print("[plotTool DEBUG] w range:", (float(w[0]), float(w[-1])), "npts=", len(w))
        if total > 1: print(f"Channel: {name}")
        num, den = tf_arrays(L)
        def _poly_str(c):
            s=""; N=len(c)
            for k,ck in enumerate(c):
                p=N-1-k
                if abs(ck)<1e-14: continue
                sign = " + " if ck>=0 and s else (" - " if ck<0 and s else ("-" if ck<0 else ""))
                mag=abs(ck)
                if p==0: term=f"{mag:.6g}"
                elif p==1: term=("" if abs(mag-1)<1e-12 else f"{mag:.6g}")+"s"
                else: term=("" if abs(mag-1)<1e-12 else f"{mag:.6g}")+f"s^{p}"
                s+=sign+term
            return s or "0"
        print(f"L(s) = ({_poly_str(num)}) / ({_poly_str(den)})")
        print(f"Gain margin      : {margins.gm:.6g} ({margins.gm_db:.3g} dB) at w_pc = {margins.wpc:.6g}")
        print(f"Phase margin     : {margins.pm:.6g} deg at w_gc = {margins.wgc:.6g}")
        from .core import static_constants
        Kp,Kv,Ka = static_constants(L)
        print(f"Static constants : Kp={Kp}  Kv={Kv}  Ka={Ka}")
        print(f"Nyquist counts   : P={P}, N={N} ⇒ Z={Z}  → {'UNSTABLE' if Z>0 else 'stable'}")
        print(f"Closed-loop Mr   : {cl.Mr_db:.3g} dB at w_r = {cl.wr:.6g};  w_bw ≈ {cl.wb:.6g}")

        # Resolve Nichols lists
        Mdef, Ndef = nichols_defaults()
        m_levels = req.nichols_Mdb if (req.nichols_Mdb and len(req.nichols_Mdb)>0) else Mdef
        n_levels = req.nichols_Ndeg if (req.nichols_Ndeg and len(req.nichols_Ndeg)>0) else Ndef

        # Build filenames
        png = lambda stub: (None if not req.save_png_dir else os.path.join(req.save_png_dir, f"{stub}{'' if total==1 else f'_c{idx+1}'}.png"))
        html = lambda stub: self._fname(req.save_html_base, stub, "html", idx, total)

        # Renders
        if req.bode:
            try:
                if req.plotly:
                    from .tools.plotting_plotly import bode_plot as bode_p
                    bode_p(L, w, margins, req.title if total==1 else f"{req.title} — {name}", False, False, html("bode"), req.wmarks)
                else:
                    from .tools.plotting_mpl import bode_plot as bode_m
                    bode_m(L, w, margins, req.title if total==1 else f"{req.title} — {name}", False, False, png("bode"), req.wmarks)
            except Exception as e:
                self.log.error("Bode plot failed: %s", e)

        if req.nyquist:
            try:
                if req.plotly:
                    from .tools.plotting_plotly import nyquist_plot as nyq_p
                    nyq_p(L, w, req.title if total==1 else f"{req.title} — {name}", req.nyq_markers, req.nyq_samples, html("nyquist"))
                else:
                    from .tools.plotting_mpl import nyquist_plot as nyq_m
                    nyq_m(L, w, req.title if total==1 else f"{req.title} — {name}", req.nyq_markers, png("nyquist"))
            except Exception as e:
                self.log.error("Nyquist plot failed: %s", e)

        if req.nichols:
            try:
                if req.plotly:
                    from .tools.plotting_plotly import nichols_plot as nich_p
                    nich_p(L, w, margins, cl, req.title if total==1 else f"{req.title} — {name}",
                           req.nichols_grid, req.nichols_closedloop, html("nichols"), req.nichols_range,
                           m_levels, n_levels, (not req.nichols_no_grid_labels))
                else:
                    from .tools.plotting_mpl import nichols_plot as nich_m
                    nich_m(L, w, margins, cl, req.title if total==1 else f"{req.title} — {name}",
                           req.nichols_grid, req.nichols_closedloop, png("nichols"), req.nichols_range,
                           m_levels, n_levels)
            except Exception as e:
                self.log.error("Nichols plot failed: %s", e)

        payload = dict(
            L=dict(num=tf_arrays(L)[0].tolist(), den=tf_arrays(L)[1].tolist()),
            margins=dict(gm=margins.gm, gm_db=margins.gm_db, pm=margins.pm, wgc=margins.wgc, wpc=margins.wpc),
            closedloop=dict(Mr_db=cl.Mr_db, wr=cl.wr, wb=cl.wb)
        )
        return payload

    def run(self, args, req: PlotRequest) -> Dict[str, Any]:
        Ls, names = build_L_from_args(args)
        report: Dict[str, Any] = {}
        ensure_dir(self.app.io.out_dir)
        for idx, (L, nm) in enumerate(zip(Ls, names)):
            w = make_grid(L, req.wmin, req.wmax, req.npts)
            payload = self.run_channel(idx, len(Ls), args, L, w, nm, req)
            report[nm] = payload
        if req.save_json_path:
            save_json(req.save_json_path, report)
        return report
