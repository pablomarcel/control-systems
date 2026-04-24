
from __future__ import annotations
from pathlib import Path
from control_systems.converterTool.tools import samples, class_diagram

def test_samples_and_diagram(tmp_path, monkeypatch):
    # run samples: writes into ./in relative to CWD; switch to tmp
    monkeypatch.chdir(tmp_path)
    (tmp_path / "in").mkdir(exist_ok=True)
    samples.main()
    assert (tmp_path / "in" / "tf_siso.json").exists()
    assert (tmp_path / "in" / "ss_siso.json").exists()
    # class diagram: write custom out path
    out_dot = tmp_path / "diagram.dot"
    monkeypatch.setenv("PYTHONHASHSEED","0")
    class_diagram.main(out=str(out_dot))
    assert out_dot.exists()
