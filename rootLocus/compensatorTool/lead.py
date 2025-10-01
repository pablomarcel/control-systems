# modernControl/rootLocus/compensatorTool/lead.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import math
import numpy as np
import control as ct

from .apis import PoleSpec
from .utils import LOG, pretty_tf


def _tf_arrays(G: "ct.TransferFunction") -> tuple[np.ndarray, np.ndarray]:
    """Return (num, den) as 1-D float arrays (descending), robust to older control versions."""
    try:
        num, den = ct.tfdata(G, squeeze=True)
    except TypeError:
        # control <= 0.9 compat
        num, den = ct.tfdata(G)

        def _first(a):
            while isinstance(a, (list, tuple)) and len(a) > 0:
                a = a[0]
            return a

        num, den = _first(num), _first(den)
    n = np.asarray(num, dtype=float).ravel()
    d = np.asarray(den, dtype=float).ravel()
    return n, d


def _arg(z: complex) -> float:
    return math.atan2(z.imag, z.real)


def _wrap_pi(theta: float) -> float:
    return (theta + math.pi) % (2 * math.pi) - math.pi


def _L_at(G: "ct.TransferFunction", s: complex) -> complex:
    n, d = _tf_arrays(G)
    return np.polyval(n, s) / np.polyval(d, s)


def _angle_L(G: "ct.TransferFunction", s: complex) -> float:
    return _arg(_L_at(G, s))


def _mag_L(G: "ct.TransferFunction", s: complex) -> float:
    return abs(_L_at(G, s))


def _pole_to_complex(pole) -> complex:
    """
    Normalize PoleSpec-like objects to a complex s*.

    Accepts (in order of preference):
      • pole.as_complex(), pole.to_complex(), pole.as_s(), pole.to_s(), pole.complex()
      • Attributes that may already store complex or (r,i): .s, .sstar, .s_star, .pole, .target, .value, .val, .point
      • Pairs of scalars: (.sigma,.wd), (.sreal,.wimag), (.real,.imag), (.re,.im)
      • Tuple/list: (real, imag)
      • Dict-like: ['sigma','wd'] or ['sreal','wimag'] or ['real','imag']
      • zeta/wn fallback: if attributes .zeta and .wn exist -> s* = -ζωn + j ωn√(1-ζ²)
      • Objects implementing __complex__ or a raw complex
    """
    # 1) Methods that (might) return complex
    for meth in ("as_complex", "to_complex", "as_s", "to_s", "complex"):
        if hasattr(pole, meth):
            fn = getattr(pole, meth)
            if callable(fn):
                try:
                    return complex(fn())
                except Exception:
                    pass

    # 2) Obvious attributes possibly holding complex or a (r,i) pair
    for name in ("s", "sstar", "s_star", "pole", "target", "value", "val", "point"):
        if hasattr(pole, name):
            v = getattr(pole, name)
            # Already complex?
            try:
                return complex(v)
            except Exception:
                # Maybe a tuple (r, i)
                try:
                    r, i = v
                    return complex(float(r), float(i))
                except Exception:
                    pass

    # 3) Named pair variants
    for rname, iname in (("sigma", "wd"), ("sreal", "wimag"),
                         ("real", "imag"), ("re", "im")):
        r = getattr(pole, rname, None)
        i = getattr(pole, iname, None)
        if r is not None and i is not None:
            try:
                return complex(float(r), float(i))
            except Exception:
                pass

    # 4) Tuple/list-like
    if isinstance(pole, (tuple, list)) and len(pole) >= 2:
        try:
            return complex(float(pole[0]), float(pole[1]))
        except Exception:
            pass

    # 5) Dict-like indexing
    if hasattr(pole, "__getitem__"):
        for keys in (("sigma", "wd"), ("sreal", "wimag"), ("real", "imag"), ("re", "im")):
            try:
                r = pole[keys[0]]  # type: ignore[index]
                i = pole[keys[1]]  # type: ignore[index]
                return complex(float(r), float(i))
            except Exception:
                pass

    # 6) zeta/wn fallback (works with PoleSpec.from_zeta_wn)
    zeta = getattr(pole, "zeta", None)
    wn = getattr(pole, "wn", None)
    if zeta is not None and wn is not None:
        try:
            zeta = float(zeta); wn = float(wn)
            if not (0 < zeta < 1) or not (wn > 0):
                raise ValueError
            sigma = -zeta * wn
            wd = wn * math.sqrt(max(0.0, 1.0 - zeta**2))
            return complex(sigma, wd)
        except Exception:
            pass

    # 7) __complex__ or already a complex-like
    try:
        return complex(pole)
    except Exception:
        pass

    raise AttributeError(
        "Cannot extract complex pole from PoleSpec; tried as_complex/to_complex/as_s/to_s, "
        ".s/.sstar/.s_star/.pole/.target/.value/.val/.point, (.sigma,.wd)/(.sreal,.wimag)/(.real,.imag)/(.re,.im), "
        "tuple/list, dict-like, zeta/wn fallback, and __complex__."
    )


