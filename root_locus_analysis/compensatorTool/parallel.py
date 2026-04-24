# modernControl/root_locus_analysis/compensatorTool/parallel.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple
import math
import warnings

import numpy as np
import control as ct

from .utils import LOG, tf_arrays, pretty_tf


# ───────────────────────── data types ─────────────────────────

@dataclass(slots=True)
class ParallelSolution:
    sstar: complex
    wn: float
    K: float
    k_scaled: float


# ───────────────────────── utils ──────────────────────────────

def _parse_list(name: str, s: Optional[str]) -> np.ndarray:
    if s is None:
        raise ValueError(f"Missing required polynomial/list for {name}.")
    toks = [t for t in s.replace(";", ",").split(",") if t.strip()]
    try:
        return np.array([float(t) for t in toks], dtype=float)
    except Exception as e:
        raise ValueError(f"Could not parse {name}='{s}': {e}")


def _poly_roots(coeffs: np.ndarray) -> np.ndarray:
    c = np.array(coeffs, float)
    i = 0
    while i < len(c) - 1 and abs(c[i]) < 1e-14:
        i += 1
    c = c[i:]
    if len(c) <= 1:
        return np.array([], dtype=complex)
    try:
        return np.roots(c)
    except Exception:
        return np.array([], dtype=complex)


def _eval_tf(G: "ct.TransferFunction", s: complex) -> complex:
    n, d = tf_arrays(G)
    return np.polyval(n, s) / np.polyval(d, s)


def _s_from_zeta_wn(zeta: float, wn: float) -> complex:
    sigma = -zeta * wn
    wd = wn * math.sqrt(max(0.0, 1.0 - zeta * zeta))
    return complex(sigma, wd)


# ───────────────────── building F(s) (three ways) ─────────────────────

def build_F_from_blocks(
    *,
    g1_num: Optional[str], g1_den: Optional[str],
    g2_num: Optional[str], g2_den: Optional[str],
    h_num: Optional[str],  h_den: Optional[str],
    gcb_num: Optional[str], gcb_den: Optional[str],
) -> Optional[ct.TransferFunction]:
    if not all([g1_num, g1_den, g2_num, g2_den, gcb_num, gcb_den]):
        return None
    G1 = ct.tf(_parse_list("g1-num", g1_num), _parse_list("g1-den", g1_den))
    G2 = ct.tf(_parse_list("g2-num", g2_num), _parse_list("g2-den", g2_den))
    H  = ct.tf(_parse_list("h-num",  h_num),  _parse_list("h-den",  h_den)) if (h_num and h_den) else ct.tf([1],[1])
    Gc_base = ct.tf(_parse_list("gcb-num", gcb_num), _parse_list("gcb-den", gcb_den))
    Gf = ct.minreal(G2 / (1 + G1*G2*H), verbose=False)
    F  = ct.minreal(Gc_base * Gf, verbose=False)

    print("G1(s):", pretty_tf(G1))
    print("G2(s):", pretty_tf(G2))
    print("H(s): ", pretty_tf(H))
    print("Gc_base(s):", pretty_tf(Gc_base))
    print("Gf(s) = G2/(1+G1G2H):", pretty_tf(Gf))
    return F


def build_F_from_char_split(
    *,
    A_num: Optional[str], B_num: Optional[str]
) -> Optional[Tuple[ct.TransferFunction, ct.TransferFunction, ct.TransferFunction]]:
    if not (A_num and B_num):
        return None
    A = ct.tf(_parse_list("A-num", A_num), [1.0])
    B = ct.tf(_parse_list("B-num", B_num), [1.0])
    F = ct.minreal(B / A, verbose=False)
    return F, A, B


def build_F_direct(*, F_num: Optional[str], F_den: Optional[str]) -> Optional[ct.TransferFunction]:
    if not (F_num and F_den):
        return None
    return ct.tf(_parse_list("F-num", F_num), _parse_list("F-den", F_den))


# ───────────────────── ζ-scan along the ray ─────────────────────

