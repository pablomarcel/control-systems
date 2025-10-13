# tools/class_diagram.py
from __future__ import annotations
import shutil
from pathlib import Path

DIAGRAM_DOT = """
digraph G {
  rankdir=LR;
  node [shape=record, style=rounded];
  CanonicalApp [label="{CanonicalApp|+ run(req)\l+ render(req,res)\l}"];
  CanonicalDesigner [label="{CanonicalDesigner|+ run(num,den): RunResult\l}"];
  CanonicalForms [label="{CanonicalForms|+ ccf_from_tf\l+ ocf_from_ss\l+ modal_real\l}"];
  RunRequest [label="{RunRequest|num, den, tfinal, dt, ...}"];
  RunResult [label="{RunResult|sys_ccf, sys_ocf, sys_modal, ...}"];
  CanonicalApp -> CanonicalDesigner;
  CanonicalDesigner -> CanonicalForms;
  CanonicalApp -> RunRequest;
  CanonicalApp -> RunResult;
}
"""

def write_dot(out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(DIAGRAM_DOT, encoding="utf-8")
    return out

def render_png(dot_path: Path, png_path: Path) -> Path | None:
    if shutil.which("dot") is None:
        return None
    import subprocess
    subprocess.check_call(["dot", "-Tpng", str(dot_path), "-o", str(png_path)])
    return png_path

if __name__ == "__main__":
    out_dir = Path("out")
    dotp = write_dot(out_dir / "canonicalTool_class_diagram.dot")
    render_png(dotp, out_dir / "canonicalTool_class_diagram.png")
    print(dotp)
