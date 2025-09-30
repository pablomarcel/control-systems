# transientAnalysis/responseTool/tests/test_cli_second_order_plotly.py
from __future__ import annotations
import json
import subprocess
import sys
from glob import glob
from pathlib import Path

import pytest


def run_cmd(args: list[str]) -> tuple[int, str]:
    """Run the CLI module with given args; return (exit_code, combined_output)."""
    cmd = [sys.executable, "-m", "transientAnalysis.responseTool.cli"] + args
    proc = subprocess.run(cmd, text=True, capture_output=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out


@pytest.mark.skipif(
    pytest.importorskip("plotly", reason="plotly not installed") is None,
    reason="plotly not installed",
)
def test_second_order_plotly_smoke(tmp_path: Path):
    # Prefer writing under tmp/out, but accept the package default out/ fallback
    root = tmp_path
    save_prefix = "plotly_demo"

    code, out = run_cmd([
        "--root", str(root),
        "second-order-plotly",
        "--wn", "2",
        "--zeta-steps", "21",
        "--tfinal", "3",
        "--dt", "0.02",
        "--save-prefix", save_prefix,
        # no HTML/PNG to avoid kaleido dependency
    ])
    assert code == 0, f"CLI failed:\n{out}"

    # Primary search location: tmp/out
    out_dir = root / "out"
    expected = out_dir / f"{save_prefix}_plotly3D.json"
    candidates = [expected, *[Path(p) for p in glob(str(out_dir / "*_plotly3D.json"))]]

    # Fallback: package default out/ (if the CLI/subcommand ignored --root)
    try:
        import transientAnalysis.responseTool as rt_pkg
        pkg_out = Path(rt_pkg.__file__).resolve().parent / "out"
        candidates.extend(
            [pkg_out / f"{save_prefix}_plotly3D.json"] +
            [Path(p) for p in glob(str(pkg_out / "*_plotly3D.json"))]
        )
    except Exception:
        pass  # if import/path resolution fails, just skip the fallback

    jpath = next((p for p in candidates if p.exists()), None)
    assert jpath is not None, (
        "Plotly JSON snapshot not found.\n"
        f"Looked under: {out_dir} and package default 'responseTool/out/'.\n"
        f"CLI output:\n{out}"
    )

    # Minimal schema validation
    data = json.loads(jpath.read_text())
    assert {"wn", "T", "zeta_grid", "Z", "overlay", "title"} <= set(data), "JSON schema keys missing"

    Nz = len(data["zeta_grid"])
    Nt = len(data["T"])
    assert isinstance(data["Z"], list) and len(data["Z"]) == Nz, "Z rows != len(zeta_grid)"
    assert all(isinstance(row, list) and len(row) == Nt for row in data["Z"]), "Z row length != len(T)"
