from __future__ import annotations
import logging
from typing import Optional, Dict

from .apis import StateSpaceAnalyzerAPI, RunOptions, AnalyzerMode
from .io import write_json

class StateToolApp:
    """High-level app orchestrator (CLI uses this)."""
    def __init__(self, out_dir: str = "state_space_analysis/stateTool/out"):
        self.api = StateSpaceAnalyzerAPI(out_dir=out_dir)

    def run_from_state(
        self, *, A: str, B: str, C: Optional[str], D: Optional[str], options: RunOptions
    ) -> Dict:
        model, tf_desc = self.api.build_from_state(A, B, C, D)
        summary = self.api.analyze(model, options, tf_desc)
        res = {"mode": summary.mode, "results": summary.results}
        if options.export_json:
            path = write_json(res, options.export_json)
            logging.info("Saved summary JSON to %s", path)
        return res

    def run_from_tf(self, *, tf: Optional[str], num: Optional[str], den: Optional[str], options: RunOptions) -> Dict:
        model, tf_desc = self.api.build_from_tf(tf=tf, num=num, den=den)
        summary = self.api.analyze(model, options, tf_desc)
        res = {"mode": summary.mode, "results": summary.results}
        if options.export_json:
            path = write_json(res, options.export_json)
            logging.info("Saved summary JSON to %s", path)
        return res
