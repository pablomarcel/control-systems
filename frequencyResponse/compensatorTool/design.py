
from __future__ import annotations
import math, logging
from dataclasses import dataclass
from typing import Optional, Tuple, List
import numpy as np
import control as ct

from .utils import parse_params, tf_from_expr, parse_list_floats, db
from .core import frequency_response_arrays, get_margins, set_gain_for_Kv
from .apis import PlantSpec, DesignOptions, PlotOptions, FrequencyGrid, LagLeadDesignSpec, LagLeadDesignResult
from . import io as io_mod

@dataclass(slots=True)
class LagLeadDesignNumbers:
    alpha: float
    beta: float
    T_lead: float
    T_lag: float
    wz_lead: float
    wp_lead: float
    wz_lag: float
    wp_lag: float
    Kc: float
    wc: float

class LagLeadDesigner:
    @staticmethod
    def preset_ogata_7_28(G_base: ct.lti) -> Tuple[LagLeadDesignNumbers, ct.lti]:
        G1 = 20 * ct.tf(G_base)
        wz_lead, wp_lead = 0.7, 7.0
        alpha = wz_lead / wp_lead
        T_lead = 1.0 / wz_lead
        wz_lag, wp_lag = 0.15, 0.015
        beta = wz_lag / wp_lag
        T_lag = 1.0 / wz_lag
        return LagLeadDesignNumbers(alpha, beta, T_lead, T_lag, wz_lead, wp_lead, wz_lag, wp_lag, 1.0, float('nan')), G1

    @staticmethod
    def _lead_from_phase_add(phi_add_deg: float, wc: float, r: float=10.0):
        sphi = math.sin(math.radians(max(0.1, min(85.0, phi_add_deg))))
        alpha = (1 - sphi)/(1 + sphi)
        r = max(r, 1.5)
        wz = wc / math.sqrt(r)
        wp = wc * math.sqrt(r)
        alpha = max(1e-3, min(0.99, wz/wp))
        T = 1.0 / wz
        return alpha, T, wz, wp

    @staticmethod
    def auto_design(G1: ct.lti, Kv_target: float, pm_target: float,
                    pm_allow_extra: float=5.0, wc_hint: Optional[float]=None,
                    r_lead: float=10.0, r_lag: float=10.0) -> LagLeadDesignNumbers:
        w = np.logspace(-3, 3, 3000)
        mag, ph, ww = frequency_response_arrays(G1, w)
        ph_deg=np.rad2deg(ph)
        target_phase = -180.0 + pm_target + pm_allow_extra
        idx = int(np.argmin(np.abs(ph_deg - target_phase)))
        wc = float(ww[idx])
        _, pm, _, _ = get_margins(G1)
        needed = max(0.0, pm_target - pm + pm_allow_extra)
        alpha, T_lead, wz_lead, wp_lead = LagLeadDesigner._lead_from_phase_add(needed, wc, r=r_lead)
        Glead = ct.tf([T_lead, 1.0], [alpha*T_lead, 1.0])
        magL,_,_=frequency_response_arrays(Glead*G1, np.array([wc]))
        beta = float(max(1.001, magL[0]))
        wz_lag = wc / max(1.001, r_lag)
        T_lag = 1.0 / wz_lag
        wp_lag = wz_lag / beta
        return LagLeadDesignNumbers(alpha, beta, T_lead, T_lag, wz_lead, wp_lead, wz_lag, wp_lag, 1.0, wc)

    def run(self, spec: LagLeadDesignSpec) -> LagLeadDesignResult:
        params = parse_params(spec.plant.params)

        if spec.design.ogata_7_28:
            G_base = tf_from_expr('1/(s*(s+1)*(s+2))', {})
            nums, G1 = self.preset_ogata_7_28(G_base)
            nyq_M_default = [1.2]
            nyq_marks_default = [0.2, 0.4, 1.0, 2.0]
        else:
            G1 = self._build_plant(spec.plant, params)
            if spec.design.Kv is not None:
                G1, Kscale, Kv_old = set_gain_for_Kv(G1, spec.design.Kv)
                logging.info('Kv scaling: Kv_old=%.6g -> Kv_target=%.6g ; Kscale=%.6g', Kv_old, spec.design.Kv, Kscale)
            nyq_M_default = []
            nyq_marks_default = []
            d = spec.design
            if all(v is not None for v in [d.wz_lead, d.wp_lead, d.wz_lag, d.wp_lag]):
                alpha = d.alpha if d.alpha is not None else float(d.wz_lead/d.wp_lead)
                beta  = d.beta  if d.beta  is not None else float(d.wz_lag/d.wp_lag)
                nums = LagLeadDesignNumbers(alpha=float(alpha), beta=float(beta),
                                            T_lead=1.0/float(d.wz_lead), T_lag=1.0/float(d.wz_lag),
                                            wz_lead=float(d.wz_lead), wp_lead=float(d.wp_lead),
                                            wz_lag=float(d.wz_lag), wp_lag=float(d.wp_lag),
                                            Kc=float(d.Kc), wc=float('nan'))
            else:
                nums = self.auto_design(G1, d.Kv if d.Kv is not None else 0.0,
                                        pm_target=float(d.pm_target if d.pm_target is not None else 50.0),
                                        pm_allow_extra=float(d.pm_allow),
                                        wc_hint=d.wc_hint, r_lead=float(d.r_lead), r_lag=float(d.r_lag))

        Glead = ct.tf([nums.T_lead,1],[nums.alpha*nums.T_lead,1])
        Glag  = ct.tf([nums.T_lag,1],[nums.beta*nums.T_lag,1])
        Gc = ct.minreal(Glead*Glag*nums.Kc, verbose=False)
        G_ol_c = ct.minreal(Gc * G1, verbose=False)

        Gcl_comp = ct.feedback(G_ol_c, 1)
        Gcl_base = ct.feedback(G1, 1)

        grid = spec.grid
        w = np.logspace(np.log10(grid.wmin), np.log10(grid.wmax), grid.wnum)

        gm_u, pm_u, wgm_u, wpm_u = get_margins(G1)
        gm_c, pm_c, wgm_c, wpm_c = get_margins(G_ol_c)

        z_cl = np.sort_complex(ct.zeros(Gcl_comp))
        p_cl = np.sort_complex(ct.poles(Gcl_comp))

        pack = {
            'uncomp_margins':{'PM_deg':pm_u, 'w_PM':wpm_u, 'GM_abs':gm_u, 'GM_dB':(db(gm_u) if np.isfinite(gm_u) else float('inf')), 'w_GM':wgm_u},
            'comp_margins':  {'PM_deg':pm_c, 'w_PM':wpm_c, 'GM_abs':gm_c, 'GM_dB':(db(gm_c) if np.isfinite(gm_c) else float('inf')), 'w_GM':wgm_c},
            'lag_lead':{
                'alpha':nums.alpha,'gamma':1/nums.alpha if nums.alpha>0 else float('inf'),
                'T2':nums.T_lead,
                'wz_lead':nums.wz_lead,'wp_lead':nums.wp_lead,
                'beta':nums.beta,'T1':nums.T_lag,
                'wz_lag':nums.wz_lag,'wp_lag':nums.wp_lag,
                'Kc':nums.Kc,'wc':nums.wc
            },
            'cl_zeros':[complex(z) for z in z_cl],
            'cl_poles':[complex(p) for p in p_cl],
            'notes':{'baseline_used':'gain_adjusted' if (spec.design.ogata_7_28 or spec.design.Kv is not None) else 'original'}
        }

        files: List[str] = []
        plot = spec.plot
        if plot.export_json:
            files.append(io_mod.write_json(plot.export_json, pack))
        if plot.export_csv_prefix:
            files.extend(io_mod.export_csvs(plot.export_csv_prefix, G1, G_ol_c, w))

        files += io_mod.render_plots(
            backend=plot.backend,
            wants=[s.strip().lower() for s in plot.plots.split(',') if s.strip()],
            G1=G1, G_ol_c=G_ol_c, w=w,
            ogata_axes=bool(plot.ogata_axes),
            nichols_templates=bool(plot.nichols_templates),
            nichols_Mdb=parse_list_floats(plot.nichols_Mdb) or ([-12, -9, -6, -3, 0, 0.9, 3, 6, 9, 12] if plot.nichols_templates else None),
            nichols_Ndeg=parse_list_floats(plot.nichols_Ndeg) or ([-30, -60, -90, -120, -150, -180] if plot.nichols_templates else None),
            nyquist_M=parse_list_floats(plot.nyquist_M) or nyq_M_default,
            nyquist_marks=parse_list_floats(plot.nyquist_marks) or nyq_marks_default,
            save_tmpl=plot.save,
            save_img_tmpl=plot.save_img,
            no_show=plot.no_show
        )
        return LagLeadDesignResult(pack=pack, files=files)

    def _build_plant(self, plant: PlantSpec, params: dict) -> ct.lti:
        import numpy as np, control as ct
        if plant.A and plant.B and plant.C:
            A = np.array([[float(self._eval(x,params)) for x in r.strip().split(',')] for r in plant.A.split(';')])
            B = np.array([[float(self._eval(x,params)) for x in r.strip().split(',')] for r in plant.B.split(';')])
            C = np.array([[float(self._eval(x,params)) for x in r.strip().split(',')] for r in plant.C.split(';')])
            D = np.array([[0.0]]) if not plant.D else np.array([[float(self._eval(x,params)) for x in r.strip().split(',')] for r in plant.D.split(';')])
            return ct.ss(A,B,C,D)
        if (plant.z is not None) or (plant.p is not None) or (plant.k is not None):
            def _vec(s):
                if s is None: return []
                ss = s.strip()
                if ss=='': return []
                parts=[p.strip() for p in (ss.split(',') if ',' in ss else ss.split())]
                from .utils import _eval as _e
                return [float(_e(p, params)) for p in parts]
            z=_vec(plant.z); p=_vec(plant.p)
            from .utils import _eval as _e
            k=1.0 if plant.k is None else float(_e(plant.k, params))
            return ct.zpk(z,p,k)
        if plant.tf_expr:
            return tf_from_expr(plant.tf_expr, params)
        if plant.num is not None and plant.den is not None:
            def _arr(vec):
                parts=[p.strip() for p in (vec.split(',') if ',' in vec else vec.split())]
                from .utils import _eval as _e
                return [float(_e(p, params)) for p in parts]
            return ct.tf(_arr(plant.num), _arr(plant.den))
        raise ValueError('Plant not specified.')

    @staticmethod
    def _eval(x, params):
        from .utils import _eval as _e
        return _e(x, params)
