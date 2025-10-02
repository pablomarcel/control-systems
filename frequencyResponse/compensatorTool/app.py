
from __future__ import annotations
import logging
from dataclasses import dataclass
from .apis import LagLeadDesignSpec
from .design import LagLeadDesigner

@dataclass(slots=True)
class CompensatorApp:
    def run(self, spec: LagLeadDesignSpec):
        logging.getLogger().setLevel(logging.INFO)
        designer = LagLeadDesigner()
        return designer.run(spec)

    @staticmethod
    def spec_ogata_7_28(*, backend='mpl', plots='bode,nyquist,nichols', save=None, no_show=True):
        from .apis import PlantSpec, DesignOptions, PlotOptions, FrequencyGrid, LagLeadDesignSpec
        plant = PlantSpec(tf_expr=None, params='')
        design = DesignOptions(ogata_7_28=True)
        plot = PlotOptions(backend=backend, plots=plots, ogata_axes=True, nichols_templates=True, save=save, no_show=no_show)
        return LagLeadDesignSpec(plant=plant, design=design, plot=plot, grid=FrequencyGrid())
