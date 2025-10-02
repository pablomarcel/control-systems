# frequencyResponse/plotTool/tests/test_app_apis_cli_paths.py

import os, sys, subprocess, inspect
from types import SimpleNamespace
from pathlib import Path

PY = sys.executable

def _env(extra=None):
    """
    Build a consistent environment for CLI subprocess calls.
    We keep this noisy by default with PLOTTOOL_DEBUG=1.
    """
    env = os.environ.copy()
    env.setdefault("PLOTTOOL_DEBUG", "1")
    env.setdefault("PYTHONWARNINGS", "default")
    # Force headless plotting to avoid GUI flakiness on CI/macOS
    env.setdefault("MPLBACKEND", "Agg")
    # Headless plotly renderer; callers can override
    env.setdefault("PLOTLY_RENDERER", "none")
    if extra:
        env.update(extra)
    return env

def _run(cmd, cwd=None, env=None, timeout=90):
    """
    Run a subprocess with maximum verbosity so failures are easy to debug.
    """
    print("\n[RUN] CWD:", cwd or os.getcwd())
    print("[RUN] ENV DIFF:", {k:v for k,v in (env or {}).items()
           if k in ("PLOTTOOL_DEBUG","MPLBACKEND","PLOTLY_RENDERER")})
    print("[RUN] CMD:", " ".join(cmd))
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    print("[RUN] RC:", p.returncode)
    print("[RUN] STDOUT:\n", p.stdout)
    print("[RUN] STDERR:\n", p.stderr)
    return p

def test_cli_help_runs():
    p = _run([PY, "-m", "frequencyResponse.plotTool.cli", "-h"], env=_env())
    assert p.returncode == 0

def test_cli_plotly_and_mpl_outputs(tmp_path):
    base = tmp_path / "out"
    base.mkdir(exist_ok=True)

    # Plotly Nichols (save HTML)
    cmd1 = [
        PY, "-m", "frequencyResponse.plotTool.cli",
        "--fnum", "K", "--fden", "s (s+1) (0.5*s+1)", "--K", "1",
        "--nichols", "--nichols-grid", "--nichols-closedloop", "--plotly",
        "--nichols-range=-240,0,-16,32",
        "--save-html", str(base / "nichols_quick")
    ]
    p1 = _run(cmd1, env=_env())
    assert p1.returncode == 0
    htmls = sorted(str(p) for p in base.glob("*nichols*.html"))
    print("[CHK] HTMLs:", htmls)
    assert htmls, "Expected nichols html"

    # Matplotlib Bode (save PNGs)
    cmd2 = [
        PY, "-m", "frequencyResponse.plotTool.cli",
        "--fnum", "K", "--fden", "s (s+1) (0.5*s+1)", "--K", "1",
        "--wmin", "0.1", "--wmax", "2", "--npts", "100",
        "--bode",
        "--save-png", str(base / "figs")
    ]
    p2 = _run(cmd2, env=_env())
    assert p2.returncode == 0
    pngs = sorted(str(p) for p in (base / "figs").glob("*.png"))
    print("[CHK] PNGs:", pngs)
    assert pngs, "Expected at least one PNG"

def test_apis_direct_call(tmp_path, monkeypatch):
    """
    Exercise PlotService directly (without subprocess).
    Be robust to historical signature variants and keep it VERY noisy.
    """
    from frequencyResponse.plotTool.app import PlotToolApp
    from frequencyResponse.plotTool.apis import PlotService

    # Headless & verbose
    monkeypatch.setenv("PLOTTOOL_DEBUG","1")
    monkeypatch.setenv("MPLBACKEND","Agg")

    app = PlotToolApp()
    svc = PlotService(app)

    # Build args fed to svc.run(...)
    args = SimpleNamespace(
        # plant / model spec
        num=None, den=None, gain=None, zeros=None, poles=None,
        fnum="K", fden="s (s+1) (0.5*s+1)", K=1.0,
        A=None, B=None, C=None, D=None,
        # frequency sweep & options
        scale=None, wmin=0.1, wmax=2.0, npts=100,
        bode=True, nyquist=False, nichols=True, nichols_grid=True, nichols_closedloop=True,
        nyq_markers=False, nyq_samples=0,
        plotly=False, wmarks=None, nichols_range="-240,0,-16,32",
        nichols_Mdb=None, nichols_Mdb_csv=None, nichols_Ndeg=None, nichols_Ndeg_csv=None, nichols_no_grid_labels=False,
        # outputs (CLI normally converts these into *computed* fields)
        save_png=str(tmp_path),
        save_html=None,
        save_json=str(Path(tmp_path) / "cov.json"),
        title="cov run", verbose=0
    )

    # ---- Mimic CLI-computed request fields ----
    # apis.run() expects these precomputed attributes (CLI usually fills them).
    args.save_png_dir = str(tmp_path)                     # where PNGs should go
    args.save_html_dir = str(tmp_path)                    # where HTML should go (unused here)
    args.save_json_path = str(Path(tmp_path) / "cov.json")# JSON summary path
    # -------------------------------------------

    # Signature displayed here will NOT include `self` (bound method behavior).
    sig = inspect.signature(svc.run)
    print("[DIRECT] svc.run signature:", str(sig))
    print("[DIRECT] Using args:", args)

    # Try the known variants in a safe order.
    call_errors = []
    variants = [
        ("run(args, args)", lambda: svc.run(args, args)),             # current expected usage path
        ("run(args)",       lambda: svc.run(args)),                   # legacy impl:  run(self, req)
        ("run(app, args)",  lambda: svc.run(app, args)),              # older impl:   run(self, app, req)
    ]
    for label, fn in variants:
        try:
            print(f"[DIRECT] Trying {label} ...")
            fn()
            print(f"[DIRECT] {label} -> OK")
            break
        except TypeError as e:
            print(f"[DIRECT] {label} -> TypeError: {e}")
            call_errors.append((label, e))
        except Exception as e:
            print(f"[DIRECT] {label} -> Exception: {type(e).__name__}: {e}")
            call_errors.append((label, e))
    else:
        msgs = "\n".join([f"  {lab}: {err}" for lab, err in call_errors])
        raise AssertionError("All PlotService.run variants failed:\n" + msgs)

    # Verify files were written by the direct call
    created = sorted(str(p) for p in Path(tmp_path).glob("*.png"))
    print("[DIRECT] Created PNGs:", created)
    assert created, "Expected PNG outputs from direct svc.run"