def _bisector_lead(s_star: complex, phi: float) -> tuple[float, float]:
    """
    Ogata Method 1: return (z, p) on real axis (z>p; both typically negative) using the correct internal bisector.
    """
    x, y = s_star.real, s_star.imag
    if abs(y) < 1e-14:
        raise ValueError("s* must be off the real axis for the lead design.")
    u_left = np.array([-1.0, 0.0])  # left horizontal
    u_PO = np.array([-x, -y]); u_PO = u_PO / np.linalg.norm(u_PO)
    b = u_left / np.linalg.norm(u_left) + u_PO  # internal bisector
    beta = math.atan2(b[1], b[0])

    xs: list[float] = []
    for sgn in (+1, -1):
        theta = beta + sgn * (phi / 2.0)
        xs.append(x - y / math.tan(theta))
    xs.sort()
    p, z = xs[0], xs[1]  # farther left = pole; nearer origin = zero
    return float(z), float(p)


@dataclass(slots=True)
class LeadDesignResult:
    method: Literal["method1", "method2"]
    sstar: complex
    Kc: float
    z: float
    p: float
    Gc: ct.TransferFunction
    L1: ct.TransferFunction


class LeadCompensatorService:
    """
    Lightweight service implementing Ogata lead designs:
      - Method 1 (bisector construction)
      - Method 2 (zero cancels a given real pole)
    """

    def method1(self, G: ct.TransferFunction, pole: PoleSpec) -> LeadDesignResult:
        s_star = _pole_to_complex(pole)
        theta0 = _angle_L(G, s_star)
        phi = abs(_wrap_pi(math.pi - theta0))
        if phi < 1e-3:
            raise RuntimeError("Angle deficiency ~ 0; a single lead may not be required.")

        z, p = _bisector_lead(s_star, phi)
        Lmag = _mag_L(G, s_star)
        # magnitude condition on Kc:
        Kc = 1.0 / (Lmag * abs((s_star - z) / (s_star - p)))

        Gc = ct.minreal(ct.tf([Kc, -Kc * z], [1.0, -p]), verbose=False)
        L1 = ct.minreal(Gc * G, verbose=False)
        return LeadDesignResult(method="method1", sstar=s_star, Kc=float(Kc), z=float(z), p=float(p), Gc=Gc, L1=L1)

    def method2(self, G: ct.TransferFunction, pole: PoleSpec, cancel_at: float) -> LeadDesignResult:
        s_star = _pole_to_complex(pole)
        theta0 = _angle_L(G, s_star)
        thetaz = _arg(s_star - cancel_at)
        thetap = _wrap_pi(theta0 + thetaz - math.pi)
        if thetap <= 0:
            thetap += math.pi
        # p from atan2(Im{s*}, Re{s*} - p) = thetap  ->  p = Re{s*} - Im{s*}/tan(thetap)
        p = float(s_star.real - s_star.imag / math.tan(thetap))
        z = float(cancel_at)
        Lmag = _mag_L(G, s_star)
        Kc = 1.0 / (Lmag * abs((s_star - z) / (s_star - p)))

        Gc = ct.minreal(ct.tf([Kc, -Kc * z], [1.0, -p]), verbose=False)
        L1 = ct.minreal(Gc * G, verbose=False)
        return LeadDesignResult(method="method2", sstar=s_star, Kc=float(Kc), z=float(z), p=float(p), Gc=Gc, L1=L1)


class LeadCompensatorApp:
    """
    Small orchestrator that builds the plant from num/den, calls the service, and prints a human-friendly report.
    """

    def __init__(self) -> None:
        self.svc = LeadCompensatorService()

    @staticmethod
    def _parse_list(s: str | np.ndarray) -> np.ndarray:
        if isinstance(s, np.ndarray):
            return s.astype(float)
        toks = [t for t in str(s).replace(";", ",").split(",") if t.strip()]
        return np.array([float(t) for t in toks], dtype=float)

    def run(
        self,
        *,
        pole: PoleSpec,
        num: str | np.ndarray,
        den: str | np.ndarray,
        method: Literal["method1", "method2"] = "method1",
        cancel_at: float | None = None,
    ) -> LeadDesignResult:
        G = ct.tf(self._parse_list(num), self._parse_list(den))
        if method == "method1":
            res = self.svc.method1(G, pole)
            mlabel = "Method 1 (bisector construction)"
        else:
            if cancel_at is None:
                raise ValueError("Method 2 requires --cancel-at <real_location>.")
            res = self.svc.method2(G, pole, cancel_at=cancel_at)
            mlabel = f"Method 2 (zero at {cancel_at:g})"

        # -------- report (kept succinct; no plots here) --------
        print("\n== Lead Compensator Design ==")
        print(
            f"Method:                   {mlabel}\n"
            f"Target pole:              s* = {res.sstar.real:.6g} "
            f"{'+' if res.sstar.imag >= 0 else '-'} j{abs(res.sstar.imag):.6g}"
        )
        print(f"Zero at s = {res.z:.6g}")
        print(f"Pole at s = {res.p:.6g}")
        print(f"Kc from |L(s*)|=1:        {res.Kc:.6g}")

        print("\nGc(s) = Kc * (s - z)/(s - p):")
        print(" ", res.Gc)

        print("\nCompensated open-loop L_new(s) = Gc(s) G(s):")
        print(" ", pretty_tf(res.L1))
        return res
