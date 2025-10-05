from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Literal, Dict, Any, Iterable
import numbers

PlotsMode = Literal["mpl", "plotly", "both", "none"]
PrefilterMode = Literal["ogata", "dcgain", "none"]

@dataclass
class LQRRunRequest:
    # system definition (exclusive OR between tf and abcd paths)
    A: Optional[str] = None
    B: Optional[str] = None
    C: Optional[str] = None
    D: Optional[str] = "0"
    num: Optional[str] = None
    den: Optional[str] = None
    # weights
    Q: str = "eye"
    R: str = "1"
    # simulations
    x0: Optional[str] = None
    step: bool = False
    step_amp: float = 1.0
    prefilter: PrefilterMode = "dcgain"
    tfinal: float = 8.0
    dt: float = 0.01
    # output
    plots: PlotsMode = "mpl"

    def to_jsonable(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LQRRunResult:
    K: list                 # list[list[float]]
    P: list                 # list[list[float]]
    eig_cl: list            # list[complex] or list[list[complex]]
    prefilter_gain: float | None
    rank_ctrb: int
    note: str = ""

    @staticmethod
    def _c_to_pair(z) -> list[float] | float:
        """Convert a complex or real value into JSON-safe form."""
        if isinstance(z, complex):
            return [float(z.real), float(z.imag)]
        # numpy scalars/numbers -> float
        if isinstance(z, numbers.Number):
            return float(z)
        return z

    @classmethod
    def _eigs_to_pairs(cls, eigs) -> list:
        """Map eigenvalues (possibly nested) to [re, im] pairs."""
        out = []
        # support flat or nested lists
        if isinstance(eigs, (list, tuple)):
            for item in eigs:
                if isinstance(item, (list, tuple)):
                    out.append([cls._c_to_pair(x) for x in item])
                else:
                    out.append(cls._c_to_pair(item))
        else:
            out = [cls._c_to_pair(eigs)]
        return out

    def to_jsonable(self) -> Dict[str, Any]:
        return {
            "K": self.K,
            "P": self.P,
            "eig": self._eigs_to_pairs(self.eig_cl),
            "prefilter_gain": (float(self.prefilter_gain) if self.prefilter_gain is not None else None),
            "rank_ctrb": int(self.rank_ctrb),
            "note": self.note,
        }
