
from stateSpaceDesign.minOrdTool import cli

def test_coalesce_and_split_helpers():
    argv = ["--A","0 1; -2 -3","--C","1 0","--poles","-10","-10","--export-json","x.json"]
    fixed = cli._coalesce_negatives(argv)
    assert any(arg.startswith("--poles=") for arg in fixed)
    out = cli._split_commas(["-10,-10","-12"])
    assert out == ["-10","-10","-12"]
