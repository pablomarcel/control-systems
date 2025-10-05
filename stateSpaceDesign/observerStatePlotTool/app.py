from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from .apis import PlotRequest, PlotResponse
from .io import JSONLoader, CSVWriter
from .core import ObserverStateProcessor
from .tools.plotting import MplPlotter, PlotlyPlotter

@dataclass
class ObserverStatePlotApp:
    def run(self, req: PlotRequest) -> PlotResponse:
        # Load
        payload = JSONLoader().load(req.data_path)

        # Sim or use present
        processor = ObserverStateProcessor()
        bundle = processor.load_or_simulate(
            payload,
            simulate=req.simulate.enabled,
            t_spec=req.simulate.t,
            x0_spec=req.simulate.x0,
            e0_spec=req.simulate.e0,
        )

        # Determine what to plot
        if req.what.strip().lower() == "auto":
            def _have(name: str) -> bool:
                return {"x": bundle.X is not None, "e": bundle.E is not None,
                        "err": (bundle.X is not None and bundle.E is not None),
                        "y": bundle.y is not None, "u": bundle.u is not None}[name]
            want = [nm for nm in ("x","e","y","u") if _have(nm)]
        else:
            want = [w.strip().lower() for w in req.what.split(",") if w.strip()]

        labels, series = processor.choose_series(want, bundle.X, bundle.E, bundle.y, bundle.u)

        # CSV
        csv_path = None
        if req.save_csv:
            csv_path = CSVWriter().write(req.save_csv, bundle.t, series, labels)

        # Plots
        png_path = None
        html_path = None
        if req.backend in ("mpl","both"):
            png_path = MplPlotter(subplots=req.subplots, no_show=req.no_show).plot(
                bundle.t, series, labels, req.save_png
            )
        if req.backend in ("plotly","both"):
            html_path = PlotlyPlotter(subplots=req.subplots).plot(
                bundle.t, series, labels, req.save_html
            )

        return PlotResponse(csv_path=csv_path, png_path=png_path, html_path=html_path)
