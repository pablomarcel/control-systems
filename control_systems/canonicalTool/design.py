
# design.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List
import numpy as np
import control as ct
from .core import CanonicalForms
from .utils import normalize_tf_coeffs, tf_equal

@dataclass(slots=True)
class RunResult:
    sys_ccf: ct.StateSpace
    sys_ocf: ct.StateSpace
    sys_modal: ct.StateSpace
    equal_ocf: bool
    equal_modal: bool
    pretty_tf: str

class CanonicalDesigner:
    """High-level orchestration for running a conversion "design"."""
    def run(self, num: list[float], den: list[float]) -> RunResult:
        num_n, den_n = normalize_tf_coeffs(num, den)
        sys_ccf = CanonicalForms.ccf_from_tf(num_n, den_n)
        sys_ocf = CanonicalForms.ocf_from_ss(sys_ccf)
        sys_modal = CanonicalForms.modal_real(sys_ccf)
        equal_ocf = tf_equal(sys_ocf, sys_ccf)
        equal_modal = tf_equal(sys_modal, sys_ccf)
        tf_str = ct.TransferFunction(num_n, den_n).__str__()
        return RunResult(
            sys_ccf=sys_ccf, sys_ocf=sys_ocf, sys_modal=sys_modal,
            equal_ocf=equal_ocf, equal_modal=equal_modal, pretty_tf=tf_str
        )
