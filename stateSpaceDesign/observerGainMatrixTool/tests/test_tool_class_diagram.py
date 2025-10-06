import os
from pathlib import Path

os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH","") + (":" if os.environ.get("PYTHONPATH") else "") + "/mnt/data"
from stateSpaceDesign.observerGainMatrixTool.tools.tool_class_diagram import write_mermaid

def test_write_mermaid(tmp_path):
    path = write_mermaid(str(tmp_path / "classes.mmd"))
    p = Path(path)
    assert p.exists()
    assert "classDiagram" in p.read_text()
