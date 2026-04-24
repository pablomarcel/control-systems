from pathlib import Path
from modeling_control_systems.systemTool.tools.class_diagram import main as write_diagram

def test_write_diagram(tmp_path, monkeypatch):
    # Write to a temp file under the package 'out' to avoid changing repo
    out = tmp_path / "diagram.mmd"
    monkeypatch.setenv("PYTHONHASHSEED","0")
    # tools script writes under parents[1]/out/... by default; call with --out absolute
    import sys
    sys.argv = ["class_diagram.py", "--out", str(out)]
    write_diagram()
    assert out.exists()
