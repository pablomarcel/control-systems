from __future__ import annotations
from frequency_response.compensatorTool.apis import (
    PlantSpec, LeadDesignOptions, LeadDesignSpec, PlotOptions, FrequencyGrid
)
from frequency_response.compensatorTool.app import CompensatorApp

def test_lead_api_design_minimal():
    plant = PlantSpec(num="4", den="1, 2, 0")
    opts = LeadDesignOptions(pm_target=50.0, pm_add=5.0, stages=1)
    plot = PlotOptions(backend="mpl", plots="bode", no_show=True)
    spec = LeadDesignSpec(plant=plant, design=opts, plot=plot, grid=FrequencyGrid())
    res = CompensatorApp().run(spec)
    assert 'comp_margins' in res.pack
    assert 'lead' in res.pack
    assert isinstance(res.pack['lead']['stages'], list)