def constant_zeta_scan(
    F: ct.TransferFunction, zeta: float,
    wn_lo: Optional[float], wn_hi: Optional[float], ngrid: int
) -> List[Tuple[complex, float]]:
    if not (0 < zeta < 1):
        raise ValueError("zeta must be in (0,1).")

    # rough wn scale from singularities
    n, d = tf_arrays(F)
    p = list(_poly_roots(d)); z = list(_poly_roots(n))
    mags = [abs(x) for x in (p + z) if np.isfinite(x) and abs(x) > 0]
    base = max(mags + [1.0])
    if wn_lo is None:
        wn_lo = 0.05 * base
    if wn_hi is None:
        wn_hi = 10.0 * base

    wns = np.linspace(float(wn_lo), float(wn_hi), int(max(400, ngrid)))
    sline = -zeta * wns + 1j * wns * math.sqrt(1 - zeta*zeta)

    vals = np.array([_eval_tf(F, s) for s in sline])
    ang  = np.unwrap(np.angle(vals))
    g = ang - math.pi  # want Arg(F)=π

    sols: List[Tuple[complex, float]] = []
    for i in range(len(wns) - 1):
        if g[i] == 0 or g[i] * g[i+1] < 0:
            a, b = wns[i], wns[i+1]
            fa, fb = g[i], g[i+1]
            for _ in range(64):  # bisection
                m = 0.5 * (a + b)
                sm = -zeta*m + 1j*m*math.sqrt(1 - zeta*zeta)
                fm = math.atan2(_eval_tf(F, sm).imag, _eval_tf(F, sm).real) - math.pi
                fm = (fm + math.pi) % (2*math.pi) - math.pi
                if fa * fm <= 0:
                    b, fb = m, fm
                else:
                    a, fa = m, fm
                if abs(b - a) < 1e-9:
                    break
            sstar = -zeta*m + 1j*m*math.sqrt(1 - zeta*zeta)
            sols.append((sstar, m))

    # de-dup near-equal wn
    out: List[Tuple[complex, float]] = []
    for s, w in sols:
        if not any(abs(w - w2) < 1e-4 for _, w2 in out):
            out.append((s, w))
    return out


# ───────────────────── plotting helpers ─────────────────────

def _trimmed_limits(xs: np.ndarray, trim=0.01) -> Tuple[float, float]:
    xs = xs[np.isfinite(xs)]
    if xs.size == 0:
        return -1.0, 1.0
    lo = np.quantile(xs, trim)
    hi = np.quantile(xs, 1.0 - trim)
    if not np.isfinite(lo) or not np.isfinite(hi) or lo == hi:
        lo, hi = float(xs.min()), float(xs.max())
    span = hi - lo
    return float(lo - 0.05 * span), float(hi + 0.05 * span)


def _nice_round_bounds(xlo, xhi, ylo, yhi, pad_units=1.0, make_square=True):
    xlo = math.floor(xlo - 1e-9) - pad_units
    xhi = math.ceil(xhi + 1e-9) + pad_units
    ylo = math.floor(ylo - 1e-9) - pad_units
    yhi = math.ceil(yhi + 1e-9) + pad_units
    if make_square:
        xspan = xhi - xlo
        yspan = yhi - ylo
        S = max(xspan, yspan)
        cx = 0.5 * (xhi + xlo)
        cy = 0.5 * (yhi + ylo)
        xlo, xhi = cx - 0.5 * S, cx + 0.5 * S
        ylo, yhi = cy - 0.5 * S, cy + 0.5 * S
    return float(xlo), float(xhi), float(ylo), float(yhi)


def _apply_ogata_grid(ax, xlo, xhi, ylo, yhi, unit_ticks=True, show_grid=True):
    try:
        ax.set_aspect('equal', adjustable='box')
    except Exception:
        pass

    if unit_ticks:
        def _ints(lo, hi, max_count=31):
            a, b = math.floor(lo), math.ceil(hi)
            if b - a <= max_count:
                return np.arange(a, b + 1, 1)
            step = int(math.ceil((b - a)/max_count))
            return np.arange(a, b + 1, step)
        ax.set_xticks(_ints(xlo, xhi))
        ax.set_yticks(_ints(ylo, yhi))
    ax.grid(show_grid, ls=":")


