from __future__ import annotations
import argparse, os, shutil, tempfile, subprocess, textwrap

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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join("stateSpaceDesign","minOrdTool","out","minOrdTool_classes.png"))
    args = ap.parse_args()
    out = args.out
    os.makedirs(os.path.dirname(out), exist_ok=True)

    # Prefer graphviz 'dot' if present
    dot_path = shutil.which("dot")
    if dot_path:
        with tempfile.NamedTemporaryFile("w", suffix=".dot", delete=False) as f:
            f.write(DOT)
            dotfile = f.name
        subprocess.run([dot_path, "-Tpng", dotfile, "-o", out], check=False)
        print(f"Class diagram → {out}")
    else:
        # Fallback: write .dot so user can render later
        fallback = out.rsplit(".",1)[0] + ".dot"
        with open(fallback, "w") as f:
            f.write(DOT)
        print("Graphviz 'dot' not found. Wrote DOT file →", fallback)

if __name__ == "__main__":
    main()
