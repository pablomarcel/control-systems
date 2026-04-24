from __future__ import annotations
from frequency_response.compensatorTool.apis import (
    PlantSpec,
    PlotOptions,
    FrequencyGrid,
    LagDesignSpec,
    LagDesignOptions,
)
from frequency_response.compensatorTool.lag import LagDesigner


def test_lag_api_design_minimal():
    plant = PlantSpec(num="4", den="1, 2, 0")
    opts = LagDesignOptions(pm_target=45.0, pm_add=8.0)
    plot = PlotOptions(backend="mpl", plots="bode", no_show=True)
    spec = LagDesignSpec(plant=plant, design=opts, plot=plot, grid=FrequencyGrid())

    res = LagDesigner().run(spec)

    assert isinstance(res.pack, dict)
    # Basic contents
    assert "comp_margins" in res.pack
    assert "uncomp_margins" in res.pack or "uncomp_margins" in res.pack.get("margins", {})
    assert "lag" in res.pack

    lagblk = res.pack["lag"]
    assert "Kc" in lagblk  # always present
    # Accept either flat fields or staged payloads
    flat_keys = {"beta", "T", "wz", "wp"}
    if flat_keys.issubset(lagblk.keys()):
        # flat structure
        for k in flat_keys:
            assert k in lagblk
    else:
        # staged structure
        assert "stages" in lagblk
        stages = lagblk["stages"]
        assert isinstance(stages, (list, tuple)) and len(stages) >= 1
        stage0 = stages[0]
        for k in ["beta", "T", "wz", "wp"]:
            assert k in stage0