def _real_axis_segments(F: "ct.TransferFunction", xlo: float, xhi: float) -> List[Tuple[float,float]]:
    """Intervals on the real axis where the locus exists (rule-of-odd)."""
    n, d = tf_arrays(F)
    re_sing = []
    for r in _poly_roots(n):
        if abs(r.imag) < 1e-10:
            re_sing.append(r.real)
    for r in _poly_roots(d):
        if abs(r.imag) < 1e-10:
            re_sing.append(r.real)
    re_sing = sorted([x for x in re_sing if np.isfinite(x)])
    edges = [xlo] + re_sing + [xhi]
    segs: List[Tuple[float, float]] = []
    for i in range(len(edges) - 1):
        mid = 0.5 * (edges[i] + edges[i+1])
        cnt = sum(1 for s in re_sing if s > mid)  # to the RIGHT
        if cnt % 2 == 1:
            segs.append((edges[i], edges[i+1]))
    return segs


def _recommended_time_from_solutions(solutions: List[ParallelSolution]) -> np.ndarray:
    if not solutions:
        return np.linspace(0, 10.0, 2001)
    sigmas = [abs(sol.sstar.real) for sol in solutions if sol.sstar.real < 0]
    sigma = min(sigmas) if sigmas else 1.0
    t_end = max(2.0, min(10.0, 6.0 / sigma))
    N = max(1000, int(200 * t_end))
    return np.linspace(0.0, t_end, N)


# ───────────────────── plotting frontends ─────────────────────

