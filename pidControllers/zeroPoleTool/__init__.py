"""
zeroPoleTool — Two‑DOF zero/pole placement controller design (Ogata §8‑7)
Object‑oriented, testable architecture for modernControl/pidControllers.
"""

from .apis import ZeroPoleAPI, Candidate, StepMetrics
from .app import ZeroPoleApp
