
from __future__ import annotations
import argparse, logging, sys
from .apis import PlantSpec, DesignOptions, PlotOptions, FrequencyGrid, LagLeadDesignSpec
from .app import CompensatorApp

def build_parser():
    p=argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
        description='Lag-Lead compensator - design & analysis (Ogata section 7-13) - modernControl.frequencyResponse.compensatorTool')

    g=p.add_argument_group('Plant input')
    g.add_argument('--tf', type=str, help='Rational TF in s, e.g. \"1/(s*(s+1)*(s+2))\"')
    g.add_argument('--num', type=str, help='TF numerator')
    g.add_argument('--den', type=str, help='TF denominator')
    g.add_argument('--z', type=str, help='ZPK zeros'); g.add_argument('--p', type=str, help='ZPK poles'); g.add_argument('--k', type=str, help='ZPK gain')
    g.add_argument('--A', type=str); g.add_argument('--B', type=str); g.add_argument('--C', type=str); g.add_argument('--D', type=str)
    g.add_argument('--params', type=str, default='', help='Param dict K=4,T=0.2')

    d=p.add_argument_group('Design')
    d.add_argument('--Kv', type=float, help='Set gain to meet velocity constant (type-1 only)')
    d.add_argument('--pm_target', type=float, help='Target phase margin (deg)')
    d.add_argument('--pm_allow', type=float, default=5.0, help='Extra phase cushion (deg)')
    d.add_argument('--wc_hint', type=float, help='Optional crossover hint')
    d.add_argument('--r_lead', type=float, default=10.0, help='wp/wz ratio for lead (default 10)')
    d.add_argument('--r_lag', type=float, default=10.0, help='Lag spacing factor (wz ~ wc/r_lag)')

    d.add_argument('--alpha', type=float, help='Lead alpha (0<alpha<1) if manual')
    d.add_argument('--beta', type=float, help='Lag beta (>1) if manual')
    d.add_argument('--wz_lead', type=float, help='Lead zero (rad/s)')
    d.add_argument('--wp_lead', type=float, help='Lead pole (rad/s)')
    d.add_argument('--wz_lag', type=float, help='Lag zero (rad/s)')
    d.add_argument('--wp_lag', type=float, help='Lag pole (rad/s)')
    d.add_argument('--Kc', type=float, default=1.0, help='Series Kc (default 1)')

    d.add_argument('--ogata_7_28', action='store_true', help='Ogata Example 7-28 preset.')

    f=p.add_argument_group('Frequency grid')
    f.add_argument('--wmin', type=float, default=1e-3)
    f.add_argument('--wmax', type=float, default=1e3)
    f.add_argument('--wnum', type=int, default=2000)

    v=p.add_argument_group('Visualization & export')
    v.add_argument('--backend', choices=['mpl','plotly'], default='mpl')
    v.add_argument('--plots', type=str, default='bode,nyquist,nichols,step,ramp')
    v.add_argument('--nichols_templates', action='store_true')
    v.add_argument('--ogata_axes', action='store_true')
    v.add_argument('--nyquist_M', nargs='+', type=float, metavar='M')
    v.add_argument('--nyquist_marks', nargs='+', type=float, metavar='w')
    v.add_argument('--save', type=str)
    v.add_argument('--save_img', type=str)
    v.add_argument('--export_json', type=str)
    v.add_argument('--export_csv_prefix', type=str)
    v.add_argument('--no_show', action='store_true')
    v.add_argument('--verbose', action='store_true')

    v.add_argument('--nichols_Mdb', nargs='+', type=float, metavar='M_dB')
    v.add_argument('--nichols_Ndeg', nargs='+', type=float, metavar='N_deg')
    return p

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=(logging.DEBUG if args.verbose else logging.INFO),
                        format='INFO: %(message)s' if not args.verbose else '%(levelname)s: %(message)s')

    plant = PlantSpec(
        tf_expr=args.tf, num=args.num, den=args.den, z=args.z, p=args.p, k=args.k,
        A=args.A, B=args.B, C=args.C, D=args.D, params=args.params or ''
    )
    design = DesignOptions(
        Kv=args.Kv, pm_target=args.pm_target, pm_allow=args.pm_allow, wc_hint=args.wc_hint,
        r_lead=args.r_lead, r_lag=args.r_lag, alpha=args.alpha, beta=args.beta,
        wz_lead=args.wz_lead, wp_lead=args.wp_lead, wz_lag=args.wz_lag, wp_lag=args.wp_lag,
        Kc=args.Kc, ogata_7_28=args.ogata_7_28
    )
    plot =  PlotOptions(
        backend=args.backend, plots=args.plots, ogata_axes=args.ogata_axes,
        nichols_templates=args.nichols_templates,
        nichols_Mdb=args.nichols_Mdb, nichols_Ndeg=args.nichols_Ndeg,
        nyquist_M=args.nyquist_M, nyquist_marks=args.nyquist_marks,
        save=args.save, save_img=args.save_img,
        export_json=args.export_json, export_csv_prefix=args.export_csv_prefix,
        no_show=args.no_show, verbose=args.verbose
    )
    grid = FrequencyGrid(wmin=args.wmin, wmax=args.wmax, wnum=args.wnum)

    spec = LagLeadDesignSpec(plant=plant, design=design, plot=plot, grid=grid)
    app = CompensatorApp()
    result = app.run(spec)
    import json as _json
    print('\\n==== DESIGN SUMMARY ====\\n'+_json.dumps(result.pack, indent=2, default=lambda o: [o.real, o.imag]))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
