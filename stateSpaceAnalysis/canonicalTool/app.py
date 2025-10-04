
from __future__ import annotations
from dataclasses import dataclass
import os

import matplotlib
if not os.environ.get("DISPLAY"):
    matplotlib.use("Agg")
import matplotlib.pyplot as plt

import control as ct
from .core import CanonicalFormsEngine as Eng
from .design import CompareOptions
from .utils import time_grid, substitute_kind, ensure_dir
from .tools.trace_uml import track

@dataclass(slots=True)
class CompareResult:
    tf_equal: dict
    symbolic: str | None

class CanonicalToolApp:
    @track("CanonicalToolApp.compare", "CanonicalFormsEngine")
    def compare(self, num, den, opts: CompareOptions) -> CompareResult:
        num_n, den_n = Eng.normalize_tf_coeffs(num, den)
        sys_ccf = Eng.make_ccf_from_tf(num_n, den_n)
        sys_ocf = Eng.make_ocf_from_ss(sys_ccf)
        sys_modal = Eng.make_modal_real(sys_ccf)

        tf_equal = {
            "OCF_vs_CCF": Eng.tf_equal(sys_ocf, sys_ccf),
            "Modal_vs_CCF": Eng.tf_equal(sys_modal, sys_ccf),
        }

        sym = Eng.symbolic_G(sys_ccf) if opts.symbolic else None
        sym_str = str(sym) if sym is not None else None

        self._plot_steps(
            systems=[sys_ccf, sys_ocf, sys_modal],
            labels=["CCF", "OCF", "Modal (real)"],
            tfinal=opts.tfinal,
            dt=opts.dt,
            backend=opts.backend,
            show=opts.show,
            save=substitute_kind(opts.save, "step") if opts.save else None
        )

        return CompareResult(tf_equal=tf_equal, symbolic=sym_str)

    @staticmethod
    def _plot_steps(systems, labels, tfinal: float, dt: float, backend: str, show: bool, save: str | None):
        T = time_grid(tfinal, dt)

        if backend == "plotly":
            try:
                import plotly.graph_objects as go
                fig = go.Figure()
                for sys, lab in zip(systems, labels):
                    t, y = ct.step_response(sys, T=T)
                    fig.add_trace(go.Scatter(x=t, y=y.squeeze(), name=lab, mode="lines"))
                fig.update_layout(title="Step responses (canonical forms)",
                                  xaxis_title="Time (s)", yaxis_title="y(t)")
                if save:
                    if save.lower().endswith(".html"):
                        import plotly.io as pio
                        pio.write_html(fig, save, include_plotlyjs="cdn", auto_open=False)
                    else:
                        import plotly.io as pio
                        pio.write_image(fig, save)
                if show:
                    fig.show()
                return
            except Exception:
                backend = "mpl"

        import matplotlib.pyplot as plt
        import control as ct
        styles = ['-', '--', ':', '-.']
        widths = [2.4, 2.0, 2.0, 2.0]
        T = time_grid(tfinal, dt)
        plt.figure(figsize=(8, 4.5))
        for i, (sys, lab) in enumerate(zip(systems, labels)):
            t, y = ct.step_response(sys, T=T)
            plt.plot(t, y.squeeze(), styles[i % len(styles)], linewidth=widths[i % len(widths)], label=lab)
        plt.title("Step responses (canonical forms)")
        plt.xlabel("Time (s)"); plt.ylabel("y(t)")
        plt.grid(True); plt.legend(); plt.tight_layout()
        if save:
            ensure_dir(save)
            plt.savefig(save, dpi=160)
        if show:
            plt.show()
        plt.close()
