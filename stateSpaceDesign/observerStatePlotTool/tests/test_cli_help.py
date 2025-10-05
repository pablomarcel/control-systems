from stateSpaceDesign.observerStatePlotTool.cli import build_parser

def test_cli_help_runs(capsys):
    parser = build_parser()
    # Simulate "--help" by checking that parser exists and has expected options
    txt = parser.format_help()
    assert "Observer/Controller state plotter" in txt
    assert "--data" in txt
    assert "--simulate_if_missing" in txt
