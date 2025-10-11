import types
from pidControllers.pidTool import cli

def test_cli_main_unit(monkeypatch):
    # Replace PIDDesignerApp with a stub to avoid heavy work
    class StubApp:
        def __init__(self, out_dir=None): pass
        def run(self, **kwargs): return 42

    monkeypatch.setattr(cli, "PIDDesignerApp", StubApp)

    argv = [
        "run",
        "--plant-form","coeff",
        "--num","1 0",
        "--den","1 1",
        "--structure","pid_dz",
        "--K-range","1","1","--K-n","1",
        "--a-range","1","1","--a-n","1",
        "--backend","none",
        "--save-prefix","unit_cli"
    ]
    # Should execute without raising (returns None)
    cli.main(argv)
    # Also hit the parser path directly
    p = cli.build_parser()
    assert p is not None
