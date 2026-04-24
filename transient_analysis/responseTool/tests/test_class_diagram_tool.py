
from __future__ import annotations
import importlib, pathlib

def test_class_diagram_generate():
    mod = importlib.import_module("transient_analysis.responseTool.tools.class_diagram")
    pkg_dir = pathlib.Path("transient_analysis/responseTool")
    if not pkg_dir.exists():
        pkg_dir = pathlib.Path(mod.__file__).resolve().parent.parent
    out = mod.generate(pkg_dir)
    if isinstance(out, pathlib.Path):
        text = out.read_text(encoding="utf-8")
    else:
        text = str(out)
    assert "@startuml" in text and "@enduml" in text
