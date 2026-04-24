# SPDX-License-Identifier: MIT
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from .io import load_json, try_parse_controller, try_parse_io
from .core import ScenarioDetector, Simulator, parse_time, parse_vec_real
from .design import CSVExporter, PlotBackend
from .utils import DEFAULT_IN_DIR, DEFAULT_OUT_DIR

@dataclass
class RunRequest:
    data: Path
    scenario: str = 'auto'      # 'auto' | 'ic' | 'step'
    what: str = 'auto'          # 'auto'->('y' for step) | 'y' | 'states' | 'both'
    subplots: bool = False
    t: str = '0:0.01:4'
    x0: Optional[str] = None
    backend: str = 'both'       # 'mpl' | 'plotly' | 'both' | 'none'
    save_png: Optional[str] = None
    save_html: Optional[str] = None
    save_csv: Optional[str] = None
    in_dir: Path = DEFAULT_IN_DIR
    out_dir: Path = DEFAULT_OUT_DIR
    no_show: bool = True        # tests set True; CLI can toggle

class StatePlotsAPI:
    def run(self, req: RunRequest) -> dict:
        payload = load_json(req.data)
        scenario = req.scenario
        if scenario == 'auto':
            scenario = ScenarioDetector.detect(payload)
        T = parse_time(req.t)
        csv = CSVExporter()
        plot = PlotBackend(subplots=req.subplots)
        results = {'scenario': scenario, 'paths': {}}

        if scenario == 'ic':
            cj = try_parse_controller(payload)
            if cj is None:
                raise ValueError("Provided JSON is not a controller payload for IC scenario")
            x0 = parse_vec_real(req.x0, cj.A.shape[0])
            res = Simulator.initial_condition(cj, T, x0)
            results['labels'] = res.labels
            results['t_len'] = len(res.t)
            if req.save_csv:
                p = csv.save_ic(res, filename=req.save_csv, out_dir=req.out_dir)
                results['paths']['csv'] = str(p)
            series = [res.X[i,:] for i in range(res.X.shape[0])]
            title = "Closed-loop response to initial condition"
            ylab = "states"
        elif scenario == 'step':
            ioj = try_parse_io(payload)
            if ioj is None:
                raise ValueError("Provided JSON is not an IO payload for STEP scenario")
            what = 'y' if req.what == 'auto' else req.what
            res = Simulator.step(ioj, T, what=what)
            results['labels'] = res.labels
            results['t_len'] = len(res.t)
            if req.save_csv:
                p = csv.save_step(res, filename=req.save_csv, out_dir=req.out_dir)
                results['paths']['csv'] = str(p)
            series = res.series
            title = "Step response" if res.kind=='y' else ("Step response (states)" if res.kind=='states' else "Step response (outputs + states)")
            ylab = "output" if res.kind=='y' else ("states" if res.kind=='states' else "value")
            T = res.t
        else:
            raise ValueError("Unknown scenario")

        if req.backend in ('mpl','both'):
            if req.save_png is not None:
                p = plot.mpl(T, series, results['labels'], title, ylab, filename_png=req.save_png, out_dir=req.out_dir)
                results['paths']['png'] = str(p) if p else None
        if req.backend in ('plotly','both'):
            if req.save_html is not None:
                p = plot.plotly(T, series, results['labels'], title, ylab, filename_html=req.save_html, out_dir=req.out_dir)
                results['paths']['html'] = str(p) if p else None
        return results
