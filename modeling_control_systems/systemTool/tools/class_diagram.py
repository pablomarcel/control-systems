#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, sys
from pathlib import Path

if __package__ in (None, ""):
    pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    import modeling_control_systems.systemTool.app as app_mod
    import modeling_control_systems.systemTool.apis as apis_mod
else:
    from .. import app as app_mod, apis as apis_mod

MERMAID = """
classDiagram
  class SystemModelingApp {
    +run(cfg: RunConfig) -> RunResult
  }
  class RunConfig {
    +mode: Literal
    +msd: MSDConfig?
    +tfss: TFfromSSConfig?
    +ode_nd: ODENoDerivConfig?
    +ode_d: ODEWithDerivConfig?
    +kvmax: CommonSim?
  }
  class RunResult {
    +ok: bool
    +message: str
    +pretty_tf: str
    +saved_images: list~str~
    +hints: list~str~
  }
  SystemModelingApp --> RunConfig
  SystemModelingApp --> RunResult
  RunConfig --> MSDConfig
  RunConfig --> TFfromSSConfig
  RunConfig --> ODENoDerivConfig
  RunConfig --> ODEWithDerivConfig
  RunConfig --> CommonSim
"""

def main():
    ap = argparse.ArgumentParser(description="Emit a Mermaid class diagram for systemTool.")
    ap.add_argument("--out", default="out/systemTool_class_diagram.mmd")
    ns = ap.parse_args()
    out = Path(__file__).resolve().parents[1] / ns.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(MERMAID.strip()+"\n", encoding="utf-8")
    print(out)

if __name__ == "__main__":
    main()
