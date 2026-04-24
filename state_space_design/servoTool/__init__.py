"""
state_space_design.servoTool
--------------------------
OOP refactor of `servos.py` for MIMO/servo I/O model construction.

Entry point:
    python -m state_space_design.servoTool.cli --help

Key modules:
    - core:        dataclasses & enums for payloads and I/O models
    - design:      ServoSynthesizer implementing K & KI flows
    - io:          loading/saving JSON/CSV, path helpers
    - apis:        stable API surface for programmatic use (TDD-friendly)
    - app:         thin orchestration wrapper (keeps CLI skinny)
    - cli:         argparse front-end (no business logic inside)
    - utils:       small helpers, shape checks, safe casting
    - tools:       optional plotting helpers (kept minimal)
"""

from .core import ServoMode, ControllerPayload, ServoIOModel
from .design import ServoSynthesizer
from .apis import RunRequest, RunResponse, run

__all__ = [
    "ServoMode",
    "ControllerPayload",
    "ServoIOModel",
    "ServoSynthesizer",
    "RunRequest",
    "RunResponse",
    "run",
]
