# pidControllers/rootLocusTool/apis.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

from .design import RootLocusConfig, RootLocusDesigner, DesignPoint
from .io import plot_mpl, plot_plotly, export_json, export_csv


@dataclass(slots=True)
class RootLocusRequest:
    cfg: RootLocusConfig
    backend: str = "plotly"   # or "mpl"
    save: Optional[str] = None
    export_json_path: Optional[str] = None
    export_csv_path: Optional[str] = None
    analyze: bool = False
    settle: float = 0.02
    precision: int = 6


class RootLocusService:
    def run(self, req: RootLocusRequest) -> Dict[str, Any]:
        designer = RootLocusDesigner(req.cfg)

        # Build plant and run the design scan (no plotting here).
        Gp = designer.build_plant()
        points: List[DesignPoint] = designer.compute_scan(Gp)
        summary = RootLocusDesigner.summarize_a(points)

        # Choose design row near recommended/override a.
        a_rec = (
            req.cfg.a_override
            if (req.cfg.a_override is not None and req.cfg.a_override > 0)
            else summary.get("a_recommended")
        )
        s_row: Optional[DesignPoint] = None
        if points and a_rec is not None:
            s_row = min(points, key=lambda p: abs(p.a - a_rec))

        # Only do locus/plot-prep if we are actually saving a figure.
        a_plot = a_rec if a_rec is not None else (req.cfg.a_override if req.cfg.a_override else 0.65)
        xlim = ylim = None

        if req.save:
            L, branches, rays, xlim, ylim = designer.prepare_l_and_rays(Gp, a_plot)

            if req.backend == "mpl":
                s_star = complex(s_row.sigma, s_row.jw) if s_row else None
                plot_mpl(
                    L,
                    designer.zeta_list(),
                    rays,
                    s_star=s_star,
                    title=req.cfg.title,
                    xlim=xlim,
                    ylim=ylim,
                    save=req.save,
                )
            else:
                s_dict = None if s_row is None else dict(
                    zeta=s_row.zeta, omega=s_row.omega, a=s_row.a,
                    K=s_row.K, Kp=s_row.Kp, Ti=s_row.Ti, Td=s_row.Td,
                    sigma=s_row.sigma, jw=s_row.jw
                )
                plot_plotly(
                    L,
                    designer.zeta_list(),
                    rays,
                    s_row=s_dict,
                    title=req.cfg.title,
                    xlim=xlim,
                    ylim=ylim,
                    save=req.save,
                )

        # Optional analysis (headless-friendly).
        perf = None
        if req.analyze and s_row is not None:
            perf = designer.analyze_closed_loop(Gp, s_row.Kp, s_row.Ti, s_row.Td, settle=req.settle)

        # Exports
        json_path = csv_path = None
        if req.export_json_path:
            payload = dict(
                plant=str(Gp),
                zetas=designer.zeta_list(),
                omega=list(req.cfg.omega),
                summary=summary,
                a_used=a_plot,
                s_row=None if s_row is None else asdict(s_row),
                xlim=xlim,
                ylim=ylim,
                perf=perf,
            )
            json_path = export_json(req.export_json_path, payload)

        if req.export_csv_path and points:
            csv_path = export_csv(req.export_csv_path, points)

        # Final tiny report
        return dict(
            plant=str(Gp),
            a_plot=a_plot,
            summary=summary,
            s_row=None if s_row is None else asdict(s_row),
            json_path=json_path,
            csv_path=csv_path,
            xlim=xlim,
            ylim=ylim,
            analyzed=perf is not None,
        )
