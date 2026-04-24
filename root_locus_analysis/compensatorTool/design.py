from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Literal
import math
import numpy as np
import control as ct

from .utils import LOG, tf_arrays, polyval, error_constants
from .core import (
    LeadStage, angle_deficiency, lead_from_bisector_validated, solve_p_for_angle,
    repair_lead_by_scan, lag_angle_mag, choose_T2, Gc_from_chain
)

Case = Literal["independent", "coupled"]

@dataclass(slots=True)
class DesignResult:
    case: Case
    sstar: complex
    Kc: float
    leads: List[LeadStage]
    T2: float
    beta: float
    Gc: ct.TransferFunction
    L: ct.TransferFunction
    before: dict
    after: dict


def design_lead_chain_sequential(G: "ct.TransferFunction", sstar: complex,
                                 nlead: int, phi_per_lead_deg: float | None,
                                 method: str, cancel_at: float | None) -> List[LeadStage]:
    leads: List[LeadStage] = []
    L_partial = G
    for k in range(nlead):
        phi_need = angle_deficiency(L_partial, sstar)
        if k == nlead - 1:
            phi_k = phi_need
        else:
            if phi_per_lead_deg is not None:
                phi_k = min(math.radians(phi_per_lead_deg), phi_need * 0.999)
            else:
                phi_k = phi_need / float(nlead - k)
        if method == "cancel" and k == 0:
            if cancel_at is None:
                raise ValueError("--lead-method cancel requires --cancel-at for stage 1.")
            z = abs(float(-cancel_at))
            p = solve_p_for_angle(sstar, phi_k, z)
            if p is None or not (p > z):
                z, p = repair_lead_by_scan(sstar, phi_k)
        else:
            z, p = lead_from_bisector_validated(sstar, phi_k)
        T1 = 1.0 / z; gamma = p / z
        leads.append(LeadStage(T1=T1, gamma=gamma, z=z, p=p))
        L_partial = ct.minreal(L_partial * ct.tf([1.0, z], [1.0, p]), verbose=False)
    return leads


def design_independent_case(G: "ct.TransferFunction",
                            sstar: complex,
                            lead_method: str,
                            cancel_at: float | None,
                            manual_lead: Tuple[float, float] | None,
                            nlead: int,
                            phi_per_lead_deg: float | None,
                            phi_cap_deg: float,
                            auto_nlead: bool,
                            err_kind: str,
                            target: float | None,
                            factor: float | None,
                            beta_user: float | None,
                            T2_user: float | None,
                            thetamax: float,
                            magwin: Tuple[float, float],
                            T2max: float) -> DesignResult:
    phi_total = angle_deficiency(G, sstar)
    phi_total_deg = math.degrees(phi_total)
    LOG.info("Angle deficiency (plant-only) at s*: phi = %.3f deg", phi_total_deg)

    if nlead < 1:
        nlead = 1
    if phi_per_lead_deg is not None and (nlead * phi_per_lead_deg + 1e-6) < phi_total_deg:
        if auto_nlead:
            nlead_new = int(math.ceil(phi_total_deg / phi_per_lead_deg))
            LOG.info("Auto-increasing number of leads: %d -> %d to cover total %.2f deg",
                     nlead, nlead_new, phi_total_deg)
            nlead = nlead_new
        else:
            raise RuntimeError(
                f"Insufficient total phase: nlead*phi-per-lead = {nlead*phi_per_lead_deg:.2f} deg < {phi_total_deg:.2f} deg. "
                f"Increase --nlead or --phi-per-lead or use --auto-nlead."
            )

    if phi_per_lead_deg is None:
        if (phi_total_deg / nlead) > phi_cap_deg + 1e-6:
            if auto_nlead:
                nlead_new = int(math.ceil(phi_total_deg / phi_cap_deg))
                LOG.info("Auto-increasing nlead for phi_cap %.1f deg: %d -> %d",
                         phi_cap_deg, nlead, nlead_new)
                nlead = nlead_new
            else:
                raise RuntimeError(
                    f"Per-lead phase would exceed cap {phi_cap_deg} deg. "
                    f"Provide --nlead or --phi-per-lead or use --auto-nlead."
                )

    if lead_method == "manual":
        if manual_lead is None:
            raise ValueError("Manual lead requires --lead-z & --lead-p OR --T1 & --gamma (single lead only).")
        z, p = manual_lead
        if not (p > z > 0):
            raise ValueError("Require p>z>0 for manual lead.")
        leads = [LeadStage(T1=1.0 / z, gamma=p / z, z=z, p=p)]
    else:
        leads = design_lead_chain_sequential(G, sstar, nlead, phi_per_lead_deg, lead_method, cancel_at)

    nG, dG = tf_arrays(G)
    Lmag = abs(polyval(nG, sstar) / polyval(dG, sstar))
    prod_ratio = 1.0
    for Ld in leads:
        prod_ratio *= abs((sstar + 1.0 / Ld.T1) / (sstar + Ld.gamma / Ld.T1))
    Kc_lead = 1.0 / (Lmag * prod_ratio)

    base = error_constants(G)
    keymap = {"kp": "Kp", "kv": "Kv", "ka": "Ka"}
    key = keymap[err_kind.lower()]
    base_const = base[key]
    gamma_prod = float(np.prod([Ld.gamma for Ld in leads]))
    if beta_user is not None:
        beta = float(beta_user)
        if beta <= 1.0:
            raise ValueError("beta must be > 1.")
        LOG.info("Using user beta = %.6g", beta)
    else:
        if target is not None:
            if not np.isfinite(base_const) or base_const <= 0:
                raise ValueError(f"Cannot size beta from target: current {key} for plant is {base_const}.")
            beta = (gamma_prod * float(target)) / (Kc_lead * float(base_const))
        elif factor is not None:
            if factor <= 1.0:
                raise ValueError("--factor must be > 1.")
            beta = (float(factor) * gamma_prod) / Kc_lead
        else:
            beta = 10.0
        if beta <= 1.0:
            raise RuntimeError(f"Computed beta={beta:.3g} <= 1. Revisit N or specs.")
        LOG.info("beta sized from steady-state: beta = %.6g", beta)

    if T2_user is not None:
        T2 = float(T2_user)
        ang, mag = lag_angle_mag(sstar, beta, T2)
        LOG.info("Using user T2=%.6g -> lag angle %.3g deg, |.|=%.4g at s*", T2, ang, mag)
    else:
        T2 = choose_T2(sstar, beta, thetamax_deg=thetamax, mag_lo=magwin[0], mag_hi=magwin[1], T2max=T2max)
        ang, mag = lag_angle_mag(sstar, beta, T2)
        LOG.info("Auto T2=%.6g so lag angle %.3g deg, |.|=%.4g at s*", T2, ang, mag)

    lag_mag = abs((sstar + 1.0 / T2) / (sstar + 1.0 / (beta * T2)))
    Kc = Kc_lead / lag_mag

    Gc = Gc_from_chain(Kc, leads, T2, beta)
    L = ct.minreal(Gc * G, verbose=False)
    return DesignResult(case="independent", sstar=sstar, Kc=Kc, leads=leads, T2=T2, beta=beta,
                        Gc=ct.minreal(Gc, verbose=False), L=L,
                        before=error_constants(G), after=error_constants(L))


