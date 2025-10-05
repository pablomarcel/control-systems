from __future__ import annotations
from .apis import RunRequest, RunResponse, run

class ServoApp:
    """Thin orchestrator for external integrations (GUIs, notebooks)."""
    def __init__(self):
        pass

    def execute(self, **kwargs) -> RunResponse:
        req = RunRequest(**kwargs)
        return run(req)
