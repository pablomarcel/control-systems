# root_locus_analysis/compensatorTool/lag.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Literal
import math
import numpy as np
import control as ct

from .utils import LOG, tf_arrays, polyval, error_constants

@dataclass(slots=True)
class LagDesignResult:
    sstar: complex
    Kc: float
    z: float
    p: float
    beta: float
    angle_deg: float
    Gc: ct.TransferFunction
    L: ct.TransferFunction
    before: dict
    after: dict

Case = Literal["kp", "kv", "ka"]

def _angle(z: complex) -> float:
    return math.atan2(z.imag, z.real)

def _wrap_pi(th: float) -> float:
    return (th + math.pi) % (2*math.pi) - math.pi

def lag_angle_contribution(sstar: complex, z: float, p: float) -> float:
    """Absolute angle (radians) of (s+z)/(s+p) at s=s*."""
    return abs(_wrap_pi(_angle(sstar + z) - _angle(sstar + p)))

def choose_lag_zp_by_angle(sstar: complex, beta: float,
                           thetamax_deg: float = 5.0,
                           T_grid: np.ndarray | None = None) -> Tuple[float, float, float]:
    """
    Search T (z=1/T, p=1/(βT)) so that |angle| ≤ thetamax (prefer larger T).
    Returns (z, p, angle_deg).
    """
    if T_grid is None:
        T_grid = np.logspace(-1, 4, 400)  # 0.1 ... 1e4
    th_max = math.radians(thetamax_deg)
    best: Tuple[float, float, float] | None = None
    for T in T_grid[::-1]:  # prefer larger T
        z = 1.0 / T
        p = 1.0 / (beta * T)
        th = lag_angle_contribution(sstar, z, p)
        if th <= th_max:
            best = (z, p, math.degrees(th))
            break
    if best is None:
        # fall back to largest T and report angle
        T = T_grid[-1]
        z = 1.0 / T
        p = 1.0 / (beta * T)
        best = (z, p, math.degrees(lag_angle_contribution(sstar, z, p)))
    return best

class LagCompensatorService:
    """
    Service layer: compute a lag compensator (single stage) that improves
    Kp/Kv/Ka by a requested target/factor or a chosen beta, and sizes Kc from |L(s*)|=1.
    """

    def design(self,
               G: "ct.TransferFunction",
               sstar: complex,
               err: Case = "kv",
               beta: float | None = None,
               target: float | None = None,
               factor: float | None = None,
               z_user: float | None = None,
               p_user: float | None = None,
               T_user: float | None = None,
               thetamax: float = 5.0) -> LagDesignResult:

        LOG.debug("LagCompensatorService.design: start")

        # BEFORE constants
        consts0 = error_constants(G)
        keymap = {"kp": "Kp", "kv": "Kv", "ka": "Ka"}
        key = keymap[err.lower()]
        base_const = consts0[key]

        # Size beta
        if beta is None:
            if factor is not None:
                if factor <= 1.0:
                    raise ValueError("--factor must be > 1.")
                beta = float(factor)
            elif target is not None:
                if not np.isfinite(base_const) or base_const <= 0:
                    raise ValueError(f"Cannot size β from target: current {key} is {base_const}.")
                beta = max(1.01, float(target) / float(base_const))
            else:
                beta = 10.0
        if beta <= 1.0:
            raise ValueError("Require β>1 for a lag network.")
        LOG.info("β (z/p) = %.6g", beta)

        # Pick z,p
        if (z_user is not None) ^ (p_user is not None):
            raise ValueError("If specifying --z or --p you must specify both.")
        if z_user is not None and p_user is not None:
            z = float(z_user); p = float(p_user)
            if not (z > p > 0):
                raise ValueError("Require z>p>0 (zero at -z, pole at -p).")
            angle_deg = math.degrees(lag_angle_contribution(sstar, z, p))
            LOG.info("Using user z/p: z=%.6g, p=%.6g (angle %.3g°)", z, p, angle_deg)
        else:
            if T_user is not None:
                T = float(T_user)
                z = 1.0 / T
                p = 1.0 / (beta * T)
                angle_deg = math.degrees(lag_angle_contribution(sstar, z, p))
                LOG.info("Using user T=%.6g → z=%.6g, p=%.6g (angle %.3g°)", T, z, p, angle_deg)
            else:
                z, p, angle_deg = choose_lag_zp_by_angle(sstar, beta, thetamax)
                LOG.info("Auto-placed z/p: z=%.6g, p=%.6g with |angle|=%.3g° (≤ %.3g°)",
                         z, p, angle_deg, thetamax)

        # Magnitude condition: |Kc * (s*+z)/(s*+p) * G(s*)| = 1
        nG, dG = tf_arrays(G)
        Lmag = abs(polyval(nG, sstar) / polyval(dG, sstar))
        Kc = 1.0 / (Lmag * abs((sstar + z) / (sstar + p)))
        LOG.info("Kc from |L(s*)|=1: %.6g", Kc)

        # Build systems
        Gc = ct.tf([Kc, Kc * z], [1.0, p])               # Kc*(s+z)/(s+p)
        L = ct.minreal(Gc * G, verbose=False)

        return LagDesignResult(
            sstar=sstar, Kc=Kc, z=z, p=p, beta=beta, angle_deg=angle_deg,
            Gc=ct.minreal(Gc, verbose=False), L=L,
            before=consts0, after=error_constants(L)
        )

