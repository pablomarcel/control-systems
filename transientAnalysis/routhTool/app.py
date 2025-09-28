# transientAnalysis/routhTool/app.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

from .core import RouthArrayBuilder, RouthConfig
from .utils import parse_coeffs, coerce_tokens, fmt_cell
from .io import RouthPaths, ensure_dirs, dump_json

@dataclass(slots=True)
class RouthApp:
    """High-level façade for the routhTool within modernControl."""
    paths: RouthPaths
    builder: RouthArrayBuilder

    @classmethod
    def discover(cls, package_dir: Path) -> "RouthApp":
        paths = RouthPaths.from_package_root(package_dir)
        ensure_dirs(paths)
        builder = RouthArrayBuilder(RouthConfig())
        return cls(paths=paths, builder=builder)

    def run(
        self,
        coeffs_raw: str,
        *,
        symbols: Optional[list[str]] = None,
        solve_for: Optional[str] = None,
        eps: float = 1e-9,
        compute_hurwitz: bool = False,
        verify_numeric: bool = False,
        export_basename: Optional[str] = None,
    ) -> Dict[str, Any]:
        tokens = parse_coeffs(coeffs_raw)
        coeffs = coerce_tokens(tokens, symbols or [])
        self.builder.cfg.eps = eps

        res = self.builder.run(
            coeffs,
            symbol_to_solve=solve_for,
            compute_hurwitz=compute_hurwitz,
            verify_numeric=verify_numeric,
        )

        payload = {
            "routh_array": [[fmt_cell(x) for x in row] for row in res.array],
            "first_column": [fmt_cell(x) for x in res.first_column],
            "degrees": res.degrees,
            "rhp_by_routh": res.rhp_by_routh,
            "rhp_by_roots": res.rhp_by_roots,
            "hurwitz_minors": [str(d) for d in (res.hurwitz_minors or [])] if res.hurwitz_minors else None,
            "stability_condition": str(res.stability_condition) if res.stability_condition is not None else None,
            "notes": [
                "Entire zero row -> derivative of auxiliary polynomial from prior row.",
                "Zero leading element -> epsilon trick.",
                "All-positive first column => asymptotic stability (no jω or RHP roots).",
            ],
        }

        if export_basename:
            out_json = self.paths.out_dir / f"{export_basename}.json"
            dump_json(out_json, payload)

        return payload