def design_coupled_case(G: "ct.TransferFunction",
                        sstar: complex,
                        nlead: int,
                        phi_per_lead_deg: float | None,
                        phi_cap_deg: float,
                        auto_nlead: bool,
                        thetamax: float,
                        T2_user: float | None,
                        magwin: Tuple[float, float],
                        T2max: float,
                        err_kind: str, target: float) -> DesignResult:
    keymap = {"kp": "Kp", "kv": "Kv", "ka": "Ka"}
    base = error_constants(G)
    key = keymap[err_kind.lower()]
    base_const = base[key]
    if not np.isfinite(base_const) or base_const <= 0:
        raise ValueError(f"Cannot size Kc: plant {key} is {base_const}.")
    Kc = float(target) / float(base_const)
    LOG.info("Coupled case: Kc = target/%s(plant) = %.6g", key, Kc)

    phi_total = angle_deficiency(G, sstar)
    phi_total_deg = math.degrees(phi_total)
    if nlead < 1:
        nlead = 1
    if phi_per_lead_deg is not None and (nlead * phi_per_lead_deg + 1e-6) < phi_total_deg:
        if auto_nlead:
            nlead_new = int(math.ceil(phi_total_deg / phi_per_lead_deg))
            LOG.info("Auto-increasing number of leads: %d -> %d to cover total %.2f deg",
                     nlead, nlead_new, phi_total_deg)
            nlead = nlead_new
        else:
            raise RuntimeError(
                f"Insufficient total phase: nlead*phi-per-lead = {nlead*phi_per_lead_deg:.2f} deg < {phi_total_deg:.2f} deg."
            )

    if phi_per_lead_deg is None and (phi_total_deg / nlead) > phi_cap_deg + 1e-6:
        if auto_nlead:
            nlead_new = int(math.ceil(phi_total_deg / phi_cap_deg))
            LOG.info("Auto-increasing nlead for phi_cap %.1f deg: %d -> %d",
                     phi_cap_deg, nlead, nlead_new)
            nlead = nlead_new
        else:
            raise RuntimeError(
                f"Per-lead phase would exceed cap {phi_cap_deg} deg. "
                f"Provide --nlead or --phi-per-lead or use --auto-nlead."
            )

    leads = design_lead_chain_sequential(G, sstar, nlead, phi_per_lead_deg, "bisector", None)

    gamma_prod = float(np.prod([Ld.gamma for Ld in leads]))
    beta = gamma_prod
    if T2_user is not None:
        T2 = float(T2_user)
        ang, mag = lag_angle_mag(sstar, beta, T2)
        LOG.info("Using user T2=%.6g -> lag angle %.3g deg, |.|=%.4g at s*", T2, ang, mag)
    else:
        T2 = choose_T2(sstar, beta, thetamax_deg=thetamax, mag_lo=magwin[0], mag_hi=magwin[1], T2max=T2max)
        ang, mag = lag_angle_mag(sstar, beta, T2)
        LOG.info("Auto T2=%.6g so lag angle %.3g deg, |.|=%.4g at s*", T2, ang, mag)

    Gc = Gc_from_chain(Kc, leads, T2, beta)
    L = ct.minreal(Gc * G, verbose=False)
    return DesignResult(case="coupled", sstar=sstar, Kc=Kc, leads=leads, T2=T2, beta=beta,
                        Gc=ct.minreal(Gc, verbose=False), L=L,
                        before=error_constants(G), after=error_constants(L))
