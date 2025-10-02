from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from pathlib import Path
import os
import numpy as np
import control as ct

from .app import PlotToolApp
from .design import build_L_from_args, tf_arrays
from .core import (
    make_grid, compute_margins, closedloop_metrics, nyq_encirclements,
    CLMetrics, Margins, nichols_defaults
)
from .io import ensure_dir, save_json
from .utils import parse_csv_vals, parse_range4, build_logger

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
    # “Computed”/derived fields (CLI normally sets these)
    save_png_dir: Optional[str] = None
    save_html_base: Optional[str] = None
    save_json_path: Optional[str] = None
    title: str = "Frequency Response"

def _truthy_env(name: str) -> bool:
    v = os.environ.get(name, "")
    return str(v).strip().lower() in ("1", "true", "yes", "on")

class PlotService:
    def __init__(self, app: PlotToolApp):
        self.app = app
        self.log = app.logger()
        self.debug = _truthy_env("PLOTTOOL_DEBUG")

    # ------------------- normalization helpers -------------------
    def _get(self, obj: Any, name: str, default: Any = None) -> Any:
        """Read attribute or dict key from arbitrary req-like object."""
        if hasattr(obj, name):
            return getattr(obj, name)
        if isinstance(obj, dict) and name in obj:
            return obj[name]
        return default

    def _coerce_req(self, req_like: Any) -> PlotRequest:
        """
        Turn any req-like object (SimpleNamespace, dict, PlotRequest, argparse Namespace)
        into a fully-populated PlotRequest, including derived path fields.
        """
        if isinstance(req_like, PlotRequest):
            req = req_like
        else:
            req = PlotRequest(
                bode               = bool(self._get(req_like, "bode", False)),
                nyquist            = bool(self._get(req_like, "nyquist", False)),
                nichols            = bool(self._get(req_like, "nichols", False)),
                nichols_grid       = bool(self._get(req_like, "nichols_grid", False)),
                nichols_closedloop = bool(self._get(req_like, "nichols_closedloop", False)),
                plotly             = bool(self._get(req_like, "plotly", False)),
                nyq_markers        = bool(self._get(req_like, "nyq_markers", False)),
                nyq_samples        = int(self._get(req_like, "nyq_samples", 0) or 0),
                wmin               = self._get(req_like, "wmin", None),
                wmax               = self._get(req_like, "wmax", None),
                npts               = int(self._get(req_like, "npts", 400) or 400),
                wmarks             = self._get(req_like, "wmarks", None),
                nichols_range      = parse_range4(self._get(req_like, "nichols_range", None)),
                nichols_Mdb        = self._get(req_like, "nichols_Mdb", None) or parse_csv_vals(self._get(req_like, "nichols_Mdb_csv", None)),
                nichols_Ndeg       = self._get(req_like, "nichols_Ndeg", None) or parse_csv_vals(self._get(req_like, "nichols_Ndeg_csv", None)),
                nichols_no_grid_labels = bool(self._get(req_like, "nichols_no_grid_labels", False)),
                title              = str(self._get(req_like, "title", "Frequency Response")),
            )

        # Derive computed path fields from multiple possible input names
        save_png_dir   = self._get(req_like, "save_png_dir", None) or self._get(req_like, "save_png", None)
        save_html_base = self._get(req_like, "save_html_base", None) or self._get(req_like, "save_html_dir", None) or self._get(req_like, "save_html", None)
        save_json_path = self._get(req_like, "save_json_path", None) or self._get(req_like, "save_json", None)

        req.save_png_dir   = save_png_dir
        req.save_html_base = save_html_base
        req.save_json_path = save_json_path

        # Ensure directories if provided
        for d in (req.save_png_dir, req.save_html_base):
            if isinstance(d, str) and d:
                Path(d).mkdir(parents=True, exist_ok=True)

        return req

    def _fname(self, base: Optional[str], stub: str, suffix: str, chan_idx: int, total: int):
        if not base:
            return None
        base_noext = base.rsplit(".", 1)[0]
        tail = f"_{stub}{'' if total == 1 else f'_c{chan_idx+1}'}"
        return f"{base_noext}{tail}.{suffix}"

    # ------------------- per-channel work -------------------
    def run_channel(self, idx: int, total: int, args_any: Any, L: ct.TransferFunction, w: np.ndarray, name: str, req: PlotRequest):
        margins: Margins = compute_margins(L, w)
        cl: CLMetrics = closedloop_metrics(L, w)

        # crude count of open-loop RHP poles for Nyquist
        P = int(np.sum(np.real(np.roots(tf_arrays(L)[1])) > 1e-12))
        try:
            N = nyq_encirclements(L, w)
        except Exception:
            N = 0
        Z = N + P

        print("\n== Channel Summary ==")
        if self.debug:
            print("[plotTool DEBUG] Running channel", idx+1, "of", total, "name=", name)
            print("[plotTool DEBUG] w[0], w[-1], npts:", float(w[0]), float(w[-1]), len(w))
            print("[plotTool DEBUG] w range:", (float(w[0]), float(w[-1])), "npts=", len(w))
        if total > 1:
            print(f"Channel: {name}")

        num, den = tf_arrays(L)

        def _poly_str(c):
            s = ""
            Np = len(c)
            for k, ck in enumerate(c):
                p = Np - 1 - k
                if abs(ck) < 1e-14:
                    continue
                sign = " + " if ck >= 0 and s else (" - " if ck < 0 and s else ("-" if ck < 0 else ""))
                mag = abs(ck)
                if p == 0:
                    term = f"{mag:.6g}"
                elif p == 1:
                    term = ("" if abs(mag - 1) < 1e-12 else f"{mag:.6g}") + "s"
                else:
                    term = ("" if abs(mag - 1) < 1e-12 else f"{mag:.6g}") + f"s^{p}"
                s += sign + term
            return s or "0"

        print(f"L(s) = ({_poly_str(num)}) / ({_poly_str(den)})")
        print(f"Gain margin      : {margins.gm:.6g} ({margins.gm_db:.3g} dB) at w_pc = {margins.wpc:.6g}")
        print(f"Phase margin     : {margins.pm:.6g} deg at w_gc = {margins.wgc:.6g}")
        from .core import static_constants
        Kp, Kv, Ka = static_constants(L)
        print(f"Static constants : Kp={Kp}  Kv={Kv}  Ka={Ka}")
        print(f"Nyquist counts   : P={P}, N={N} ⇒ Z={Z}  → {'UNSTABLE' if Z>0 else 'stable'}")
        print(f"Closed-loop Mr   : {cl.Mr_db:.3g} dB at w_r = {cl.wr:.6g};  w_bw ≈ {cl.wb:.6g}")

        # Resolve Nichols lists
        Mdef, Ndef = nichols_defaults()
        m_levels = req.nichols_Mdb if (req.nichols_Mdb and len(req.nichols_Mdb) > 0) else Mdef
        n_levels = req.nichols_Ndeg if (req.nichols_Ndeg and len(req.nichols_Ndeg) > 0) else Ndef

        # Build filenames
        png  = lambda stub: (None if not req.save_png_dir   else os.path.join(req.save_png_dir,   f"{stub}{'' if total==1 else f'_c{idx+1}'}.png"))
        html = lambda stub: self._fname(req.save_html_base, stub, "html", idx, total)

        # Renders
        if req.bode:
            try:
                if req.plotly:
                    from .tools.plotting_plotly import bode_plot as bode_p
                    bode_p(L, w, margins, req.title if total == 1 else f"{req.title} — {name}", False, False, html("bode"), req.wmarks)
                else:
                    from .tools.plotting_mpl import bode_plot as bode_m
                    bode_m(L, w, margins, req.title if total == 1 else f"{req.title} — {name}", False, False, png("bode"), req.wmarks)
            except Exception as e:
                self.log.error("Bode plot failed: %s", e)

        if req.nyquist:
            try:
                if req.plotly:
                    from .tools.plotting_plotly import nyquist_plot as nyq_p
                    nyq_p(L, w, req.title if total == 1 else f"{req.title} — {name}", req.nyq_markers, req.nyq_samples, html("nyquist"))
                else:
                    from .tools.plotting_mpl import nyquist_plot as nyq_m
                    nyq_m(L, w, req.title if total == 1 else f"{req.title} — {name}", req.nyq_markers, png("nyquist"))
            except Exception as e:
                self.log.error("Nyquist plot failed: %s", e)

        if req.nichols:
            try:
                if req.plotly:
                    from .tools.plotting_plotly import nichols_plot as nich_p
                    nich_p(L, w, margins, cl, req.title if total == 1 else f"{req.title} — {name}",
                           req.nichols_grid, req.nichols_closedloop, html("nichols"), req.nichols_range,
                           m_levels, n_levels, (not req.nichols_no_grid_labels))
                else:
                    from .tools.plotting_mpl import nichols_plot as nich_m
                    nich_m(L, w, margins, cl, req.title if total == 1 else f"{req.title} — {name}",
                           req.nichols_grid, req.nichols_closedloop, png("nichols"), req.nichols_range,
                           m_levels, n_levels)
            except Exception as e:
                self.log.error("Nichols plot failed: %s", e)

        payload = dict(
            L=dict(num=tf_arrays(L)[0].tolist(), den=tf_arrays(L)[1].tolist()),
            margins=dict(gm=margins.gm, gm_db=margins.gm_db, pm=margins.pm, wgc=margins.wgc, wpc=margins.wpc),
            closedloop=dict(Mr_db=cl.Mr_db, wr=cl.wr, wb=cl.wb),
        )
        return payload

    # ------------------- public API -------------------
    def run(self, args, req_like: Any) -> Dict[str, Any]:
        """
        args: plant/model spec (num/den, gain/zeros/poles, or fnum/fden/K; possibly A,B,C,D)
        req_like: anything that describes plotting request (PlotRequest, SimpleNamespace, dict, argparse.Namespace)
        """
        # Normalize request
        req = self._coerce_req(req_like)

        # Build plant channels
        Ls, names = build_L_from_args(args)

        # Ensure root out_dir exists (for parity with CLI behavior)
        ensure_dir(self.app.io.out_dir)

        report: Dict[str, Any] = {}
        for idx, (L, nm) in enumerate(zip(Ls, names)):
            w = make_grid(L, req.wmin, req.wmax, req.npts)
            payload = self.run_channel(idx, len(Ls), args, L, w, nm, req)
            report[nm] = payload

        # Optional JSON summary
        if req.save_json_path:
            save_json(req.save_json_path, report)
        return report
