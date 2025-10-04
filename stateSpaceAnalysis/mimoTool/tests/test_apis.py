import os, json
from stateSpaceAnalysis.mimoTool import apis

def test_apis_describe_two_tank():
    info = apis.describe(apis.DescribeRequest(plant="two_tank"))
    assert set(["A","B","C","D","poles","ninputs","noutputs"]).issubset(info.keys())
    assert info["ninputs"] == 2 and info["noutputs"] == 2

def test_apis_sigma_and_steps_save(tmp_path):
    # sigma save
    path = apis.sigma(apis.SigmaRequest(plant="two_zone_thermal", save=True, out_name="sigma_tt.png"))
    assert path.endswith("sigma_tt.png")
    assert os.path.exists(path)

    # steps save (creates two images, one per input; names include u{idx})
    out_paths = apis.steps(apis.StepRequest(plant="two_tank", tfinal=2.0, dt=0.5, save=True, out_prefix="tt"))
    assert len(out_paths) >= 1
    for p in out_paths:
        assert os.path.exists(p)
