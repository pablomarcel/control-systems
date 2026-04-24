from __future__ import annotations
from state_space_analysis.stateTool.apis import StateSpaceAnalyzerAPI, RunOptions, AnalyzerMode

def test_api_end_to_end_state():
    api = StateSpaceAnalyzerAPI()
    model, tf_desc = api.build_from_state("0 1; -2 -3", "0;1", "3 1", "0")
    opts = RunOptions(mode=AnalyzerMode.ALL, pretty=False)
    summary = api.analyze(model, opts, tf_desc)
    assert "state" in summary.results
    assert "obs" in summary.results

def test_api_end_to_end_tf():
    api = StateSpaceAnalyzerAPI()
    model, tf_desc = api.build_from_tf(tf="(s+3)/(s^2+3*s+2)")
    opts = RunOptions(mode=AnalyzerMode.ALL, pretty=False)
    summary = api.analyze(model, opts, tf_desc)
    assert "splane" in summary.results
    assert "obssplane" in summary.results
