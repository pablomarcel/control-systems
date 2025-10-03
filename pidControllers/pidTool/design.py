from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
try:
    import control as ct
except Exception:  # pragma: no cover
    ct = None

from .core import (Metrics, Requirements, Candidate,
                   controller_tf, compute_metrics, meets_requirements,
                   objective_value, poles_stable)

def make_grid(vals: List[float], rng: Optional[List[float]], n: Optional[int]) -> List[float]:
    if vals:
        return sorted(vals)
    if rng and n:
        lo, hi = float(rng[0]), float(rng[1])
        return list(np.linspace(lo, hi, int(n)))
    raise ValueError("Provide explicit --*-vals or --*-range ... --*-n for each parameter.")

def make_grids(args) -> Dict[str, List[float]]:
    from .utils import parse_list_of_floats as _pf
    grids: Dict[str, List[float]] = {}
    if args.structure == "pid":
        grids["Kp"] = make_grid(_pf(args.Kp_vals), args.Kp_range, args.Kp_n)
        grids["Ki"] = make_grid(_pf(args.Ki_vals), args.Ki_range, args.Ki_n)
        grids["Kd"] = make_grid(_pf(args.Kd_vals), args.Kd_range, args.Kd_n)
    elif args.structure == "pi":
        grids["Kp"] = make_grid(_pf(args.pi_Kp_vals), args.pi_Kp_range, args.pi_Kp_n)
        grids["Ki"] = make_grid(_pf(args.pi_Ki_vals), args.pi_Ki_range, args.pi_Ki_n)
    elif args.structure == "pd":
        grids["Kp"] = make_grid(_pf(args.pd_Kp_vals), args.pd_Kp_range, args.pd_Kp_n)
        grids["Kd"] = make_grid(_pf(args.pd_Kd_vals), args.pd_Kd_range, args.pd_Kd_n)
    elif args.structure == "pid_dz":
        grids["K"]  = make_grid(_pf(args.K_vals), args.K_range, args.K_n)
        grids["a"]  = make_grid(_pf(args.a_vals), args.a_range, args.a_n)
    else:
        raise ValueError("unknown structure")
    return grids

def search_candidates(Gp: "ct.TransferFunction",
                      structure: str,
                      grids: Dict[str, List[float]],
                      req: Requirements,
                      tfinal: Optional[float],
                      dt: Optional[float],
                      objective: str,
                      wts: Tuple[float, float, float, float],
                      max_eval_warn: int = 250_000) -> List[Candidate]:
    from itertools import product
    keys = list(grids.keys())
    lists = [grids[k] for k in keys]
    total = 1
    for L_ in lists:
        total *= max(1, len(L_))
    if total > max_eval_warn:
        print(f"[warn] large grid ({total} combos). Consider tightening ranges.")

    results: List[Candidate] = []
    for values in product(*lists):
        params = {k: float(v) for k, v in zip(keys, values)}
        try:
            Gc = controller_tf(structure, params)
        except Exception as e:
            print(f"[skip] invalid controller {params}: {e}")
            continue

        L = Gc * Gp
        T = ct.feedback(L, 1)

        if not poles_stable(T):
            continue

        m = compute_metrics(T, tfinal=tfinal, dt=dt, settle_tol=req.settle_tol)
        if not meets_requirements(m, req):
            continue

        obj = objective_value(m, objective, *wts)
        results.append(Candidate(params=params, metrics=m, obj=obj,
                                 stable=True, controller_str=str(Gc)))

    results.sort(key=lambda c: c.obj)
    return results
