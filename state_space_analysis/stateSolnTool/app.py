
# app.py — high-level application facade
from __future__ import annotations
import logging
from .core import StateSolnEngine

class StateSolnApp:
    DEFAULT_OUTDIR = "state_space_analysis/stateSolnTool/out"

    def __init__(self, canonical: str = "controllable"):
        self.engine = StateSolnEngine(canonical=canonical)

    def run(self, **kwargs):
        return self.engine.run(**kwargs)

    @staticmethod
    def configure_logging(level: str = "INFO"):
        logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO),
                            format="%(levelname)s: %(message)s")
