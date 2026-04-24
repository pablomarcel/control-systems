
from __future__ import annotations
import numpy as np, control as ct
from typing import Tuple
from .utils import db, undb

def tf_arrays(G: ct.TransferFunction):
    num, den = ct.tfdata(G)
    import numpy as _np
    num=_np.asarray(num,dtype=object); den=_np.asarray(den,dtype=object)
    while _np.ndim(num)>1: num=num[0]
    while _np.ndim(den)>1: den=den[0]
    return _np.asarray(num,float).ravel(), _np.asarray(den,float).ravel()

def eval_L(G: ct.TransferFunction, w: np.ndarray) -> np.ndarray:
    n,d=tf_arrays(G); s=1j*np.asarray(w,float)
    return np.polyval(n,s)/np.polyval(d,s)

def frequency_response_arrays(G: ct.lti, w: np.ndarray):
    try:
        mag, ph, ww = ct.frequency_response(G, w)
        return np.squeeze(mag), np.unwrap(np.squeeze(ph)), np.squeeze(ww)
    except Exception:
        if isinstance(G, ct.TransferFunction):
            Hjw=eval_L(G,w)
            return np.abs(Hjw), np.unwrap(np.angle(Hjw)), w
        raise

def get_margins(G: ct.lti) -> Tuple[float,float,float,float]:
    try:
        ret=ct.margin(G)
        if isinstance(ret,(list,tuple)) and len(ret)>=4:
            gm,pm,wgm,wpm = [float(ret[i]) for i in range(4)]
            return gm,pm,wgm,wpm
        return float(getattr(ret,'gain_margin',np.nan)), float(getattr(ret,'phase_margin',np.nan)), \
               float(getattr(ret,'gain_cross_frequency',getattr(ret,'wgm',np.nan))), float(getattr(ret,'phase_cross_frequency',getattr(ret,'wpm',np.nan)))
    except Exception:
        pass
    try:
        sm=ct.stability_margins(G)
        if isinstance(sm,(list,tuple)) and len(sm)>=4:
            gm,pm,wgm,wpm=sm[0],sm[1],sm[2],sm[3]
        else:
            gm=getattr(sm,'gain_margin',np.nan); pm=getattr(sm,'phase_margin',np.nan)
            wgm=getattr(sm,'gain_cross_frequency',np.nan); wpm=getattr(sm,'phase_cross_frequency',np.nan)
        return float(gm),float(pm),float(wgm),float(wpm)
    except Exception:
        return float('nan'),float('nan'),float('nan'),float('nan')

def is_stable(sys: ct.lti) -> bool:
    try:
        poles = ct.poles(sys)
        return np.all(np.real(poles) < 0)
    except Exception:
        return False

def kv_of_tf(sys_tf: ct.TransferFunction) -> float:
    num, den = ct.tfdata(sys_tf)
    num=np.array(num[0][0], float); den=np.array(den[0][0], float)
    if abs(den[-1])>1e-14:
        raise ValueError('Kv only defined for type-1 (den constant term == 0).')
    if len(den)<2:
        raise ValueError('Denominator too short for type-1.')
    a1=den[-2]; N0=num[-1]
    return N0/a1

def set_gain_for_Kv(G: ct.lti, Kv_target: float):
    Gtf=ct.tf(G); Kv_old=kv_of_tf(Gtf)
    if abs(Kv_old)<1e-15:
        raise ValueError('Kv_old is 0; cannot scale.')
    Kscale=Kv_target/Kv_old
    return Kscale*Gtf, float(Kscale), float(Kv_old)

def nichols_templates(Mdb_list, Ndeg_list, phase_span=(-360.0,0.0), npts=800):
    lines_M, lines_N = [], []
    with np.errstate(divide='ignore', invalid='ignore'):
        for Mdb in Mdb_list or []:
            Mabs = undb(Mdb); phs=np.linspace(*phase_span, npts)
            T = Mabs*np.exp(1j*np.deg2rad(phs))
            mask = np.abs(1.0 - T) > 1e-12
            L = T[mask]/(1.0 - T[mask])
            if L.size: lines_M.append((np.angle(L,deg=True), db(np.abs(L)), f'M={Mdb:g} dB'))
        for Ndeg in Ndeg_list or []:
            Mabs=np.logspace(-3,1,npts)
            T=Mabs*np.exp(1j*np.deg2rad(Ndeg))
            mask = np.abs(1.0 - T) > 1e-12
            L=T[mask]/(1.0 - T[mask])
            if L.size: lines_N.append((np.angle(L,deg=True), db(np.abs(L)), f'N={Ndeg:g} deg'))
    return lines_M, lines_N
