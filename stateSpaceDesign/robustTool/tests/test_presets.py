from stateSpaceDesign.robustTool.tools.presets import OGATA_10_7_EXAMPLE

def test_presets_has_expected_keys():
    assert "plant" in OGATA_10_7_EXAMPLE
    assert "leadlag" in OGATA_10_7_EXAMPLE
    assert "weights" in OGATA_10_7_EXAMPLE
