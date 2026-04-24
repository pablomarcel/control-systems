from __future__ import annotations
import sys
import types
from pathlib import Path
import numpy as np

from transient_analysis.hurwitzTool.io import IOManager

def test_io_dirs_and_csv(tmp_path: Path):
    io = IOManager(tmp_path)
    assert io.in_dir.exists()
    assert io.out_dir.exists()
    csv_path = tmp_path / "out" / "test.csv"
    saved = io.save_csv(csv_path, ["a","b"], [[1,2],[3,4]])
    assert saved.exists() and saved.read_text().strip().splitlines()[0] == "a,b"

def test_save_png_heatmap_with_fake_matplotlib(tmp_path: Path, monkeypatch):
    # Inject a fake matplotlib.pyplot implementation
    fake_pyplot = types.SimpleNamespace()
    calls = {}

    def recorder(name):
        def fn(*args, **kwargs):
            calls[name] = calls.get(name, 0) + 1
        return fn

    fake_pyplot.figure = recorder("figure")
    fake_pyplot.imshow = recorder("imshow")
    fake_pyplot.xlabel = recorder("xlabel")
    fake_pyplot.ylabel = recorder("ylabel")
    fake_pyplot.title = recorder("title")
    fake_pyplot.colorbar = recorder("colorbar")
    fake_pyplot.tight_layout = recorder("tight_layout")
    def savefig(path, dpi=160):
        # create an empty file to simulate saved PNG
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(b"PNG")
        calls["savefig"] = calls.get("savefig", 0) + 1
    fake_pyplot.savefig = savefig
    fake_pyplot.close = recorder("close")

    fake_matplotlib = types.SimpleNamespace(pyplot=fake_pyplot)
    monkeypatch.setitem(sys.modules, "matplotlib", fake_matplotlib)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", fake_pyplot)

    io = IOManager(tmp_path)
    xs = np.array([0.0, 1.0])
    ys = np.array([0.0, 1.0])
    Z = np.array([[1,0],[0,1]], dtype=bool)
    msg = io.save_png_heatmap(tmp_path / "out" / "hm.png", xs, ys, Z)
    assert "Saved PNG" in msg
    assert (tmp_path / "out" / "hm.png").exists()
    # ensure our pyplot was exercised
    assert calls.get("imshow", 0) == 1
