# SPDX-License-Identifier: MIT
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from .apis import StatePlotsAPI, RunRequest

@dataclass
class StatePlotsApp:
    api: StatePlotsAPI

    def run(self, **kwargs):
        req = RunRequest(**kwargs)
        return self.api.run(req)

def main_kwargs_from_args(args) -> dict:
    from .utils import DEFAULT_IN_DIR, DEFAULT_OUT_DIR
    data = Path(args.data)
    if not data.is_absolute():
        data = DEFAULT_IN_DIR / data
    return dict(
        data=data,
        scenario=args.scenario,
        what=args.what,
        subplots=args.subplots,
        t=args.t,
        x0=args.x0,
        backend=args.backend,
        save_png=args.save_png,
        save_html=args.save_html,
        save_csv=args.save_csv,
        no_show=args.no_show,
    )
