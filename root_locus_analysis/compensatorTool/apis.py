# modernControl/root_locus_analysis/compensatorTool/apis.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Tuple
import math
import control as ct

from .utils import parse_list
from .design import design_independent_case, design_coupled_case, DesignResult

Case = Literal["indep", "coupled"]


@dataclass(slots=True)
class PoleSpec:
    """Desired location, provided either directly or via (zeta, wn)."""
    sstar: complex
    desc: str  # ASCII only for robust CLI output

    @staticmethod
    def from_zeta_wn(zeta: float, wn: float) -> "PoleSpec":
        if not (0 < zeta < 1) or wn <= 0:
            raise ValueError("Provide 0<zeta<1 and wn>0")
        sigma = -zeta * wn
        wd = wn * math.sqrt(1 - zeta**2)
        # ASCII description to avoid UnicodeEncodeError in constrained stdout envs
        return PoleSpec(complex(sigma, wd), f"zeta={zeta:g}, wn={wn:g}")

    @staticmethod
    def from_parts(sreal: float, wimag: float) -> "PoleSpec":
        if wimag < 0:
            raise ValueError("wimag must be >= 0")
        sign = "+" if wimag >= 0 else "-"
        return PoleSpec(complex(sreal, wimag), f"s*={sreal:+.6g} {sign} j{abs(wimag):.6g}")


class CompensatorService:
    """Façade for compensator design. Test-oriented and dependency-light."""
    def design(
        self,
        case: Case,
        num: str,
        den: str,
        pole: PoleSpec,
        *,
        lead_method: str = "bisector",
        cancel_at: float | None = None,
        manual_lead: Tuple[float, float] | None = None,
        nlead: int = 1,
        phi_per_lead: float | None = None,
        phi_cap: float = 60.0,
        auto_nlead: bool = True,
        err: str = "kv",
        target: float | None = None,
        factor: float | None = None,
        beta: float | None = None,
        T2: float | None = None,
        thetamax: float = 5.0,
        magwin: tuple[float, float] = (0.98, 1.02),
        T2max: float = 1000.0,
    ) -> DesignResult:
        G = ct.tf(parse_list(num), parse_list(den))
        if case == "coupled":
            if target is None:
                raise ValueError("Coupled case requires target for Kp/Kv/Ka")
            return design_coupled_case(
                G=G,
                sstar=pole.sstar,
                nlead=nlead,
                phi_per_lead_deg=phi_per_lead,
                phi_cap_deg=phi_cap,
                auto_nlead=auto_nlead,
                thetamax=thetamax,
                T2_user=T2,
                magwin=magwin,
                T2max=T2max,
                err_kind=err,
                target=target,
            )
        else:
            return design_independent_case(
                G=G,
                sstar=pole.sstar,
                lead_method=lead_method,
                cancel_at=cancel_at,
                manual_lead=manual_lead,
                nlead=nlead,
                phi_per_lead_deg=phi_per_lead,
                phi_cap_deg=phi_cap,
                auto_nlead=auto_nlead,
                err_kind=err,
                target=target,
                factor=factor,
                beta_user=beta,
                T2_user=T2,
                thetamax=thetamax,
                magwin=magwin,
                T2max=T2max,
            )
