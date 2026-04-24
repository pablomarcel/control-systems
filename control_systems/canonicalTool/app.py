
# app.py
from __future__ import annotations
import logging
from typing import Optional
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import control as ct
from .apis import RunRequest, PlotConfig
from .design import CanonicalDesigner, RunResult

class CanonicalApp:
    def __init__(self, level: int = logging.INFO) -> None:
        self.log = logging.getLogger("canonicalTool")
        if not self.log.handlers:
            h = logging.StreamHandler()
            fmt = logging.Formatter("[%(levelname)s] %(message)s")
            h.setFormatter(fmt)
            self.log.addHandler(h)
        self.log.setLevel(level)
        self.designer = CanonicalDesigner()

    def run(self, req: RunRequest) -> RunResult:
        self.log.info("Running canonical conversion…")
        res = self.designer.run(req.num, req.den)
        self.log.info("G(s) normalized: %s", res.pretty_tf.replace("\n"," "))
        self.log.info("OCF == CCF ? %s", res.equal_ocf)
        self.log.info("Modal == CCF ? %s", res.equal_modal)
        return res

    def render(self, req: RunRequest, res: RunResult, plotcfg: Optional[PlotConfig] = None):
        if not req.plots:
            return
        if req.no_show:
            matplotlib.use("Agg", force=True)
        plotcfg = plotcfg or PlotConfig()
        styles = ['-', '--', ':']
        widths = [2.4, 2.0, 2.0]
        T = np.arange(0.0, req.tfinal + req.dt, req.dt)
        plt.figure(figsize=(8,4.5))
        for i, (sys, lab) in enumerate([(res.sys_ccf, "CCF"), (res.sys_ocf, "OCF"), (res.sys_modal, "Modal (real)") ]):
            T, y = ct.step_response(sys, T=T)
            plt.plot(T, y, styles[i % len(styles)], linewidth=widths[i % len(widths)], label=lab)
        plt.title(plotcfg.title)
        plt.xlabel("Time (s)"); plt.ylabel("y(t)")
        plt.grid(True); plt.legend(); plt.tight_layout()
        if req.save_png:
            plt.savefig(req.save_png, dpi=160)
        if not req.no_show:
            plt.show()
        plt.close()
