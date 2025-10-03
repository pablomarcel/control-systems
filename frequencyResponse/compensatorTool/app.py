from __future__ import annotations
import logging
from dataclasses import dataclass

from .apis import (
    LagLeadDesignSpec,
    LeadDesignSpec,
)
from .design import LagLeadDesigner
from .lead import LeadDesigner


@dataclass(slots=True)
class CompensatorApp:
    def run(self, spec):
        """
        Dispatch to the appropriate designer based on the spec type.
        - LagLeadDesignSpec -> LagLeadDesigner
        - LeadDesignSpec    -> LeadDesigner
        """
        logging.getLogger().setLevel(logging.INFO)

        if isinstance(spec, LeadDesignSpec):
            designer = LeadDesigner()
            return designer.run(spec)

        if isinstance(spec, LagLeadDesignSpec):
            designer = LagLeadDesigner()
            return designer.run(spec)

        raise TypeError(
            f"Unsupported spec type: {type(spec).__name__}. "
            "Expected LagLeadDesignSpec or LeadDesignSpec."
        )

    @staticmethod
    def spec_ogata_7_28(
        *,
        backend: str = "mpl",
        plots: str = "bode,nyquist,nichols",
        save: str | None = None,
        no_show: bool = True,
    ) -> LagLeadDesignSpec:
        """
        Convenience builder for the Ogata 7-28 preset (lag–lead).
        """
        from .apis import PlantSpec, DesignOptions, PlotOptions, FrequencyGrid, LagLeadDesignSpec

        plant = PlantSpec(tf_expr=None, params="")
        design = DesignOptions(ogata_7_28=True)
        plot = PlotOptions(
            backend=backend,
            plots=plots,
            ogata_axes=True,
            nichols_templates=True,
            save=save,
            no_show=no_show,
        )
        return LagLeadDesignSpec(plant=plant, design=design, plot=plot, grid=FrequencyGrid())
