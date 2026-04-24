# modernControl/root_locus_analysis/compensatorTool/app.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import warnings

import control as ct

from .utils import LOG, pretty_tf
from .apis import CompensatorService, PoleSpec


@dataclass(slots=True)
class AppOptions:
    """Options for high-level app presentation."""
    plot: Sequence[str] | None = None  # e.g. ("locus", "step")


class CompensatorApp:
    """High-level orchestrator: run design, print summary, optional plots."""
    def __init__(self) -> None:
        self.svc = CompensatorService()

    def _plot(self, L: ct.TransferFunction, sstar: complex, which: Sequence[str]) -> None:
        """Render optional plots without affecting the service API."""
        try:
            import matplotlib.pyplot as plt
            import numpy as _np
        except Exception:
            LOG.error("matplotlib not available; skipping plots.")
            return

        if "locus" in which:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    rl, _ = ct.root_locus(L, plot=False, gains=_np.logspace(-3, 3, 400))
                except TypeError:
                    rl, _ = ct.root_locus(L, Plot=False, kvect=_np.logspace(-3, 3, 400))

            fig, ax = plt.subplots(1, 1, figsize=(6, 5))
            if isinstance(rl, (list, tuple)):
                for br in rl:
                    br = _np.asarray(br)
                    ax.plot(br.real, br.imag, lw=1)
            else:
                for k in range(rl.shape[1]):
                    ax.plot(rl[:, k].real, rl[:, k].imag, lw=1)
            ax.plot([sstar.real], [sstar.imag], "ko", label="s*")
            ax.axhline(0, color="k", lw=0.6)
            ax.axvline(0, color="k", lw=0.6)
            ax.grid(True, ls=":")
            ax.legend()
            ax.set_title("Root Locus (compensated)")

        if "step" in which:
            T = ct.feedback(L, 1)
            t, y = ct.step_response(T)
            fig2, ax2 = plt.subplots(1, 1, figsize=(6, 3.5))
            ax2.plot(t, y)
            ax2.set_xlabel("t")
            ax2.set_ylabel("y(t)")
            ax2.grid(True, ls=":")
            ax2.set_title("Unit-step response (compensated)")

        try:
            import matplotlib.pyplot as plt  # reuse
            plt.show()
        except Exception:
            pass

    def run(self, **kwargs):
        """
        Execute a design run and print a summary.

        Notes:
        - UI-only kwargs (like 'plot') are consumed here and not forwarded to the service layer.
        - This function is side-effectful (prints/plots) but returns the design result.
        """
        pole: PoleSpec = kwargs.pop("pole")
        plot = kwargs.pop("plot", None)

        res = self.svc.design(pole=pole, **kwargs)

        # Title uses an en dash to match tests exactly
        print("\n== Lag–Lead Compensator Design ==")
        Gc, L = res.Gc, res.L
        print(f"Desired pole:          {pole.desc}")
        print(
            "Case:                  "
            + ("gamma!=beta (independent)" if res.case == "independent" else "generalized gamma=beta (coupled)")
        )
        print(f"Kc:                    {res.Kc:.6g}")

        if len(res.leads) == 1:
            Ld = res.leads[0]
            print(f"T1, gamma (lead):      T1={Ld.T1:.6g}, gamma={Ld.gamma:.6g}")
        else:
            print(f"Leads (N={len(res.leads)}):")
            for i, Ld in enumerate(res.leads, 1):
                print(f"  [{i}] T1={Ld.T1:.6g}, gamma={Ld.gamma:.6g}  (z={Ld.z:.6g}, p={Ld.p:.6g})")

        print(f"T2, beta (lag):        T2={res.T2:.6g}, beta={res.beta:.6g}")
        print("\nGc(s) =\n ", pretty_tf(Gc))
        print("\nCompensated open-loop L(s) = Gc(s)G(s) =\n ", pretty_tf(L))

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

        if plot:
            self._plot(L, res.sstar, plot)

        return res