def plot_root_locus(
    F: "ct.TransferFunction",
    solutions: List[ParallelSolution],
    *,
    kmin: Optional[float], kmax: Optional[float], kpts: int,
    clip: float, title: str, plotly_html: Optional[str],
    zeta_for_ray: Optional[float] = None,
    ogata_grid: bool = True,
    show_real_axis_segments: bool = True,
    xlim_override: Optional[Tuple[float, float]] = None,
    ylim_override: Optional[Tuple[float, float]] = None,
    pad_units: float = 1.0,
    legend_mode: str = "outside",
    mpl_grid: bool = True,
    plotly_grid: bool = True,
    plotly_cross_axes: bool = False,
) -> None:
    # compute root locus samples
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            kvect = None
            if kmin is not None and kmax is not None and kmax > kmin > 0:
                kvect = np.logspace(math.log10(kmin), math.log10(kmax), max(40, kpts))
            rl, _ = ct.root_locus(F, plot=False, gains=kvect)
        except TypeError:
            rl, _ = ct.root_locus(F, Plot=False, kvect=kvect if kvect is not None else np.logspace(-4, 4, max(40, kpts)))

    # autoscale → integer-rounded, square box
    pts = np.hstack([np.asarray(b) for b in rl]) if isinstance(rl, (list, tuple)) else rl.reshape(-1)
    X = np.real(pts[np.isfinite(pts)])
    Y = np.imag(pts[np.isfinite(pts)])
    xlo, xhi = _trimmed_limits(X, clip)
    ylo, yhi = _trimmed_limits(Y, clip)
    if xlim_override is not None:
        xlo, xhi = xlim_override
    if ylim_override is not None:
        ylo, yhi = ylim_override
    xlo, xhi, ylo, yhi = _nice_round_bounds(xlo, xhi, ylo, yhi, pad_units=pad_units, make_square=True)

    # matplotlib
    try:
        import matplotlib.pyplot as plt
        figsize = (8.6, 6.2) if legend_mode == "outside" else (7.2, 6.2)
        fig, ax = plt.subplots(1, 1, figsize=figsize)

        if isinstance(rl, (list, tuple)):
            for br in rl:
                br = np.asarray(br)
                ax.plot(br.real, br.imag, lw=1)
        else:
            for k in range(rl.shape[1]):
                ax.plot(rl[:, k].real, rl[:, k].imag, lw=1)

        # zeros/poles and s*
        try:
            n, d = tf_arrays(F)
            z = _poly_roots(n)
            p = _poly_roots(d)
            if z.size:
                ax.plot(np.real(z), np.imag(z), 'o', mfc='w', label='zeros')
            if p.size:
                ax.plot(np.real(p), np.imag(p), 'x', label='poles')
        except Exception:
            pass

        have_s_label = False
        for sol in solutions:
            ax.plot([sol.sstar.real], [sol.sstar.imag], 'ko', mfc='w', label='s*' if not have_s_label else None)
            have_s_label = True

        # ζ-ray
        if zeta_for_ray and 0 < zeta_for_ray < 1:
            theta = math.acos(zeta_for_ray)
            xs = np.linspace(xlo, max(xhi, 0.2), 300)
            ys = np.tan(theta) * (-xs)
            ax.plot(xs, ys, '--', lw=0.9, color='brown', label=f'ζ={zeta_for_ray:g} ray')

        # real-axis eligible segments
        if show_real_axis_segments:
            for a, b in _real_axis_segments(F, xlo, xhi):
                ax.plot([a, b], [0, 0], lw=3, alpha=0.15, color='k')

        ax.axhline(0, color='k', lw=0.6)
        ax.axvline(0, color='k', lw=0.6)
        ax.set_title(title)
        ax.set_xlim(xlo, xhi)
        ax.set_ylim(ylo, yhi)
        if ogata_grid:
            _apply_ogata_grid(ax, xlo, xhi, ylo, yhi, unit_ticks=True, show_grid=mpl_grid)

        if legend_mode == "outside":
            ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0)
        elif legend_mode != "none":
            ax.legend(loc=legend_mode)

        fig.tight_layout()
        plt.show()
    except Exception as e:
        LOG.warning("matplotlib locus failed: %s", e)

    # Plotly export
    if plotly_html:
        try:
            import plotly.graph_objects as go
            fig = go.Figure()

            if isinstance(rl, (list, tuple)):
                for br in rl:
                    br = np.asarray(br)
                    fig.add_trace(go.Scatter(x=br.real, y=br.imag, mode="lines", name="branch"))
            else:
                for k in range(rl.shape[1]):
                    fig.add_trace(go.Scatter(x=rl[:, k].real, y=rl[:, k].imag, mode="lines", name=f"branch {k+1}"))

            n, d = tf_arrays(F)
            z = _poly_roots(n)
            p = _poly_roots(d)
            if z.size:
                fig.add_trace(go.Scatter(x=np.real(z), y=np.imag(z), mode="markers",
                                         marker=dict(symbol="circle-open", size=10), name="zeros"))
            if p.size:
                fig.add_trace(go.Scatter(x=np.real(p), y=np.imag(p), mode="markers",
                                         marker=dict(symbol="x", size=10), name="poles"))

            for i, sol in enumerate(solutions, 1):
                fig.add_trace(go.Scatter(x=[sol.sstar.real], y=[sol.sstar.imag], mode="markers",
                                         marker=dict(symbol="circle-open", size=10), name=f"s* {i}"))

            # ζ-ray
            if zeta_for_ray and 0 < zeta_for_ray < 1:
                theta = math.acos(zeta_for_ray)
                xs = np.linspace(xlo, max(xhi, 0.2), 300)
                ys = np.tan(theta) * (-xs)
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(dash="dash"),
                                         name=f"ζ={zeta_for_ray:g} ray"))

            fig.update_layout(
                title=title, template="plotly_white",
                xaxis=dict(title="Real axis", range=[xlo, xhi], dtick=1, tickangle=0,
                           showgrid=plotly_grid, zeroline=False),
                yaxis=dict(title="Imag axis", range=[ylo, yhi], dtick=1, tickangle=0,
                           showgrid=plotly_grid, zeroline=False, scaleanchor="x", scaleratio=1),
                legend=dict(x=1.02, y=1, xanchor="left"),
                margin=dict(l=60, r=80, t=50, b=60),
            )

            if plotly_cross_axes:
                fig.add_shape(type="line", x0=xlo, x1=xhi, y0=0, y1=0, line=dict(color="black", width=1))
                fig.add_shape(type="line", x0=0, x1=0, y0=ylo, y1=yhi, line=dict(color="black", width=1))

            fig.write_html(plotly_html, include_plotlyjs="cdn", full_html=True)
            LOG.info("Wrote Plotly locus to %s", plotly_html)
        except Exception as e:
            LOG.warning("Plotly export failed: %s", e)


