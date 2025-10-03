from __future__ import annotations
import os, csv, json
from dataclasses import asdict
from typing import List
try:
    import control as ct
except Exception:  # pragma: no cover
    ct = None

from .core import Candidate
from .utils import ensure_out_dir

def export_results(prefix: str,
                   Gp: "ct.TransferFunction",
                   structure: str,
                   cands: List[Candidate],
                   top: int,
                   want_json: bool,
                   want_csv: bool,
                   out_dir: str | None = None) -> None:
    outdir = ensure_out_dir(out_dir)
    meta = {
        "plant": str(Gp),
        "structure": structure,
        "top": min(top, len(cands)),
        "results": [
            {"rank": i+1, "params": cand.params, "metrics": asdict(cand.metrics),
             "objective": cand.obj, "controller": cand.controller_str}
            for i, cand in enumerate(cands[:top])
        ]
    }
    if want_json:
        pj = os.path.join(outdir, f"{prefix}_results.json")
        with open(pj, "w", encoding="utf-8") as f: json.dump(meta, f, indent=2)
        print(f"[saved] JSON -> {pj}")
    if want_csv:
        pc = os.path.join(outdir, f"{prefix}_results.csv")
        with open(pc, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["rank","params","OS_%","Ts_s","Tr_s","ESS","ITAE","ISE","objective"])
            for i, cand in enumerate(cands[:top]):
                m = cand.metrics
                w.writerow([i+1, cand.params, f"{m.overshoot:.6g}", f"{m.settling_time:.6g}",
                            f"{m.rise_time:.6g}", f"{m.ess:.6g}", f"{m.itae:.6g}",
                            f"{m.ise:.6g}", f"{cand.obj:.6g}"])
        print(f"[saved] CSV -> {pc}")
