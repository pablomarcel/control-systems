
from __future__ import annotations

import os
from pathlib import Path

from root_locus_analysis.systemResponseTool.apis import RunRequest, SystemResponseService

def test_service_runs_minimal(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "1")
    svc = SystemResponseService(in_dir=tmp_path/"in", out_dir=tmp_path/"out", show_plots=False)

    req = RunRequest(
        sys_args=["tf; name=G; num=1; den=1,1; fb=none"],
        responses=["step"],
        tfinal=0.2,
        dt=0.05,
        out_prefix=str(tmp_path/"out"/"svc_demo"),
        title="svc",
    )
    svc.run(req)
    assert (tmp_path/"out/svc_demo_step.csv").exists()
    assert (tmp_path/"out/svc_demo_step.html").exists()
