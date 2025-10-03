
from __future__ import annotations
import numpy as np
import control as ct
from frequencyResponse.compensatorTool.design import LagLeadDesigner
from frequencyResponse.compensatorTool.app import CompensatorApp
from frequencyResponse.compensatorTool.apis import PlantSpec, DesignOptions, PlotOptions, FrequencyGrid, LagLeadDesignSpec

def test_auto_design_path_and_run_no_plots(tmp_path):
    G = ct.tf([1.0], [1.0, 1.0, 0.0])  # type-1
    # Use the API objects to run through design path with no plots, json only
    plant = PlantSpec(tf_expr="1/(s*(s+1))", params="")
    design = DesignOptions(Kv=4.0, pm_target=50.0, pm_allow=5.0, wc_hint=None)
    plot = PlotOptions(backend="mpl", plots="",
                       export_json=str(tmp_path/"pack.json"), no_show=True)
    spec = LagLeadDesignSpec(plant=plant, design=design, plot=plot, grid=FrequencyGrid())
    app = CompensatorApp()
    res = app.run(spec)
    assert (tmp_path/"pack.json").exists()
    assert "comp_margins" in res.pack
    assert isinstance(res.files, list)

def test_preset_ogata_7_28_and_files(tmp_path):
    # Exercise the preset path with some plots
    from frequencyResponse.compensatorTool.app import CompensatorApp
    from frequencyResponse.compensatorTool.apis import PlantSpec, DesignOptions, PlotOptions, FrequencyGrid, LagLeadDesignSpec
    plant = PlantSpec(tf_expr=None, params="")
    design = DesignOptions(ogata_7_28=True)
    plot = PlotOptions(backend="mpl", plots="bode,nyquist,nichols", no_show=True,
                       save=str(tmp_path/"og728_{kind}.png"), nichols_templates=True)
    spec = LagLeadDesignSpec(plant=plant, design=design, plot=plot, grid=FrequencyGrid())
    app = CompensatorApp()
    res = app.run(spec)
    # At least one file saved
    assert any(p.endswith(".png") for p in res.files)
