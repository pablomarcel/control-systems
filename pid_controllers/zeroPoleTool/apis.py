from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
import control as ct
import sympy as sp
from .core import tf_from_coeff, tf_from_poly, tf_from_zpk, plant_polys
from .design import Designer, Candidate, StepMetrics, linspace_or_vals
from .io import export_results
from .viz import step_reference, step_disturbance, ramp_reference, accel_reference
from .utils import parse_list_of_floats, parse_list_of_complex, pretty_tf

@dataclass(slots=True)
class DesignRequest:
    plant_form: str
    num: Optional[str] = None
    den: Optional[str] = None
    num_poly: Optional[str] = None
    den_poly: Optional[str] = None
    gain: Optional[float] = None
    zeros: Optional[str] = None
    poles: Optional[str] = None
    arch: str = "fig8-31"
    a_vals: Optional[str] = None; b_vals: Optional[str] = None; c_vals: Optional[str] = None
    a_range: Optional[Tuple[float,float]] = None; a_n: Optional[int] = None
    b_range: Optional[Tuple[float,float]] = None; b_n: Optional[int] = None
    c_range: Optional[Tuple[float,float]] = None; c_n: Optional[int] = None
    os_min: float = 0.0; os_max: float = 100.0; ts_max: float = 10.0; settle_tol: float = 0.02
    rank_dist_peak_weight: float = 0.0
    export_json: bool = False; export_csv: bool = False
    plot_prefix: str = "zp_design"; save_prefix: str = "zp_design"
    plots: List[str] = None
    no_progress: bool = False
    best_effort: bool = False
    debug: bool = False

class ZeroPoleAPI:
    @staticmethod
    def build_gp(req: DesignRequest) -> ct.TransferFunction:
        s = sp.Symbol("s")
        if req.plant_form == "coeff":
            if not req.num or not req.den:
                raise ValueError("coeff form needs num & den")
            return tf_from_coeff(parse_list_of_floats(req.num), parse_list_of_floats(req.den))
        if req.plant_form == "poly":
            if not req.num_poly or not req.den_poly:
                raise ValueError("poly form needs num_poly & den_poly")
            return tf_from_poly(req.num_poly, req.den_poly, s)
        if req.plant_form == "zpk":
            z = parse_list_of_complex(req.zeros); p = parse_list_of_complex(req.poles); k = req.gain or 1.0
            return tf_from_zpk(z, p, float(k))
        raise ValueError(f"unknown plant_form {req.plant_form}")

    @staticmethod
    def run(req: DesignRequest):
        Gp = ZeroPoleAPI.build_gp(req)
        print(pretty_tf("Plant Gp(s)", Gp)); print(f"[arch] {req.arch}")
        a_grid = linspace_or_vals(parse_list_of_floats(req.a_vals) if req.a_vals else [], req.a_range or (0,0), req.a_n or 0)
        b_grid = linspace_or_vals(parse_list_of_floats(req.b_vals) if req.b_vals else [], req.b_range or (0,0), req.b_n or 0)
        c_grid = linspace_or_vals(parse_list_of_floats(req.c_vals) if req.c_vals else [], req.c_range or (0,0), req.c_n or 0)
        designer = Designer(arch=req.arch)
        best, ok_list, closest, counts = designer.search(Gp, a_grid, b_grid, c_grid,
                                                         req.os_min, req.os_max, req.ts_max, req.settle_tol,
                                                         req.rank_dist_peak_weight,
                                                         show_progress=(not req.no_progress), debug=req.debug)
        picked = best
        used_best_effort = False
        if not ok_list and closest and req.best_effort:
            closest.sort(key=lambda x: x[0])
            a,b,c = closest[0][1]
            P = plant_polys(Gp)
            builder = designer.arch.build_channels
            Gc1,Gc2,Gc_sum,T_ref,T_dist,den_cl,Kc,z1,z0 = builder(a,b,c,P)
            from .design import step_metrics
            mr = step_metrics(T_ref, settle_tol=req.settle_tol)
            md = step_metrics(T_dist, settle_tol=req.settle_tol)
            from control.timeresp import step_response
            from .utils import pick_tgrid_from_poles
            ttmp = pick_tgrid_from_poles(ct.poles(T_dist)); _, ytmp = step_response(T_dist, ttmp)
            import numpy as np
            peak = float(np.max(np.abs(np.asarray(ytmp, dtype=float))))
            picked = Candidate(a=a,b=b,c=c,Kc=Kc,z1=z1,z0=z0,
                               Gc1=Gc1,Gc2=Gc2,Gc_sum=Gc_sum,
                               T_ref=T_ref,T_dist=T_dist,
                               metrics_ref=mr,metrics_dist=md, den_cl=den_cl, dist_peak=peak)
            used_best_effort = True

        if not picked:
            print("[RESULT] No candidate satisfied the constraints.")
            return None, []

        print("\n=== Best candidate" + (" [BEST-EFFORT]" if used_best_effort else "") + " ===")
        c = picked
        print(f"(a,b,c)=({c.a:.4g}, {c.b:.4g}, {c.c:.4g}) | Kc={c.Kc:.4g}, z1={c.z1:.4g}, z0={c.z0:.4g}")
        print("Disturbance peak |y|max:", f"{c.dist_peak:.4g}")
        print("\n" + str(c.Gc1)); print(str(c.Gc2)); print(str(c.Gc_sum))

        if req.export_json or req.export_csv:
            P = plant_polys(Gp)
            export_results(req.save_prefix, str(Gp), req.arch, P.Kp, P.A, P.B, ok_list if ok_list else [picked], req.export_json, req.export_csv)

        if req.plots:
            if "step_ref" in req.plots:  step_reference(req.plot_prefix, picked)
            if "step_dist" in req.plots: step_disturbance(req.plot_prefix, picked)
            if "ramp_ref" in req.plots:  ramp_reference(req.plot_prefix, picked)
            if "accel_ref" in req.plots: accel_reference(req.plot_prefix, picked)

        return picked, ok_list
