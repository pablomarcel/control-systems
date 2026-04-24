# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import shutil
import tempfile
import subprocess
import textwrap

DOT = r"""
digraph G {
  rankdir=LR;
  node [shape=record, fontsize=10];

  SystemSpec [label="{SystemSpec|+ A: ndarray\l+ C: ndarray\l+ B: ndarray?\l+ n(): int\l}"];
  MinOrderObserverDesigner [label="{MinOrderObserverDesigner|+ compute_T()\l+ compute_bar()\l+ ke_acker()\l+ design()\l}"];
  MinOrdAppService [label="{MinOrdAppService|+ design_observer()\l}"];

  SystemSpec -> MinOrderObserverDesigner [label="composition"];
  MinOrderObserverDesigner -> MinOrdAppService [style=dashed, label="used by"];
}
"""

def main(argv: list[str] | None = None):
    # Do NOT read pytest’s argv; parse only what’s passed in
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument(
        "--out",
        default=os.path.join("state_space_design", "minOrdTool", "out", "minOrdTool_classes.png"),
        help="Output path for the class diagram (PNG). If Graphviz 'dot' is not available, a .dot file is written instead."
    )
    args = ap.parse_args(argv or [])

    out = args.out
    os.makedirs(os.path.dirname(out), exist_ok=True)

    dot_path = shutil.which("dot")
    if dot_path:
        with tempfile.NamedTemporaryFile("w", suffix=".dot", delete=False) as f:
            f.write(DOT)
            dotfile = f.name
        subprocess.run([dot_path, "-Tpng", dotfile, "-o", out], check=False)
        print(f"Class diagram → {out}")
    else:
        # Fallback: write .dot so the user can render later
        fallback = out.rsplit(".", 1)[0] + ".dot"
        with open(fallback, "w") as f:
            f.write(DOT)
        print("Graphviz 'dot' not found. Wrote DOT file →", fallback)

if __name__ == "__main__":
    main()
