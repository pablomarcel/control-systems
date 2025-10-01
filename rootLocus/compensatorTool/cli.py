# modernControl/rootLocus/compensatorTool/cli.py
from __future__ import annotations

from typing import Optional, Tuple, Literal
import click


@click.group()
def cli():
    # Keep the en dash to satisfy tests; avoid other exotic glyphs.
    """Lag–Lead designer (Ogata Sec. 6-8), multi-lead edition - rootLocus.compensatorTool."""


# --- multi-lead lag–lead "design" subcommand ---------------------------------
@cli.command(
    "design",
    help=(
        "Run a compensator design and print a summary (with optional plots).\n\n"
        "Lag–Lead designer (Ogata Sec. 6-8), multi-lead edition - rootLocus.compensatorTool."
    ),
)
@click.option("--num", required=True, help="Plant numerator coeffs (descending)")
@click.option("--den", required=True, help="Plant denominator coeffs (descending)")
@click.option("--zeta", type=float, default=None, help="Desired damping ratio (0<zeta<1)")
@click.option("--wn", type=float, default=None, help="Desired natural frequency (>0)")
@click.option("--sreal", type=float, default=None, help="Desired pole real part sigma")
@click.option("--wimag", type=float, default=None, help="Desired pole imag part wd (>=0)")
@click.option("--case", type=click.Choice(["indep", "coupled"]), default="indep")
@click.option("--lead-method", type=click.Choice(["bisector", "cancel", "manual"]), default="bisector")
@click.option("--cancel-at", type=float, default=None, help="First-stage zero location if cancel")
@click.option("--lead-z", type=float, default=None, help="Manual: zero at s=-z (z>0)")
@click.option("--lead-p", type=float, default=None, help="Manual: pole at s=-p (p>z)")
@click.option("--T1", "t1", type=float, default=None, help="Manual: T1 (with --gamma)")
@click.option("--gamma", type=float, default=None, help="Manual: gamma>1 (with --T1)")
@click.option("--nlead", type=int, default=1, help="Number of lead stages")
@click.option("--phi-per-lead", type=float, default=None, help="Approx per-lead phase (deg)")
@click.option("--phi-cap", type=float, default=60.0, help="Per-lead phase cap if not provided")
@click.option("--no-autonlead", is_flag=True, help="Disable auto nlead increase")
@click.option("--err", type=click.Choice(["kp", "kv", "ka"]), default="kv")
@click.option("--target", type=float, default=None, help="Target Kp/Kv/Ka")
@click.option("--factor", type=float, default=None, help="Improvement factor r(>1) (indep only)")
@click.option("--beta", type=float, default=None, help="Fix beta (>1)")
@click.option("--T2", "t2", type=float, default=None, help="Fix T2 for lag stage")
@click.option("--T2max", "t2max", type=float, default=1000.0)
@click.option("--thetamax", type=float, default=5.0)
@click.option("--magwin", default="0.98,1.02")
@click.option("--plot", multiple=True, type=click.Choice(["locus", "step"]))
@click.option("-v", "--verbose", count=True)
def design_cmd(
    num,
    den,
    zeta,
    wn,
    sreal,
    wimag,
    case,
    lead_method,
    cancel_at,
    lead_z,
    lead_p,
    t1,
    gamma,
    nlead,
    phi_per_lead,
    phi_cap,
    no_autonlead,
    err,
    target,
    factor,
    beta,
    t2,
    t2max,
    thetamax,
    magwin,
    plot,
    verbose,
):
    """Run a compensator design and print a summary (with optional plots)."""
    from .apis import PoleSpec
    from .utils import LOG
    import logging

    if verbose >= 2:
        LOG.setLevel(logging.DEBUG)
    elif verbose == 1:
        LOG.setLevel(logging.INFO)
    else:
        LOG.setLevel(logging.INFO)

    # Pole spec
    if zeta is not None:
        if wn is None or wn <= 0:
            raise click.BadParameter("When --zeta is provided, --wn (>0) is also required.")
        pole = PoleSpec.from_zeta_wn(zeta, wn)
    else:
        if sreal is None or wimag is None:
            raise click.BadParameter("Provide either (--zeta, --wn) or (--sreal, --wimag).")
        pole = PoleSpec.from_parts(sreal, wimag)

    # Manual lead tuple normalization
    manual: Optional[Tuple[float, float]] = None
    if lead_method == "manual":
        has_tg = (t1 is not None) and (gamma is not None)
        has_zp = (lead_z is not None) and (lead_p is not None)
        if has_tg and not has_zp:
            if t1 <= 0 or gamma <= 1:
                raise click.BadParameter("Manual (T1,gamma) requires T1>0 and gamma>1.")
            manual = (1.0 / t1, gamma / t1)
        elif has_zp and not has_tg:
            manual = (float(lead_z), float(lead_p))
        else:
            raise click.BadParameter("Manual lead: provide either (T1,gamma) OR (lead-z,lead-p), not both.")

    # Orchestrate via App
    from .app import CompensatorApp
    App = CompensatorApp()
    App.run(
        pole=pole,
        case=case,
        num=num,
        den=den,
        lead_method=lead_method,
        cancel_at=cancel_at,
        manual_lead=manual,
        nlead=nlead,
        phi_per_lead=phi_per_lead,
        phi_cap=phi_cap,
        auto_nlead=(not no_autonlead),
        err=err,
        target=target,
        factor=factor,
        beta=beta,
        T2=t2,
        thetamax=thetamax,
        magwin=tuple(float(x) for x in magwin.split(",")),
        T2max=t2max,
        plot=plot,
    )


