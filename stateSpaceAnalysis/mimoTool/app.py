"""
App orchestrator for typical workflows.
"""
from __future__ import annotations
from .apis import DescribeRequest, StepRequest, SigmaRequest, describe, steps, sigma

class MIMOToolApp:
    def run_describe(self, plant: str) -> dict:
        return describe(DescribeRequest(plant=plant))  # type: ignore[arg-type]

    def run_steps(self, plant: str, tfinal=100.0, dt=0.1, save=False, out_prefix=None):
        return steps(StepRequest(plant=plant, tfinal=tfinal, dt=dt, save=save, out_prefix=out_prefix))  # type: ignore[arg-type]

    def run_sigma(self, plant: str, save=False, out_name=None):
        return sigma(SigmaRequest(plant=plant, save=save, out_name=out_name))  # type: ignore[arg-type]
