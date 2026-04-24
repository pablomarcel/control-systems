from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple
import sympy as sp

from .utils import (
    parse_matrix, split_fraction_raw, parse_poly_text, parse_poly,
    normalize_monic, ensure_proper, pretty, to_numeric
)
from .core import (
    StateSpaceModel, controllable_canonical_from_tf,
    controllability_matrix, observability_matrix,
    alt_modal_ctrl, alt_modal_obs,
    s_plane_minimality, pbh_stabilizable, pbh_detectable
)

class AnalyzerMode(str, Enum):
    ALL = "all"
    STATE = "state"
    ALT = "alt"
    S_PLANE = "splane"
    OUTPUT = "output"
    STAB = "stab"
    OBS = "obs"
    OBSALT = "obsalt"
    OBSSPLANE = "obssplane"
    DETECT = "detect"

@dataclass
class RunOptions:
    mode: AnalyzerMode = AnalyzerMode.ALL
    pretty: bool = False
    numeric: bool = False
    digits: int = 8
    eps: float = 0.0
    export_json: Optional[str] = None

@dataclass
class AnalysisSummary:
    mode: str
    results: Dict

class StateSpaceAnalyzerAPI:
    """Facade class: orchestrates parsing → model → analysis → summary."""
    def __init__(self, out_dir: str = "state_space_analysis/stateTool/out"):
        self.out_dir = out_dir

    # ----------------------- Construction helpers -----------------------
    def build_from_state(
        self, A_txt: str, B_txt: str, C_txt: Optional[str] = None, D_txt: Optional[str] = None
    ) -> Tuple[StateSpaceModel, Dict]:
        A = parse_matrix(A_txt); B = parse_matrix(B_txt)
        C = parse_matrix(C_txt) if C_txt else None
        D = parse_matrix(D_txt) if D_txt else None
        return StateSpaceModel(A, B, C, D), {"tf_num_desc": None, "tf_den_desc": None}

    def build_from_tf(
        self, tf: Optional[str] = None, num: Optional[str] = None, den: Optional[str] = None
    ) -> Tuple[StateSpaceModel, Dict]:
        if not (tf or (num and den)):
            raise ValueError("Provide a TF via --tf or --num/--den.")
        if tf:
            split = split_fraction_raw(tf)
            if split:
                num_txt, den_txt = split
                tf_num_desc = parse_poly_text(num_txt)
                tf_den_desc = parse_poly_text(den_txt)
            else:
                # full sympify pipeline
                from .utils import to_expr_s, sym_s
                expr = sp.together(to_expr_s(tf))
                P, Q = sp.fraction(expr)
                Ps, Qs = sp.Poly(sp.expand(P), sym_s()), sp.Poly(sp.expand(Q), sym_s())
                tf_num_desc = [sp.nsimplify(c) for c in Ps.all_coeffs()]
                tf_den_desc = [sp.nsimplify(c) for c in Qs.all_coeffs()]
        else:
            tf_num_desc = parse_poly(num)
            tf_den_desc = parse_poly(den)

        num_m, den_m = normalize_monic(tf_num_desc, tf_den_desc)
        num_p, den_p, _ = ensure_proper(num_m, den_m)
        A, B, C, D = controllable_canonical_from_tf(num_p, den_p)
        return StateSpaceModel(A, B, C, D), {"tf_num_desc": tf_num_desc, "tf_den_desc": tf_den_desc}

    # ---------------------------- Analyses ------------------------------
    def analyze(self, model: StateSpaceModel, options: RunOptions, tf_desc: Dict) -> AnalysisSummary:
        A, B, C, D = model.A, model.B, model.C, model.D
        summary: Dict = {"mode": options.mode.value, "results": {}}

        # Controllability
        if options.mode in (AnalyzerMode.ALL, AnalyzerMode.STATE):
            Mc = controllability_matrix(A, B)
            rk = Mc.rank(); n = A.shape[0]; ok = (rk == n)
            summary["results"]["state"] = {"rank": int(rk), "n": int(n), "controllable": bool(ok)}

        if options.mode in (AnalyzerMode.ALL, AnalyzerMode.ALT):
            res, P, F = alt_modal_ctrl(A, B)
            entry = {}
            if res is None:
                entry["applicable"] = False
                evals = sp.Matrix.eigenvals(A)
                entry["eigs"] = {str(k): int(v) for k, v in evals.items()}
            else:
                entry["applicable"] = True; entry["controllable"] = bool(res)
            summary["results"]["alt"] = entry

        if options.mode in (AnalyzerMode.ALL, AnalyzerMode.S_PLANE):
            if tf_desc.get("tf_num_desc") is None or tf_desc.get("tf_den_desc") is None:
                summary["results"]["splane"] = {"skipped": True}
            else:
                num_m, den_m = normalize_monic(tf_desc["tf_num_desc"], tf_desc["tf_den_desc"])
                ok, gcd_expr, info = s_plane_minimality(num_m, den_m)
                summary["results"]["splane"] = {
                    "no_cancellation": bool(ok),
                    "gcd": str(sp.simplify(gcd_expr)),
                    "details": {k: str(v) for k, v in info.items()}
                }

        # Output controllability
        if options.mode in (AnalyzerMode.ALL, AnalyzerMode.OUTPUT):
            if C is None or D is None:
                summary["results"]["output"] = {"skipped": True}
            else:
                n = A.shape[0]; m = C.shape[0]
                blocks = []; Ak = sp.eye(n)
                for _ in range(n):
                    blocks.append(C * Ak * B); Ak = Ak * A
                if not isinstance(D, sp.MatrixBase): D = sp.Matrix([[D]]) if m == 1 else sp.zeros(m, 1)
                blocks.append(D)
                Mout = sp.Matrix.hstack(*blocks); rk = Mout.rank(); ok = (rk == m)
                summary["results"]["output"] = {"rank": int(rk), "m": int(m), "output_controllable": bool(ok)}

        if options.mode in (AnalyzerMode.ALL, AnalyzerMode.STAB):
            ok, bad = pbh_stabilizable(A, B, eps=options.eps)
            summary["results"]["stabilizable"] = {"stabilizable": bool(ok),
                                                  "uncontrollable_unstable_eigs": [complex(z).__repr__() for z in bad]}

        # Observability
        if options.mode in (AnalyzerMode.ALL, AnalyzerMode.OBS):
            if C is None:
                summary["results"]["obs"] = {"skipped": True}
            else:
                Mo = observability_matrix(A, C)
                rk = Mo.rank(); n = A.shape[0]; ok = (rk == n)
                summary["results"]["obs"] = {"rank": int(rk), "n": int(n), "observable": bool(ok)}

        if options.mode in (AnalyzerMode.ALL, AnalyzerMode.OBSALT):
            if C is None:
                summary["results"]["obsalt"] = {"skipped": True}
            else:
                res, P, CP = alt_modal_obs(A, C)
                entry = {}
                if res is None:
                    entry["applicable"] = False
                    evals = sp.Matrix.eigenvals(A)
                    entry["eigs"] = {str(k): int(v) for k, v in evals.items()}
                else:
                    entry["applicable"] = True; entry["observable"] = bool(res)
                summary["results"]["obsalt"] = entry

        if options.mode in (AnalyzerMode.ALL, AnalyzerMode.OBSSPLANE):
            if tf_desc.get("tf_num_desc") is None or tf_desc.get("tf_den_desc") is None:
                summary["results"]["obssplane"] = {"skipped": True}
            else:
                num_m, den_m = normalize_monic(tf_desc["tf_num_desc"], tf_desc["tf_den_desc"])
                ok, gcd_expr, info = s_plane_minimality(num_m, den_m)
                summary["results"]["obssplane"] = {
                    "no_cancellation": bool(ok),
                    "gcd": str(sp.simplify(gcd_expr)),
                    "details": {k: str(v) for k, v in info.items()}
                }

        if options.mode in (AnalyzerMode.ALL, AnalyzerMode.DETECT):
            if C is None:
                summary["results"]["detect"] = {"skipped": True}
            else:
                ok, bad = pbh_detectable(A, C, eps=options.eps)
                summary["results"]["detect"] = {"detectable": bool(ok),
                                                "unobservable_unstable_eigs": [complex(z).__repr__() for z in bad]}
        return AnalysisSummary(mode=options.mode.value, results=summary["results"])
