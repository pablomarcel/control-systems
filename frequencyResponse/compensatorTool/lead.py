from __future__ import annotations
import math, logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

import numpy as np
import control as ct

from .apis import PlantSpec, LeadDesignSpec, LeadDesignResult
# We reuse utilities if they exist in your codebase. To keep this OOP module
# drop-in friendly, each import is wrapped in a small compatibility shim.
try:
    from .utils import parse_params, db, _eval as _ueval
except Exception:
    import math as _m
    _EPS = np.finfo(float).tiny
    def db(x): 
        x = np.maximum(x, _EPS)
        return 20.0*np.log10(x)
    def parse_params(s: str) -> dict:
        if not s: return {}
        SAFE_FUNCS = {k: getattr(_m, k) for k in [
            'sin','cos','tan','asin','acos','atan','atan2','sinh','cosh','tanh','exp','log','log10','sqrt','pi','e'
        ]}
        SAFE_FUNCS.update({'j':1j,'J':1j})
        out = {}
        for tok in s.split(','):
            tok = tok.strip()
            if not tok: continue
            k,v = tok.split('=')
            out[k.strip()] = float(eval(v.strip(), {'__builtins__': {}}, SAFE_FUNCS | out))
        return out
    def _ueval(expr: str, params: dict) -> float:
        SAFE_FUNCS = {'pi': _m.pi, 'e': _m.e}
        return float(eval(expr, {'__builtins__': {}}, SAFE_FUNCS | params))

try:
    from .core import frequency_response_arrays, get_margins, set_gain_for_Kv
except Exception:
    # Local fallbacks for smoke tests
    def frequency_response_arrays(G: ct.lti, w: np.ndarray):
        mag, phase, omega = ct.frequency_response(G, w)
        return np.squeeze(mag), np.squeeze(phase), np.squeeze(omega)
    def get_margins(G: ct.lti):
        gm, pm, wgm, wpm = ct.margin(G)
        if isinstance(gm, (list, tuple)):  # normalize shape across versions
            gm, pm, wgm, wpm = gm[0], pm[0], wgm[0], wpm[0]
        return float(gm), float(pm), float(wgm), float(wpm)
    def set_gain_for_Kv(G: ct.lti, Kv_target: float):
        # Basic type-1 scaling (best-effort fallback)
        Gtf = ct.tf(G)
        num, den = ct.tfdata(Gtf)
        num = np.array(num[0][0], dtype=float)
        den = np.array(den[0][0], dtype=float)
        if abs(den[-1]) > 1e-14:
            raise ValueError('Kv only defined for type-1 plants.')
        Kv_old = num[-1]/den[-2]
        Kscale = Kv_target / Kv_old
        return Kscale*Gtf, float(Kscale), float(Kv_old)

def _parse_vec(s: str | None, params: dict) -> List[float]:
    if not s: return []
    toks = [t for t in s.replace(',', ' ').split() if t.strip()]
    return [float(_ueval(t, params)) for t in toks]

def _build_plant(plant: PlantSpec, params: dict) -> ct.lti:
    # Priority: SS > ZPK > TF > tf_expr
    if plant.A and plant.B and plant.C:
        def mat(m): 
            rows = [[_ueval(x, params) for x in r.strip().split(',')] for r in plant.A.split(';')]
            return np.array(rows, dtype=float)
        A = np.array([[float(_ueval(x, params)) for x in r.strip().split(',')] for r in plant.A.split(';')])
        B = np.array([[float(_ueval(x, params)) for x in r.strip().split(',')] for r in plant.B.split(';')])
        C = np.array([[float(_ueval(x, params)) for x in r.strip().split(',')] for r in plant.C.split(';')])
        D = np.array([[0.0]]) if not plant.D else np.array([[float(_ueval(x, params)) for x in r.strip().split(',')] for r in plant.D.split(';')])
        return ct.ss(A,B,C,D)
    if (plant.z is not None) or (plant.p is not None) or (plant.k is not None):
        z = _parse_vec(plant.z, params)
        p = _parse_vec(plant.p, params)
        k = 1.0 if plant.k is None else float(_ueval(plant.k, params))
        return ct.zpk(z, p, k)
    if (plant.num is not None) and (plant.den is not None):
        num = _parse_vec(plant.num, params); den = _parse_vec(plant.den, params)
        return ct.tf(num, den)
    if plant.tf_expr:
        # very simple evaluator; your utils.tf_from_expr likely does better
        s = ct.TransferFunction.s
        return eval(plant.tf_expr, {'s': s, '__builtins__': {}}, {})
    raise ValueError('Plant not specified.')

@dataclass(slots=True)
class LeadStage:
    alpha: float
    T: float
    wz: float
    wp: float

def _alpha_from_phi(phi_deg: float) -> float:
    phi = max(0.1, min(85.0, float(phi_deg)))
    s = math.sin(math.radians(phi))
    a = (1 - s) / (1 + s)
    return float(np.clip(a, 1e-6, 0.999))

