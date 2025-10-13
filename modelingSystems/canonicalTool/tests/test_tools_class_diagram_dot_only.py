
from pathlib import Path
import shutil
from modelingSystems.canonicalTool.tools.class_diagram import write_dot, render_png

def test_write_dot_and_skip_png(tmp_path, monkeypatch):
    dotp = write_dot(tmp_path / "x.dot")
    assert dotp.exists()
    # Simulate no 'dot' in PATH
    monkeypatch.setenv("PATH", "", prepend=False)
    out = render_png(dotp, tmp_path / "x.png")
    assert out is None or (hasattr(out, "exists") and out.exists())
