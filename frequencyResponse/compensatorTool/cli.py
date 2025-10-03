# cli.py
from __future__ import annotations

import argparse
import logging
import sys

from .apis import (
    PlantSpec,
    DesignOptions,
    PlotOptions,
    FrequencyGrid,
    LagLeadDesignSpec,
)

# Lead-only API types are optional (present when lead.py + apis additions are installed)
try:
    from .apis import LeadDesignSpec, LeadDesignOptions  # type: ignore
    _HAVE_LEAD_API = True
except Exception:  # pragma: no cover (keeps lag-lead tests passing if lead API not yet present)
    LeadDesignSpec = None  # type: ignore
    LeadDesignOptions = None  # type: ignore
    _HAVE_LEAD_API = False

from .app import CompensatorApp
from .utils import parse_list_floats


def build_parser() -> argparse.ArgumentParser:
    # ASCII-only description for test compatibility (tests grep this exact phrase)
    p = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=(
            "Lag-Lead compensator - design & analysis (Ogata section 7-13)\n"
            "modernControl.frequencyResponse.compensatorTool"
        ),
    )

    # --------------------------- Top-level mode -------------------------------
    # Default stays 'laglead' so existing commands & tests remain unchanged.
    p.add_argument(
        "--mode",
        choices=["laglead", "lead"],
        default="laglead",
        help="Choose design mode (default: laglead)",
    )

    # --------------------------- Plant input ---------------------------------
    g = p.add_argument_group("Plant input")
    g.add_argument("--tf", type=str, help='Rational TF in s, e.g. "1/(s*(s+1)*(s+2))"')
    g.add_argument("--num", type=str, help="TF numerator")
    g.add_argument("--den", type=str, help="TF denominator")
    g.add_argument("--z", type=str, help="ZPK zeros")
    g.add_argument("--p", type=str, help="ZPK poles")
    g.add_argument("--k", type=str, help="ZPK gain")
    g.add_argument("--A", type=str, help='State matrix A, rows with ";", entries with ","')
    g.add_argument("--B", type=str, help='Input matrix B, rows with ";", entries with ","')
    g.add_argument("--C", type=str, help='Output matrix C, rows with ";", entries with ","')
    g.add_argument("--D", type=str, help='Feedthrough D, rows with ";", entries with ","')
    g.add_argument("--params", type=str, default="", help="Param dict like K=4,T=0.2")

    # --------------------------- Design (laglead) -----------------------------
    d = p.add_argument_group("Design (laglead)")
    d.add_argument("--Kv", type=float, help="Set gain to meet velocity constant (type-1 only)")
    d.add_argument("--pm_target", type=float, help="Target phase margin (deg)")
    d.add_argument("--pm_allow", type=float, default=5.0, help="Extra phase cushion (deg)")
    d.add_argument("--wc_hint", type=float, help="Optional crossover hint")
    d.add_argument("--r_lead", type=float, default=10.0, help="wp/wz ratio for lead (default 10)")
    d.add_argument("--r_lag", type=float, default=10.0, help="Lag spacing factor (wz ~ wc/r_lag)")

    d.add_argument("--alpha", type=float, help="Lead alpha (0<alpha<1) if manual")
    d.add_argument("--beta", type=float, help="Lag beta (>1) if manual")
    d.add_argument("--wz_lead", type=float, help="Lead zero (rad/s)")
    d.add_argument("--wp_lead", type=float, help="Lead pole (rad/s)")
    d.add_argument("--wz_lag", type=float, help="Lag zero (rad/s)")
    d.add_argument("--wp_lag", type=float, help="Lag pole (rad/s)")
    d.add_argument("--Kc", type=float, default=1.0, help="Series Kc (default 1)")

    d.add_argument("--ogata_7_28", action="store_true", help="Ogata Example 7-28 preset.")

    # --------------------------- Design (lead-only) ---------------------------
    # These are ignored unless --mode lead is set.
    dlead = p.add_argument_group("Design (lead-only)")
    dlead.add_argument("--lead_pm_target", type=float, help="Target phase margin (deg) for lead-only")
    dlead.add_argument("--lead_pm_add", type=float, default=5.0, help="Extra φ (deg) to offset crossover shift (default 5)")
    dlead.add_argument("--lead_stages", type=int, default=1, help="Number of cascaded lead sections (>=1)")
    dlead.add_argument("--lead_phi_split", type=str, help="Asymmetric per-stage φ percentages, e.g., '60,40'")
    dlead.add_argument("--lead_alpha", type=float, help="Manual lead α (single-stage manual mode)")
    dlead.add_argument("--lead_T", type=float, help="Manual lead T (requires --lead_alpha)")
    dlead.add_argument("--lead_Kc", type=float, help="Manual Kc (optional)")

    # --------------------------- Frequency grid ------------------------------
    f = p.add_argument_group("Frequency grid")
    f.add_argument("--wmin", type=float, default=1e-3)
    f.add_argument("--wmax", type=float, default=1e3)
    f.add_argument("--wnum", type=int, default=2000)

    # --------------------------- Visualization & export ----------------------
    v = p.add_argument_group("Visualization & export")
    v.add_argument("--backend", choices=["mpl", "plotly"], default="mpl")
    v.add_argument("--plots", type=str, default="bode,nyquist,nichols,step,ramp")
    v.add_argument("--nichols_templates", action="store_true")
    v.add_argument("--ogata_axes", action="store_true")

    # Flexible list arguments: accept 0+ tokens, each token can itself contain commas.
    v.add_argument("--nyquist_M", nargs="*", metavar="M")
    v.add_argument("--nyquist_marks", nargs="*", metavar="w")

    v.add_argument("--save", type=str)
    v.add_argument("--save_img", type=str)
    v.add_argument("--export_json", type=str)
    v.add_argument("--export_csv_prefix", type=str)
    v.add_argument("--no_show", action="store_true")
    v.add_argument("--verbose", action="store_true")
    v.add_argument("--show_unstable", action="store_true")  # force-show unstable baseline in time plots

    # Nichols template contours (also flexible lists)
    v.add_argument("--nichols_Mdb", nargs="*", metavar="M_dB")
    v.add_argument("--nichols_Ndeg", nargs="*", metavar="N_deg")

    return p


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    args = build_parser().parse_args(argv)

    logging.basicConfig(
        level=(logging.DEBUG if args.verbose else logging.INFO),
        format="INFO: %(message)s" if not args.verbose else "%(levelname)s: %(message)s",
    )

    # --------------------------- Build common API specs -----------------------
    plant = PlantSpec(
        tf_expr=args.tf,
        num=args.num,
        den=args.den,
        z=args.z,
        p=args.p,
        k=args.k,
        A=args.A,
        B=args.B,
        C=args.C,
        D=args.D,
        params=args.params or "",
    )

    # Parse flexible list inputs (space- or comma-separated, with/without quotes)
    def _flex(seq: list[str] | None):
        if not seq:
            return None
        return parse_list_floats(" ".join(seq))

    plot = PlotOptions(
        backend=args.backend,
        plots=args.plots,
        ogata_axes=args.ogata_axes,
        nichols_templates=args.nichols_templates,
        nichols_Mdb=_flex(args.nichols_Mdb),
        nichols_Ndeg=_flex(args.nichols_Ndeg),
        nyquist_M=_flex(args.nyquist_M),
        nyquist_marks=_flex(args.nyquist_marks),
        save=args.save,
        save_img=args.save_img,
        export_json=args.export_json,
        export_csv_prefix=args.export_csv_prefix,
        no_show=args.no_show,
        verbose=args.verbose,
        show_unstable=args.show_unstable,
    )

    grid = FrequencyGrid(wmin=args.wmin, wmax=args.wmax, wnum=args.wnum)

    # --------------------------- Execute (mode switch) ------------------------
    if args.mode == "lead":
        if not _HAVE_LEAD_API:
            # Keep behavior explicit if apis additions haven't landed yet.
            raise RuntimeError(
                "Lead mode requested but Lead API types are not available. "
                "Make sure apis.py defines LeadDesignOptions and LeadDesignSpec, "
                "and lead.py is present."
            )
        # Build lead-only spec
        lead_design = LeadDesignOptions(  # type: ignore
            Kv=args.Kv,
            pm_target=args.lead_pm_target,
            pm_add=args.lead_pm_add,
            stages=args.lead_stages,
            phi_split=(args.lead_phi_split or None),
            alpha=args.lead_alpha,
            T=args.lead_T,
            Kc=args.lead_Kc,
        )
        spec = LeadDesignSpec(plant=plant, design=lead_design, plot=plot, grid=grid)  # type: ignore

        # Call the lead-only engine directly to avoid touching CompensatorApp/tests
        from .lead import LeadDesigner  # lazy import to keep deps light for laglead tests
        result = LeadDesigner().run(spec)  # type: ignore

    else:
        # Default lag–lead path (unchanged)
        design = DesignOptions(
            Kv=args.Kv,
            pm_target=args.pm_target,
            pm_allow=args.pm_allow,
            wc_hint=args.wc_hint,
            r_lead=args.r_lead,
            r_lag=args.r_lag,
            alpha=args.alpha,
            beta=args.beta,
            wz_lead=args.wz_lead,
            wp_lead=args.wp_lead,
            wz_lag=args.wz_lag,
            wp_lag=args.wp_lag,
            Kc=args.Kc,
            ogata_7_28=args.ogata_7_28,
        )
        spec = LagLeadDesignSpec(plant=plant, design=design, plot=plot, grid=grid)
        app = CompensatorApp()
        result = app.run(spec)

    # --------------------------- Print summary -------------------------------
    import json as _json

    print(
        "\n==== DESIGN SUMMARY ====\n"
        + _json.dumps(result.pack, indent=2, default=lambda o: [o.real, o.imag])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