def _step_from_blocks(
    *, g1_num: Optional[str], g1_den: Optional[str],
    g2_num: Optional[str], g2_den: Optional[str],
    h_num: Optional[str],  h_den: Optional[str],
    gcb_num: Optional[str], gcb_den: Optional[str],
    K: float
) -> Optional[ct.TransferFunction]:
    if not all([g1_num, g1_den, g2_num, g2_den, gcb_num, gcb_den]):
        return None
    try:
        G1 = ct.tf(_parse_list("g1-num", g1_num), _parse_list("g1-den", g1_den))
        G2 = ct.tf(_parse_list("g2-num", g2_num), _parse_list("g2-den", g2_den))
        H  = ct.tf(_parse_list("h-num",  h_num),  _parse_list("h-den",  h_den)) if (h_num and h_den) else ct.tf([1],[1])
        Gc_base = ct.tf(_parse_list("gcb-num", gcb_num), _parse_list("gcb-den", gcb_den))
        Gc = ct.minreal(K * Gc_base, verbose=False)
        # Series-equivalent for the closed loop described in your script:
        T = ct.minreal((G1*G2) / (1 + G1*G2*H + G2*Gc), verbose=False)
        return T
    except Exception:
        return None


def _step_from_char(A_num: Optional[str], B_num: Optional[str], step_num: Optional[str], K: float) -> Optional[ct.TransferFunction]:
    if not (A_num and B_num and step_num):
        return None
    A = ct.tf(_parse_list("A-num", A_num), [1.0])
    B = ct.tf(_parse_list("B-num", B_num), [1.0])
    den = ct.minreal(A + K*B, verbose=False)
    num = ct.tf(_parse_list("step-num", step_num), [1.0])
    return ct.minreal(num / den, verbose=False)


def compute_step_traces(
    *, solutions: List[ParallelSolution],
    g1_num: Optional[str], g1_den: Optional[str],
    g2_num: Optional[str], g2_den: Optional[str],
    h_num: Optional[str],  h_den: Optional[str],
    gcb_num: Optional[str], gcb_den: Optional[str],
    A_num: Optional[str], B_num: Optional[str], step_num: Optional[str],
) -> Tuple[Optional[np.ndarray], List[Tuple[str, np.ndarray]]]:
    """Return (t, traces) where traces = [(label, y(t)), ...]."""
    if not solutions:
        return None, []
    t = _recommended_time_from_solutions(solutions)
    traces: List[Tuple[str, np.ndarray]] = []
    for sol in solutions:
        Tsys = _step_from_blocks(
            g1_num=g1_num, g1_den=g1_den,
            g2_num=g2_num, g2_den=g2_den,
            h_num=h_num,   h_den=h_den,
            gcb_num=gcb_num, gcb_den=gcb_den,
            K=sol.K
        )
        if Tsys is None:
            Tsys = _step_from_char(A_num, B_num, step_num, sol.K)
        if Tsys is None:
            LOG.info("Step plot requested, but neither blocks nor (A,B,step-num) were provided.")
            return None, []
        _, y = ct.step_response(Tsys, T=t)
        traces.append((f"K={sol.K:.5g} (k={sol.k_scaled:.5g})", y))
    return t, traces


# ───────────────────── user-facing app ─────────────────────