# --- Lag-only subcommand -----------------------------------------------------
@cli.command(
    "lag",
    help=(
        "Lag-only compensator design (Ogata §6-7): size β from target/factor or set explicitly; "
        "auto-place z,p near origin with small angle at s*, then size Kc from |L(s*)|=1."
    ),
)
@click.option("--num", required=True, help="Plant numerator coeffs (descending)")
@click.option("--den", required=True, help="Plant denominator coeffs (descending)")
@click.option("--zeta", type=float, default=None, help="Desired damping ratio (0<zeta<1)")
@click.option("--wn", type=float, default=None, help="Desired natural frequency (>0)")
@click.option("--sreal", type=float, default=None, help="Desired pole real part sigma")
@click.option("--wimag", type=float, default=None, help="Desired pole imag part wd (>=0)")
@click.option("--err", type=click.Choice(["kp", "kv", "ka"]), default="kv")
@click.option("--target", type=float, default=None, help="Target Kp/Kv/Ka")
@click.option("--factor", type=float, default=None, help="Improvement factor r(>1)")
@click.option("--beta", type=float, default=None, help="Fix beta (>1)")
@click.option("--z", "z_user", type=float, default=None, help="Place zero at s=-z (z>0). Require --p too.")
@click.option("--p", "p_user", type=float, default=None, help="Place pole at s=-p (p>0, and p<z).")
@click.option("--T", "T_user", type=float, default=None, help="With --beta, use z=1/T, p=1/(βT).")
@click.option("--thetamax", type=float, default=5.0, help="Max angle at s* for auto z/p (deg)")
@click.option("-v", "--verbose", count=True)
def lag_cmd(
    num, den, zeta, wn, sreal, wimag,
    err, target, factor, beta, z_user, p_user, T_user, thetamax, verbose
):
    """Run a lag-only compensator design and print a summary."""
    from .apis import PoleSpec
    from .utils import LOG
    import logging
    import numpy as _np

    if verbose >= 2:
        LOG.setLevel(logging.DEBUG)
    elif verbose == 1:
        LOG.setLevel(logging.INFO)
    else:
        LOG.setLevel(logging.INFO)

    # Pole spec
    if zeta is not None:
        if wn is None or wn <= 0:
            raise click.BadParameter("When --zeta is provided, --wn (>0) is also required.")
        pole = PoleSpec.from_zeta_wn(zeta, wn)
    else:
        if sreal is None or wimag is None:
            raise click.BadParameter("Provide either (--zeta, --wn) or (--sreal, --wimag).")
        pole = PoleSpec.from_parts(sreal, wimag)

    from .lag import LagCompensatorApp

    def _parse_list(s: str) -> _np.ndarray:
        toks = [t for t in s.replace(";", ",").split(",") if t.strip()]
        return _np.array([float(t) for t in toks], dtype=float)

    App = LagCompensatorApp()
    App.run(
        pole=pole,
        num=_parse_list(num),
        den=_parse_list(den),
        err=err,
        target=target,
        factor=factor,
        beta=beta,
        z_user=z_user,
        p_user=p_user,
        T_user=T_user,
        thetamax=thetamax,
    )


# --- Lead-only subcommand ----------------------------------------------------
@cli.command(
    "lead",
    help=(
        "Lead-only compensator design (Ogata §6-6): Method 1 (bisector) or Method 2 (zero cancels a pole); "
        "sizes Kc so that |L(s*)|=1 at the desired pole."
    ),
)
@click.option("--num", required=True, help="Plant numerator coeffs (descending)")
@click.option("--den", required=True, help="Plant denominator coeffs (descending)")
@click.option("--zeta", type=float, default=None, help="Desired damping ratio (0<zeta<1)")
@click.option("--wn", type=float, default=None, help="Desired natural frequency (>0)")
@click.option("--sreal", type=float, default=None, help="Desired pole real part sigma")
@click.option("--wimag", type=float, default=None, help="Desired pole imag part wd (>=0)")
@click.option("--method", type=click.Choice(["1", "2", "bisector", "cancel"]), default="1")
@click.option("--cancel-at", type=float, default=None, help="(Method 2) real location for compensator zero")
@click.option("-v", "--verbose", count=True)
def lead_cmd(
    num, den, zeta, wn, sreal, wimag, method, cancel_at, verbose
):
    """Run a lead-only compensator design and print a summary."""
    from .apis import PoleSpec
    from .utils import LOG
    import logging
    import numpy as _np
    from .lead import LeadCompensatorApp

    if verbose >= 2:
        LOG.setLevel(logging.DEBUG)
    elif verbose == 1:
        LOG.setLevel(logging.INFO)
    else:
        LOG.setLevel(logging.INFO)

    # Pole spec
    if zeta is not None:
        if wn is None or wn <= 0:
            raise click.BadParameter("When --zeta is provided, --wn (>0) is also required.")
        pole = PoleSpec.from_zeta_wn(zeta, wn)
    else:
        if sreal is None or wimag is None:
            raise click.BadParameter("Provide either (--zeta, --wn) or (--sreal, --wimag).")
        pole = PoleSpec.from_parts(sreal, wimag)

    def _parse_list(s: str) -> _np.ndarray:
        toks = [t for t in s.replace(";", ",").split(",") if t.strip()]
        return _np.array([float(t) for t in toks], dtype=float)

    m: Literal["method1", "method2"]
    if method in ("1", "bisector"):
        m = "method1"
    else:
        m = "method2"

    App = LeadCompensatorApp()
    App.run(
        pole=pole,
        num=_parse_list(num),
        den=_parse_list(den),
        method=m,
        cancel_at=cancel_at,
    )


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