class LeadDesigner:
    def run(self, spec: LeadDesignSpec) -> LeadDesignResult:
        params = parse_params(spec.plant.params)
        G1 = _build_plant(spec.plant, params)

        # Optional Kv scaling
        if spec.design.Kv is not None:
            G1, Kscale, Kv_old = set_gain_for_Kv(G1, float(spec.design.Kv))
            logging.info("Kv scaling: Kv_old=%.6g -> Kv_target=%.6g ; Kscale=%.6g", Kv_old, spec.design.Kv, Kscale)

        # Frequency grid
        w = np.logspace(np.log10(spec.grid.wmin), np.log10(spec.grid.wmax), spec.grid.wnum)

        # Manual single-stage path
        stages: List[LeadStage] = []
        wc = float('nan')
        if (spec.design.alpha is not None) and (spec.design.T is not None):
            a = float(spec.design.alpha); T = float(spec.design.T)
            stages = [LeadStage(alpha=a, T=T, wz=1.0/T, wp=1.0/(a*T))]
            Kc = 1.0 if spec.design.Kc is None else float(spec.design.Kc)
        else:
            # Auto design requires pm_target
            if spec.design.pm_target is None:
                raise ValueError('Lead design requires either (alpha & T) or lead_pm_target.')
            stages, Kc, wc = self._auto_design(G1, float(spec.design.pm_target), float(spec.design.pm_add),
                                               int(spec.design.stages), spec.design.phi_split, w)

        # Compose compensator
        Gc = ct.tf([1],[1])
        for st in stages:
            Gc *= ct.tf([st.T, 1.0], [st.alpha*st.T, 1.0])
        if not math.isnan(Kc): Gc *= Kc

        G_ol_c = ct.minreal(Gc * G1, verbose=False)

        # Margins
        gm_u, pm_u, wgm_u, wpm_u = get_margins(G1)
        gm_c, pm_c, wgm_c, wpm_c = get_margins(G_ol_c)

        pack = {
            'uncomp_margins': {'PM_deg': pm_u, 'w_PM': wpm_u, 'GM_abs': gm_u, 'GM_dB': (db(gm_u) if np.isfinite(gm_u) else float('inf')), 'w_GM': wgm_u},
            'comp_margins':   {'PM_deg': pm_c, 'w_PM': wpm_c, 'GM_abs': gm_c, 'GM_dB': (db(gm_c) if np.isfinite(gm_c) else float('inf')), 'w_GM': wgm_c},
            'lead': {
                'stages': [{'alpha': st.alpha, 'T': st.T, 'wz': st.wz, 'wp': st.wp} for st in stages],
                'Kc': float(Kc), 'wc': float(wc),
            },
        }

        # Optional exports/plots via io module if available
        files: List[str] = []
        try:
            from . import io as io_mod  # type: ignore
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
                nichols_Mdb=plot.nichols_Mdb,
                nichols_Ndeg=plot.nichols_Ndeg,
                nyquist_M=plot.nyquist_M,
                nyquist_marks=plot.nyquist_marks,
                save_tmpl=plot.save, save_img_tmpl=plot.save_img,
                no_show=plot.no_show, show_unstable=plot.show_unstable,
            )
        except Exception:
            # io helpers not available in this environment; ignore
            pass

        return LeadDesignResult(pack=pack, files=files)

    def _auto_design(self, G1: ct.lti, pm_target: float, pm_add: float, stages: int,
                     phi_split: Optional[str], w: np.ndarray):
        gm, pm, wgm, wpm = get_margins(G1)
        phi_total = pm_target - pm + pm_add
        if phi_total <= 0:
            logging.warning('Target PM already met; forcing φ_total=10° minimum.')
            phi_total = 10.0
        nst = max(1, int(stages))
        if phi_split:
            parts = [float(t) for t in phi_split.replace(',', ' ').split() if t.strip()]
            s = sum(parts) or 1.0
            phi_list = [phi_total * (x/s) for x in parts[:nst]]
            if len(phi_list) < nst:
                phi_list += [phi_total / nst] * (nst - len(phi_list))
        else:
            phi_list = [phi_total / nst] * nst

        alpha_list = [_alpha_from_phi(p) for p in phi_list]
        alpha_prod = float(np.prod(alpha_list))

        mag, _, ww = frequency_response_arrays(G1, w)
        target = 1.0 / math.sqrt(alpha_prod)
        idx = int(np.argmin(np.abs(mag - target)))
        wc = float(ww[idx])

        stages_out: List[LeadStage] = []
        for a in alpha_list:
            T = 1.0 / (wc * math.sqrt(a))
            stages_out.append(LeadStage(alpha=a, T=T, wz=1.0/T, wp=1.0/(a*T)))

        Gc_base = ct.tf([1],[1])
        for st in stages_out:
            Gc_base *= ct.tf([st.T, 1.0], [st.alpha*st.T, 1.0])
        Gw = ct.evalfr(G1, 1j*wc); Gcb = ct.evalfr(Gc_base, 1j*wc)
        Kc = 1.0 / max(abs(Gw * Gcb), 1e-16)
        return stages_out, float(Kc), float(wc)
