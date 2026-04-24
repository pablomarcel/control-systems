from __future__ import annotations
from dataclasses import dataclass
import dataclasses as dc
from typing import Optional, Tuple, List, Dict, Any
import logging, os
import numpy as np

from .apis import RootLocusRequest, RootLocusBatchSpec
from .utils import make_logger, parse_list, safe_title_to_filename
from .core import L0Builder, tf_siso_arrays, poles_and_zeros, RootLocusEngine, KGridBuilder
from .overlays import SGridOverlay, ConstGainOverlay
from .plotting import PlotService
from .geometry import compute_bounds
from .io import OutputSpec, ensure_outdir


@dataclass(slots=True)
class RootLocusApp:
    out_dir: str = "out"
    log: logging.Logger = None

    def __post_init__(self):
        if self.log is None:
            self.log = make_logger(False)
        ensure_outdir(self.out_dir)

    # ---- helpers for K-grid parsing
    @staticmethod
    def _parse_kpos(x: Optional[str]) -> Optional[tuple[float, float, int, str]]:
        if not x:
            return None
        pr = [p.strip() for p in str(x).replace(";", ",").split(",") if p.strip() != ""]
        if len(pr) < 2:
            return None
        lo, hi = float(pr[0]), float(pr[1])
        N = int(pr[2]) if len(pr) >= 3 else 400
        mode = pr[3].lower() if len(pr) >= 4 else "log"
        if mode not in ("lin", "log"):
            mode = "log"
        return (lo, hi, N, mode)

    @staticmethod
    def _parse_kneg(x: Optional[str]) -> Optional[tuple[float, float]]:
        if not x:
            return None
        pr = [p.strip() for p in str(x).replace(";", ",").split(",") if p.strip() != ""]
        if len(pr) < 2:
            return None
        return (float(pr[0]), float(pr[1]))

    def _build_zgrid_overlay(self, req: RootLocusRequest) -> Optional[SGridOverlay]:
        zgrid = SGridOverlay.parse_grid_spec(req.zeta, ([0.1 * k for k in range(1, 10)] if req.sgrid else []))
        wgrid = SGridOverlay.parse_grid_spec(req.wn, ([0.5, 1.0, 2.0] if req.sgrid else []))
        if not zgrid and not wgrid:
            return None
        return SGridOverlay(zgrid, wgrid, label_zeta=req.label_zeta, label_wn=req.label_wn)

    def _build_cg_overlay(self, req: RootLocusRequest) -> Optional[ConstGainOverlay]:
        levelsK = parse_list(req.kgains) if req.cg else []
        levelsA = parse_list(req.cg_absL)
        if not levelsK and not levelsA:
            return None
        return ConstGainOverlay(levelsK, levelsA, req.cg_res)

    # ---- main run
    def run(self, req: RootLocusRequest, outs: OutputSpec) -> Dict[str, Any]:
        L0 = L0Builder().build(
            poles=req.poles, zeros=req.zeros, kgain=req.kgain,
            num=req.num, den=req.den,
            Gnum=req.Gnum, Gden=req.Gden, Hnum=req.Hnum, Hden=req.Hden,
            ssA=req.ssA, ssB=req.ssB, ssC=req.ssC, ssD=req.ssD, io=req.io
        )
        self.log.info(f"L0(s) = {L0}")
        num, den = tf_siso_arrays(L0)
        P, Z = poles_and_zeros(L0)
        self.log.info(f"Open-loop poles: {P}")
        self.log.info(f"Open-loop zeros: {Z}")

        K = KGridBuilder().build(num, den, Z, self._parse_kpos(req.kpos), self._parse_kneg(req.kneg), req.auto)
        R = RootLocusEngine().roots_over_K(num, den, K)
        self.log.info(f"K samples: {len(K)}; system order n={R.shape[1]}.")

        zgrid_overlay = self._build_zgrid_overlay(req)
        cg_overlay = self._build_cg_overlay(req)
        klabels = parse_list(req.klabels)

        title = req.title or "Root–Locus Pro"
        base = safe_title_to_filename(title)
        html = outs.html or f"{base}.html"
        png = outs.png
        csv = outs.csv

        html = os.path.join(self.out_dir, html)
        png = os.path.join(self.out_dir, png) if png else None
        csv = os.path.join(self.out_dir, csv) if csv else None

        PlotService(self.log).plot(
            L0, R, K, klabels,
            title, html, png, csv,
            zgrid_overlay, cg_overlay,
            req.arrows, req.arrow_every, req.arrow_scale,
            req.xlim, req.ylim
        )
        return {"title": title, "html": html, "png": png, "csv": csv}

    # ---- batch run
    def run_batch(self, batch: RootLocusBatchSpec) -> str:
        """Run a batch of cases and build a simple HTML index."""
        ensure_outdir(batch.outdir)

        # Only request fields belong in RootLocusRequest
        req_field_names = {f.name for f in dc.fields(RootLocusRequest)}
        summaries: List[Dict[str, Any]] = []

        cases = batch.cases or []
        for idx, case in enumerate(cases, 1):
            cfg: Dict[str, Any] = {**(batch.defaults or {}), **(case or {})}

            # slice request kwargs
            req_kwargs = {k: cfg.get(k) for k in req_field_names}
            if not req_kwargs.get("title"):
                req_kwargs["title"] = cfg.get("title") or f"Case {idx}"

            title = req_kwargs["title"]
            self.log.info(f"--- Case {idx}/{len(cases)}: {title} ---")

            # outputs (html/png/csv)
            html_name = cfg.get("html") or f"{safe_title_to_filename(title)}.html"
            outs = OutputSpec(
                out_dir=batch.outdir,
                html=html_name,
                png=cfg.get("png"),
                csv=cfg.get("csv"),
            )

            try:
                result = self.run(RootLocusRequest(**req_kwargs), outs)
                summaries.append(result)
            except Exception as e:
                self.log.error(f"Case failed: {e}")

        # write simple index
        report_name = batch.report or "root_locus_report.html"
        rpt_path = os.path.join(batch.outdir, report_name)
        lines = [
            "<html><head><meta charset='utf-8'><title>Root–Locus Report</title></head><body>",
            "<h1>Root–Locus Report</h1><ol>",
        ]
        for s in summaries:
            rel = os.path.relpath(s["html"], batch.outdir)
            lines.append(f"<li><a href='{rel}'>{s['title']}</a></li>")
        lines.append("</ol></body></html>")
        with open(rpt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.log.info(f"[saved] report -> {rpt_path}")
        return rpt_path
