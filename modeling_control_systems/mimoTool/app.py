
from __future__ import annotations
import logging
from typing import Dict
import numpy as np
import matplotlib.pyplot as plt

from .apis import RunConfig, RunResult, PlantSummary
from .core import MIMOPlantBuilder, MIMOAnalyzer
from .design import MIMOPlotter, PlotConfig
from .io import write_json
from .utils import ensure_out_path

_PLANTS = {
    "two_tank": MIMOPlantBuilder.two_tank,
    "two_zone_thermal": MIMOPlantBuilder.two_zone_thermal,
}

class MIMOApp:
    """Coordinates analysis, plotting, and I/O for MIMO examples."""

    def __init__(self, level: int = logging.INFO) -> None:
        self.log = logging.getLogger("mimoTool")
        self.log.setLevel(level)
        if not self.log.handlers:
            h = logging.StreamHandler()
            h.setLevel(level)
            self.log.addHandler(h)

    def run(self, cfg: RunConfig) -> RunResult:
        self.log.info("Running MIMO analyses for: %s", ", ".join(cfg.plants))
        summaries = []
        w = cfg.wgrid()

        for pname in cfg.plants:
            sys = _PLANTS[pname]()
            poles = [complex(p) for p in MIMOAnalyzer.poles(sys)]
            summaries.append(PlantSummary(name=pname, poles=poles))

            # steps
            steps = MIMOAnalyzer.step_for_each_input(sys, cfg.tfinal, cfg.dt)
            if cfg.plot_steps:
                MIMOPlotter.steps_per_input(steps, PlotConfig(title_prefix=cfg.title_prefix, show=cfg.show))
                if cfg.save_png:
                    for u in range(len(steps)):
                        p = ensure_out_path(cfg.save_png.format(plant=pname, kind=f"step_u{u+1}"), "out", f"{pname}_step_u{u+1}.png")
                        plt.gcf().savefig(p)

            # sigma
            sout = MIMOAnalyzer.sigma_over_frequency(sys, w)
            if cfg.plot_sigma:
                MIMOPlotter.sigma(sout, PlotConfig(sigma_title=f"{pname}: σ(G(jω))", show=cfg.show))
                if cfg.save_png:
                    p = ensure_out_path(cfg.save_png.format(plant=pname, kind="sigma"), "out", f"{pname}_sigma.png")
                    plt.gcf().savefig(p)

            # JSON summary per plant
            if cfg.save_json:
                write_json({"plant": pname, "poles": [complex(p) for p in poles]}, cfg.save_json.format(plant=pname), "out", f"{pname}_summary.json")

        return RunResult(summaries=summaries)

    def render(self, cfg: RunConfig, result: RunResult) -> None:
        # Rendering handled inline during run (plots already created/saved)
        self.log.debug("Render step complete (plots already handled).")
