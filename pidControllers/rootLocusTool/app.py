from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .design import RootLocusConfig
from .apis import RootLocusService, RootLocusRequest

@dataclass(slots=True)
class RootLocusApp:
    in_dir: str = "pidControllers/rootLocusTool/in"
    out_dir: str = "pidControllers/rootLocusTool/out"

    def run(
        self, *,
        example: Optional[str] = None,
        num: Optional[str] = None,
        den: Optional[str] = None,
        backend: str = "plotly",
        save: Optional[str] = None,
        export_json: Optional[str] = None,
        export_csv: Optional[str] = None,
        **kwargs
    ):
        # ---- split config kwargs vs request-only kwargs ----
        cfg_keys = {
            "zeta_values", "zeta_range", "zeta_n",
            "omega", "kmin", "kmax",
            "a_override",
            "ray_wmin", "ray_scale",
            "xlim", "ylim",
            "title",
        }
        cfg_kwargs = {k: v for k, v in kwargs.items() if k in cfg_keys}
        req_only = {k: v for k, v in kwargs.items() if k not in cfg_keys}

        cfg = RootLocusConfig(example=example, num=num, den=den, **cfg_kwargs)

        svc = RootLocusService()
        req = RootLocusRequest(
            cfg=cfg,
            backend=backend,
            save=save,
            export_json_path=export_json,
            export_csv_path=export_csv,
            analyze=bool(req_only.get("analyze", False)),
            settle=float(req_only.get("settle", 0.02)),
            precision=int(req_only.get("precision", 6)),
        )
        return svc.run(req)
