from __future__ import annotations
from pathlib import Path
from pid_controllers.rootLocusTool.app import RootLocusApp

def test_app_run_filters_kwargs(tmp_path, monkeypatch):
    # Use absolute paths for exports to avoid CWD dependency
    json_path = tmp_path / "app.json"
    csv_path = tmp_path / "rows.csv"

    app = RootLocusApp()
    result = app.run(
        example="ogata_8_1",
        backend="plotly",
        save=None,  # headless path
        export_json=str(json_path),
        export_csv=str(csv_path),
        # cfg kwargs
        zeta_values=[0.6, 0.7],
        omega=(0.2, 2.0, 20),
        # request-only kwargs
        analyze=False,
        settle=0.03,
        precision=5,
    )
    assert result["json_path"]
    assert Path(result["json_path"]).exists()
    assert result["csv_path"]
    assert Path(result["csv_path"]).exists()
    # Ensure fields exist
    assert "summary" in result and "a_plot" in result