class LagCompensatorApp:
    """High-level orchestrator for lag design: print summary (no plots for now)."""

    def __init__(self) -> None:
        self.svc = LagCompensatorService()

    def run(self, **kwargs) -> LagDesignResult:
        """
        Expected kwargs:
            pole (PoleSpec) OR (sreal,wimag) pair already resolved by caller,
            num, den (strings for coefficients), and lag-specific options.
        """
        from .apis import PoleSpec  # lazy import to keep CLI --help fast

        pole: PoleSpec = kwargs.pop("pole")
        G = ct.tf(kwargs.pop("num"), kwargs.pop("den"))
        err = kwargs.pop("err", "kv")
        beta = kwargs.pop("beta", None)
        target = kwargs.pop("target", None)
        factor = kwargs.pop("factor", None)
        z_user = kwargs.pop("z_user", None)
        p_user = kwargs.pop("p_user", None)
        T_user = kwargs.pop("T_user", None)
        thetamax = kwargs.pop("thetamax", 5.0)

        res = self.svc.design(
            G=G, sstar=pole.sstar, err=err, beta=beta, target=target, factor=factor,
            z_user=z_user, p_user=p_user, T_user=T_user, thetamax=thetamax
        )

        # ---- report (ASCII-safe) ----
        print("\n== Lag Compensator Design ==")
        print(f"Desired pole:            {pole.desc}")
        print(f"β (z/p):                 {res.beta:.6g}")
        print(f"Zero z  (at s=-z):       {res.z:.6g}")
        print(f"Pole p  (at s=-p):       {res.p:.6g}")
        print(f"Angle at s*:             {res.angle_deg:.3g} deg")
        print(f"Kc from |L(s*)|=1:       {res.Kc:.6g}")

        from .utils import pretty_tf
        print("\nGc(s) (lag) = Kc*(s+z)/(s+p):")
        print(" ", pretty_tf(res.Gc))
        print("\nCompensated open-loop L_new(s) = Gc(s)G(s):")
        print(" ", pretty_tf(res.L))

        b, a = res.before, res.after

        def fmt(v):
            import numpy as np
            if v is np.inf:
                return "inf"
            try:
                return f"{float(v):.6g}"
            except Exception:
                return str(v)

        print("\n=== Open-loop low-frequency constants (unity-feedback conventions) ===")
        print(f" BEFORE (plant):  Kp={fmt(b['Kp'])}  Kv={fmt(b['Kv'])}  Ka={fmt(b['Ka'])}  (type={b['type']})")
        print(f" AFTER  (with Gc): Kp={fmt(a['Kp'])}  Kv={fmt(a['Kv'])}  Ka={fmt(a['Ka'])}  (type={a['type']})")

        return res