class ParallelCompensatorApp:
    """
    Small orchestrator around the series-equivalent parallel compensation locus:
        1 + K F(s) = 0
    Builds F(s) three ways (blocks, A+K·B split, or direct),
    computes K for s* or finds intersections along a ζ-ray,
    prints a clean report, and optionally plots locus/step.
    """

    def _parse_limits_arg(self, values: Optional[List[str]], name: str) -> Optional[Tuple[float, float]]:
        """Accept either: --xlim LO HI  or  --xlim 'LO,HI' (forward-compatible with cli)."""
        if values is None:
            return None
        parts: List[str]
        if len(values) == 1:
            s = values[0]
            if "," in s:
                parts = [t for t in s.split(",") if t.strip()]
            else:
                raise ValueError(f"--{name} needs two numbers: use '--{name} LO HI' or '--{name} \"LO,HI\"'")
        else:
            parts = values[:2]
        if len(parts) != 2:
            raise ValueError(f"--{name} requires exactly two numbers")
        lo, hi = float(parts[0]), float(parts[1])
        if lo > hi:
            lo, hi = hi, lo
        if lo == hi:
            hi = lo + 1.0
        return lo, hi

    def run(
        self,
        *,
        # (i) blocks
        g1_num: Optional[str], g1_den: Optional[str],
        g2_num: Optional[str], g2_den: Optional[str],
        h_num: Optional[str],  h_den: Optional[str],
        gcb_num: Optional[str], gcb_den: Optional[str],
        # (ii) A+K·B split (and step numerator for output TF)
        A_num: Optional[str], B_num: Optional[str], step_num: Optional[str],
        # (iii) direct F
        F_num: Optional[str], F_den: Optional[str],
        # specs
        zeta: Optional[float], wn: Optional[float],
        sreal: Optional[float], wimag: Optional[float],
        # plotting/report knobs
        plot: Tuple[str, ...] | None = None,
        k_range: Optional[str] = None,
        k_pts: int = 600,
        locus_clip: float = 0.01,
        plotly_locus: Optional[str] = None,
        plotly_step: Optional[str] = None,
        wn_range: Optional[str] = None,
        grid: int = 2400,
        no_ogata_grid: bool = False,
        no_real_axis_hint: bool = False,
        legend: str = "outside",
        xlim: Optional[List[str]] = None,
        ylim: Optional[List[str]] = None,
        pad: float = 1.0,
        mpl_grid: str = "on",
        plotly_grid: str = "on",
        plotly_cross_axes: bool = False,
        scale: float = 1.0,
        verbose: int = 0,
    ) -> List[ParallelSolution]:

        # Build F(s) by precedence: blocks → (A,B) → direct
        F = None; A = B = None
        Fb = build_F_from_blocks(g1_num=g1_num, g1_den=g1_den, g2_num=g2_num, g2_den=g2_den,
                                 h_num=h_num, h_den=h_den, gcb_num=gcb_num, gcb_den=gcb_den)
        if Fb is not None:
            print("F(s) from blocks =", pretty_tf(Fb)); F = Fb

        cs = build_F_from_char_split(A_num=A_num, B_num=B_num)
        if cs is not None:
            Fcs, A, B = cs; print("F(s) from A+K·B split =", pretty_tf(Fcs)); F = Fcs

        Fd = build_F_direct(F_num=F_num, F_den=F_den)
        if Fd is not None:
            print("F(s) direct        =", pretty_tf(Fd)); F = Fd

        if F is None:
            raise ValueError("Provide F(s): via blocks (G1,G2,H,+Gc_base), OR --A-num/--B-num, OR --F-num/--F-den.")

        # Solve K for provided s* or run ζ-scan
        solutions: List[ParallelSolution] = []
        if zeta is not None and wn is not None:
            if not (0 < zeta < 1 and wn > 0):
                raise ValueError("--zeta ∈ (0,1), --wn > 0 required.")
            sstar = _s_from_zeta_wn(zeta, wn)
            K = 1.0 / abs(_eval_tf(F, sstar))
            solutions.append(ParallelSolution(sstar=sstar, wn=wn, K=K, k_scaled=K/scale))
        elif sreal is not None and wimag is not None:
            if wimag < 0:
                raise ValueError("--wimag must be ≥ 0.")
            sstar = complex(sreal, wimag)
            wn_eff = abs(sstar)
            K = 1.0 / abs(_eval_tf(F, sstar))
            solutions.append(ParallelSolution(sstar=sstar, wn=wn_eff, K=K, k_scaled=K/scale))
        else:
            if zeta is None:
                raise ValueError("Provide either (--zeta, --wn) or (--sreal, --wimag), or ζ-only for a ζ-scan.")
            if not (0 < zeta < 1):
                raise ValueError("--zeta must be in (0,1).")
            wn_lo = wn_hi = None
            if wn_range:
                parts = [t for t in wn_range.split(",") if t.strip()]
                if len(parts) == 2:
                    wn_lo, wn_hi = float(parts[0]), float(parts[1])
            for sstar, wn_i in constant_zeta_scan(F, zeta, wn_lo, wn_hi, grid):
                K = 1.0 / abs(_eval_tf(F, sstar))
                solutions.append(ParallelSolution(sstar=sstar, wn=wn_i, K=K, k_scaled=K/scale))
            if not solutions:
                LOG.warning("No intersections found on the ζ-ray. Adjust --wn-range or --grid.")

        # Report
        print("\nSeries-equivalent loop: 1 + K·F(s) = 0")
        print("F(s) =", pretty_tf(F))
        n, d = tf_arrays(F)
        z = _poly_roots(n); p = _poly_roots(d)
        if z.size or p.size:
            ztxt = [f"{c.real:.4g}+{c.imag:.4g}j" for c in z] or ["—"]
            ptxt = [f"{c.real:.4g}+{c.imag:.4g}j" for c in p] or ["—"]
            print("Open-loop zeros:", ztxt, "\nOpen-loop poles :", ptxt)
        print("scale =", scale)
        print("\nSolutions (on ζ-line if applicable):")
        print("  (σ, jωd)                   ωn            K                 k = K/scale")
        for sol in solutions:
            s = sol.sstar
            print(f"  ({s.real:+.6g}, {s.imag:+.6g}j)   {sol.wn:.6g}     {sol.K:.6g}          {sol.k_scaled:.6g}")

        # parse axis overrides (optional)
        xlim_pair = self._parse_limits_arg(xlim, "xlim") if xlim else None
        ylim_pair = self._parse_limits_arg(ylim, "ylim") if ylim else None

        # Plots
        if plot:
            if "locus" in plot:
                kmin = kmax = None
                if k_range:
                    parts = [t for t in k_range.split(",") if t.strip()]
                    if len(parts) == 2:
                        kmin, kmax = float(parts[0]), float(parts[1])
                plot_root_locus(
                    F, solutions,
                    kmin=kmin, kmax=kmax, kpts=int(max(40, k_pts)),
                    clip=max(0.0, min(0.2, locus_clip)),
                    title="Root Locus of 1 + K·F(s)",
                    plotly_html=plotly_locus,
                    zeta_for_ray=zeta if (zeta is not None and wn is None) else None,
                    ogata_grid=not no_ogata_grid,
                    show_real_axis_segments=not no_real_axis_hint,
                    xlim_override=xlim_pair, ylim_override=ylim_pair,
                    pad_units=float(pad),
                    legend_mode=legend,
                    mpl_grid=(mpl_grid == "on"),
                    plotly_grid=(plotly_grid == "on"),
                    plotly_cross_axes=plotly_cross_axes,
                )

            if "step" in plot:
                t, traces = compute_step_traces(
                    solutions=solutions,
                    g1_num=g1_num, g1_den=g1_den,
                    g2_num=g2_num, g2_den=g2_den,
                    h_num=h_num,   h_den=h_den,
                    gcb_num=gcb_num, gcb_den=gcb_den,
                    A_num=A_num, B_num=B_num, step_num=step_num,
                )
                if t is not None and traces:
                    # Matplotlib step
                    try:
                        import matplotlib.pyplot as plt
                        fig, ax = plt.subplots(1, 1, figsize=(7.6, 4.4))
                        for label, y in traces:
                            ax.plot(t, y, label=label)
                        ax.grid(True, ls=":"); ax.set_xlabel("t [s]"); ax.set_ylabel("y(t)")
                        ax.set_title("Unit-step (all solutions)")
                        ax.legend()
                        fig.tight_layout()
                        plt.show()
                    except Exception as e:
                        LOG.warning("Step plot (matplotlib) failed: %s", e)

                    # Plotly step (optional)
                    if plotly_step:
                        try:
                            import plotly.graph_objects as go
                            fig = go.Figure()
                            for label, y in traces:
                                fig.add_trace(go.Scatter(x=t, y=y, mode="lines", name=label))
                            fig.update_layout(
                                title="Unit-step (all solutions)", template="plotly_white",
                                xaxis=dict(title="t [s]", showgrid=(plotly_grid == "on")),
                                yaxis=dict(title="y(t)",  showgrid=(plotly_grid == "on")),
                                legend=dict(x=1.02, y=1, xanchor="left"),
                                margin=dict(l=60, r=80, t=50, b=60),
                            )
                            fig.write_html(plotly_step, include_plotlyjs="cdn", full_html=True)
                            LOG.info("Wrote Plotly step responses to %s", plotly_step)
                        except Exception as e:
                            LOG.warning("Plotly step export failed: %s", e)

        return solutions
