from __future__ import annotations
import numpy as np
import logging as log
from .apis import RunRequest, RunResult
from .core import Plant, Controller, Weights, FrequencyTools, LoopBuilder
from .design import RobustAnalyzer
from .tools.plot import Plotter

class RobustApp:
    def __init__(self, logger: str | None = None):
        if logger:
            log.getLogger(logger)

    def run(self, req: RunRequest) -> RunResult:
        plant = Plant(req.num, req.den)
        ctrl = Controller(req.pid, req.K_num, req.K_den)
        weights = Weights(req.Wm_num, req.Wm_den, req.Ws_num, req.Ws_den, req.Wa_num, req.Wa_den)
        analyzer = RobustAnalyzer(req, plant, ctrl, weights)
        result = analyzer.run()

        # Optional plotting
        if req.plots != "none":
            try:
                # Build loops once more for plotting curves
                G = plant.tf(); K = ctrl.tf()
                L, S, T = LoopBuilder.loops(G, K)
                w = np.logspace(np.log10(req.wmin), np.log10(req.wmax), req.npts)
                curves = []
                try:
                    mT, pT = FrequencyTools.bode_mag_phase(T, w); curves.append(("T (closed-loop)", {"mag": mT, "phs": pT}))
                    mS, pS = FrequencyTools.bode_mag_phase(S, w); curves.append(("S (sensitivity)", {"mag": mS, "phs": pS}))
                except Exception as e:
                    log.warning(f"Bode overlay skipped (likely MIMO): {e}")
                # Weighted overlays (mag only)
                from control import series
                if req.Wm_num and req.Wm_den:
                    mWmT, _ = FrequencyTools.bode_mag_phase(series(Weights(req.Wm_num, req.Wm_den).get()[0], T), w)
                    curves.append(("Wm·T", {"mag": mWmT, "phs": None}))
                if req.Ws_num and req.Ws_den:
                    mWsS, _ = FrequencyTools.bode_mag_phase(series(Weights(None, None, req.Ws_num, req.Ws_den).get()[1], S), w)
                    curves.append(("Ws·S", {"mag": mWsS, "phs": None}))
                if curves:
                    if req.plots in ("mpl","both"):    Plotter.bode_mpl(w, curves)
                    if req.plots in ("plotly","both"): Plotter.bode_plotly(w, curves)
            except Exception as e:
                log.error(f"Plotting failed: {e}")

        # Optional step plots
        if req.step and result.step_time is not None:
            try:
                if req.plots in ("mpl","both"):    Plotter.step_mpl(result.step_time, result.step_y, result.step_u)
                if req.plots in ("plotly","both"): Plotter.step_plotly(result.step_time, result.step_y, result.step_u)
            except Exception as e:
                log.error(f"Step plotting failed: {e}")

        return result
