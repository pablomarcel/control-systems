from __future__ import annotations
import os, json, csv
from typing import List
from dataclasses import asdict
import numpy as np
from .utils import ensure_out_dir
from .design import Candidate
from . import utils

def export_results(prefix: str, plant_str: str, arch: str,
                   Kp: float, A: np.ndarray, B: np.ndarray,
                   cands: List[Candidate], want_json: bool, want_csv: bool) -> None:
    outdir = ensure_out_dir()
    if want_json:
        path = os.path.join(outdir, f"{prefix}_results.json")
        meta = {
            "plant": plant_str, "arch": arch,
            "Kp": float(Kp), "A_monic": list(map(float, A.tolist())),
            "B_monic": list(map(float, B.tolist())),
            "results": [
                {
                    "rank": i+1,
                    "a": c.a, "b": c.b, "c": c.c,
                    "Kc": c.Kc, "z1": c.z1, "z0": c.z0,
                    "dist_peak": c.dist_peak,
                    "metrics_ref": asdict(c.metrics_ref),
                    "metrics_dist": asdict(c.metrics_dist),
                    "Gc1": str(c.Gc1), "Gc2": str(c.Gc2), "Gc_sum": str(c.Gc_sum),
                    "T_ref": str(c.T_ref), "T_dist": str(c.T_dist),
                    "den_cl": c.den_cl,
                } for i, c in enumerate(cands)
            ]
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        print(f"[saved] JSON -> {path}")
    if want_csv:
        path = os.path.join(outdir, f"{prefix}_results.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["rank","a","b","c","Kc","z1","z0",
                        "OS_ref_%","Ts_ref_s","Tr_ref_s","ESS_ref",
                        "Ts_dist_s","Dist_peak"])
            for i, c in enumerate(cands):
                mr, md = c.metrics_ref, c.metrics_dist
                w.writerow([i+1, c.a, c.b, c.c, c.Kc, c.z1, c.z0,
                            f"{mr.overshoot:.6g}", f"{mr.settling_time:.6g}",
                            f"{mr.rise_time:.6g}", f"{mr.ess:.6g}",
                            f"{md.settling_time:.6g}", f"{c.dist_peak:.6g}"])
        print(f"[saved] CSV -> {path}")
