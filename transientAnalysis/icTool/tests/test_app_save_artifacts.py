import numpy as np
from pathlib import Path
import os
os.environ["MPLBACKEND"] = "Agg"

from transientAnalysis.icTool.app import IcToolApp

def test_app_saves_plots_and_json(tmp_path: Path):
    app = IcToolApp(base_dir=tmp_path)

    A = np.array([[0,1],[-6,-5]], float)
    x0 = np.array([0.2, 0.1], float)
    T = np.linspace(0, 0.1, 6)

    # compare1 (plot)
    app.run_compare1(A, x0, T, save=True)
    assert (tmp_path / "out" / "compare1.png").exists()

    # case1 (plot)
    app.run_case1(A, x0, T, save=True)
    assert (tmp_path / "out" / "case1.png").exists()

    # compare2 (plot)
    C = np.eye(2)
    app.run_compare2(A, C, x0, T, save=True)
    assert (tmp_path / "out" / "compare2.png").exists()

    # TF ogata (plot + json + analytic overlay)
    app.run_tf_step_ogata(1.0, 3.0, 2.0, 0.1, 0.05, T, save=True, save_json=True, overlay_analytic=True)
    assert (tmp_path / "out" / "tf_step_ogata.png").exists()
    assert (tmp_path / "out" / "tf_step_ogata.json").exists()

    # TF generic (plot + json)
    app.run_tf_step_generic(np.array([0.1, 0.05, 0.0]), np.array([1.0, 3.0, 2.0]), T, save=True, save_json=True)
    assert (tmp_path / "out" / "tf_step.png").exists()
    assert (tmp_path / "out" / "tf_step.json").exists()