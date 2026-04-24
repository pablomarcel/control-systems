from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict
try:
    import control as ct
except Exception:  # pragma: no cover
    ct = None

from .core import pretty_tf, margins_report, controller_tf
from .core import Requirements
from .design import make_grids, search_candidates
from .io import export_results
from .utils import ensure_out_dir

class PIDDesignerApp:
    """High-level orchestrator for PID design runs."""
    def __init__(self, out_dir: str | None = None):
        self.out_dir = ensure_out_dir(out_dir)

    def run(self, *, Gp: "ct.TransferFunction", structure: str,
            req: Requirements, grids: Dict[str, List[float]],
            objective: str, weights: Tuple[float, float, float, float],
            tfinal: Optional[float], dt: Optional[float],
            backend: str, plot_top: int, save_prefix: str,
            export_json: bool, export_csv: bool):

        print("\n" + "="*78)
        print("Plant / Controller / Open Loop")
        print("="*78)
        print(pretty_tf("Plant Gp(s)", Gp))

        print("\n" + "="*78)
        print("Grid Search")
        print("="*78)
        gs = {k: (len(v), (float(v[0]), float(v[-1]))) for k, v in grids.items()}
        print(f"Structure: {structure}")
        print(f"Grids: {gs}")
        print(f"Requirements: {req}")
        print(f"Objective: {objective} (w_ts={weights[0]}, w_mp={weights[1]}, w_itae={weights[2]}, w_ise={weights[3]})")

        cands = search_candidates(Gp=Gp, structure=structure, grids=grids, req=req,
                                  tfinal=tfinal, dt=dt, objective=objective, wts=weights)
        if not cands:
            print("\n[RESULT] No candidate satisfied the constraints. Relax constraints or widen ranges.")
            return 0

        best = cands[0]
        Gc_best = controller_tf(structure, best.params)
        L_best = Gc_best * Gp

        print("\n" + "="*78)
        print("Best Candidate")
        print("="*78)
        print(pretty_tf("Controller Gc(s)", Gc_best))
        print(pretty_tf("Open loop L(s)=Gc*Gp", L_best))
        print("\nOpen-loop margins:\n" + margins_report(L_best))

        m = best.metrics
        print("\nStep metrics (unit step):")
        print(f"  Overshoot           : {m.overshoot:.4g} %")
        print(f"  Settling time (2%)  : {m.settling_time:.4g} s")
        print(f"  Rise time (10–90%)  : {m.rise_time:.4g} s")
        print(f"  Steady-state error  : {m.ess:.4g}")
        print(f"  ITAE                : {m.itae:.4g}")
        print(f"  ISE                 : {m.ise:.4g}")
        print(f"  Objective           : {best.obj:.4g}")

        export_results(prefix=save_prefix, Gp=Gp, structure=structure,
                       cands=cands, top=plot_top, want_json=export_json, want_csv=export_csv,
                       out_dir=self.out_dir)

        # Plotting handled lazily to keep core testable; write HTML/PNG if backends available
        if backend == "none":
            return len(cands)
        try:
            from .plotter import plot_step_mpl, plot_step_plotly
            if backend == "mpl":
                plot_step_mpl(cands, Gp, structure, plot_top,
                              save_path=os.path.join(self.out_dir, f"{save_prefix}_step_mpl.png"))
            else:
                plot_step_plotly(cands, Gp, structure, plot_top,
                                 save_path=os.path.join(self.out_dir, f"{save_prefix}_step_plotly.html"))
        except Exception as e:
            print(f"[warn] plotting failed: {e}")
        return len(cands)

# keep import local to avoid issues when control is missing in some environments
import os  # noqa: E402
