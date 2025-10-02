
from __future__ import annotations
import numpy as np, control as ct
from typing import Optional, List, Tuple

from .core import frequency_response_arrays, get_margins, eval_L
from .utils import db

def _wrap_nichols(ph_rad: np.ndarray) -> np.ndarray:
    deg=np.rad2deg(ph_rad); deg=(deg+360.0)%360.0; return deg-360.0

def get_margins_safe(G: ct.lti) -> Tuple[float,float,float,float]:
    gm, pm, wgm, wpm = get_margins(G)
    return gm, pm, (wgm if np.isfinite(wgm) else None), (wpm if np.isfinite(wpm) else None)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, LogLocator, NullFormatter

def _new_fig(*args, **kwargs):
    kwargs.setdefault('constrained_layout', True)
    return plt.figure(*args, **kwargs)

def _add_log_minor_grid(ax):
    ax.grid(True, which='both', alpha=0.6)
    ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2,10)*0.1))
    ax.xaxis.set_minor_formatter(NullFormatter())

def plot_bode_mpl(series, w, title='Bode', wgm=None, wpm=None):
    fig = _new_fig(figsize=(9.8, 6.3))
    gs = fig.add_gridspec(2, 1, height_ratios=[1,1])
    axm = fig.add_subplot(gs[0,0])
    axp = fig.add_subplot(gs[1,0], sharex=axm)
    for label,G in series:
        mag, ph, _ = frequency_response_arrays(G,w)
        axm.semilogx(w, db(mag), lw=2, label=label)
        axp.semilogx(w, np.rad2deg(ph), lw=2, label=label)
    axm.axhline(0,color='k',ls='--',lw=0.9,alpha=0.7)
    _add_log_minor_grid(axm); _add_log_minor_grid(axp)
    axm.yaxis.set_major_locator(MultipleLocator(10)); axm.yaxis.set_minor_locator(MultipleLocator(2))
    axp.yaxis.set_major_locator(MultipleLocator(10)); axp.yaxis.set_minor_locator(MultipleLocator(5))
    def _vline(ax, x, label):
        if x is None: return
        ax.axvline(x=x, color='k', ls='--', lw=1.1, alpha=0.85)
        ax.text(x, ax.get_ylim()[1], f' {label}={x:.3g}', va='bottom', ha='left', fontsize=9, rotation=90)
    _vline(axm, wgm, 'wgc'); _vline(axp, wgm, 'wgc')
    _vline(axm, wpm, 'wpc'); _vline(axp, wpm, 'wpc')
    axm.legend(loc='best'); fig.suptitle(title)
    axp.set_xlabel('w (rad/s)'); axm.set_ylabel('dB'); axp.set_ylabel('deg')
    return fig

def _m_circle_xy(M: float, npts=800):
    M2 = M*M
    c = -M2/(M2 - 1.0)
    r =  M/abs(M2 - 1.0)
    th = np.linspace(0, 2*np.pi, npts)
    x = c + r*np.cos(th); y = r*np.sin(th)
    return x, y, c, r

def _annotate_nyq_marks(ax, G: ct.lti, marks: List[float], color='k'):
    if not marks: return
    for w in marks:
        m = eval_L(ct.tf(G), np.array([w]))[0]
        ax.plot(m.real, m.imag, 'o', ms=4, color=color)
        ax.text(m.real+0.08, m.imag+0.08, f'{w:g}', fontsize=9, color=color)

def plot_nyquist_mpl(series, w, title='Nyquist', ogata_axes=False, Mlist: Optional[List[float]]=None,
                     freq_marks: Optional[List[float]]=None):
    fig=_new_fig(figsize=(6.8,6.8)); ax=fig.add_subplot(111)
    for label,G in series:
        Gjw = eval_L(ct.tf(G), w)
        track=np.concatenate([np.conj(Gjw[::-1]), Gjw])
        ax.plot(track.real, track.imag, lw=2, label=label)
    if Mlist:
        for M in Mlist:
            x,y,_,_=_m_circle_xy(M)
            ax.plot(x,y, color='0.6', lw=1.0, ls='-')
    if freq_marks:
        _annotate_nyq_marks(ax, series[-1][1], freq_marks, color='k')
    ax.plot([-1],[0],'ko',ms=6,label='-1+j0')
    ax.axhline(0,color='k',lw=0.8); ax.axvline(0,color='k',lw=0.8)
    ax.set_aspect('equal',adjustable='box'); ax.grid(True, alpha=0.6); ax.legend(loc='best')
    if ogata_axes:
        ax.set_xlim(-8,2); ax.set_ylim(-8,2)
    ax.set_xlabel('Re{G(jw)}'); ax.set_ylabel('Im{G(jw)}'); ax.set_title(title)
    return fig

def build_nichols_templates(Mdb_list, Ndeg_list):
    from .core import nichols_templates
    return nichols_templates(Mdb_list, Ndeg_list)

def plot_nichols_mpl(series, w, title='Nichols', templates=None):
    fig=_new_fig(figsize=(10.8,6.0)); ax=fig.add_subplot(111)
    for label,G in series:
        mag,ph,_=frequency_response_arrays(G,w)
        ax.plot(_wrap_nichols(ph), db(mag), lw=2, label=label)
    if templates:
        M_lines,N_lines=templates
        for phs,gdbs,name in M_lines: ax.plot(phs,gdbs,'--',lw=0.9,color='0.6')
        for phs,gdbs,name in N_lines: ax.plot(phs,gdbs,':',lw=0.9,color='0.6')
    ax.axhline(0,color='k',lw=0.8,ls='--',alpha=0.75)
    ax.grid(True,which='both', alpha=0.6); ax.legend(loc='best')
    ax.set_xlabel('Phase (deg)'); ax.set_ylabel('Gain (dB)'); ax.set_title(title)
    ax.set_xlim(-360,0); ax.set_ylim(-60,40)
    return fig

def _time_vector_from_wc(wc: float, kind='step'):
    if not np.isfinite(wc) or wc<=0: T0=4.0
    else: T0=2*np.pi/wc
    if kind=='step': return np.linspace(0, 8*T0, 2200)
    return np.linspace(0, 8*T0, 2200)

def plot_step_mpl(G1: ct.lti, G_ol_c: ct.lti, w, ogata_axes: bool):
    Gcl_base = ct.feedback(G1, 1)
    Gcl_comp = ct.feedback(G_ol_c, 1)
    _, _, _, wpm_c = get_margins(G_ol_c)
    _, _, _, wpm_u = get_margins(G1)
    ref_w = (wpm_c if np.isfinite(wpm_c) and wpm_c>0 else (wpm_u if np.isfinite(wpm_u) and wpm_u>0 else 1.0))
    t = _time_vector_from_wc(ref_w, 'step')
    if ogata_axes: 
        import numpy as _np
        t=_np.linspace(0,40.0,max(1200,len(t)))
    T1,y1 = ct.step_response(Gcl_base, T=t)
    T2,y2 = ct.step_response(Gcl_comp, T=t)
    fig=_new_fig(figsize=(11.5,3.8)); ax=fig.add_subplot(111)
    ax.plot(T1,y1,lw=2,label='Uncomp CL')
    ax.plot(T2,y2,lw=2,label='Comp CL')
    ax.grid(True); ax.legend(loc='best'); ax.set_xlabel('t (s)'); ax.set_ylabel('y(t)'); ax.set_title('Unit Step')
    if ogata_axes: ax.set_xlim(0,40)
    return fig

def plot_ramp_mpl(G1: ct.lti, G_ol_c: ct.lti, w, ogata_axes: bool):
    Gcl_base = ct.feedback(G1, 1)
    Gcl_comp = ct.feedback(G_ol_c, 1)
    _, _, _, wpm_c = get_margins(G_ol_c)
    _, _, _, wpm_u = get_margins(G1)
    ref_w = (wpm_c if np.isfinite(wpm_c) and wpm_c>0 else (wpm_u if np.isfinite(wpm_u) and wpm_u>0 else 1.0))
    t = _time_vector_from_wc(ref_w, 'ramp')
    if ogata_axes: 
        import numpy as _np
        t=_np.linspace(0,20.0,max(1200,len(t)//2))
    u = t
    T1,y1,_ = ct.forced_response(Gcl_base, T=t, U=u)
    T2,y2,_ = ct.forced_response(Gcl_comp, T=t, U=u)
    fig=_new_fig(figsize=(10.5,6.0)); ax=fig.add_subplot(111)
    ax.plot(t,t,'--',color='0.5',lw=1.5,label='Reference r(t)=t')
    ax.plot(T1,y1,lw=2,label='Uncomp CL')
    ax.plot(T2,y2,lw=2,label='Comp CL')
    if ogata_axes: ax.set_xlim(0,20); ax.set_ylim(0,20); ax.set_aspect('equal', adjustable='box')
    ax.grid(True); ax.legend(loc='best'); ax.set_xlabel('t (s)'); ax.set_ylabel('y(t)'); ax.set_title('Unit Ramp')
    return fig

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    _HAVE_PLOTLY = True
except Exception:
    _HAVE_PLOTLY = False

def bode_plotly(series, w, title='Bode', wgm=None, wpm=None):
    if not _HAVE_PLOTLY:
        raise RuntimeError('Plotly not available')
    fig=make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                      subplot_titles=('Magnitude (dB)','Phase (deg)'))
    for label,G in series:
        mag,ph,_=frequency_response_arrays(G,w)
        fig.add_trace(go.Scatter(x=w, y=db(mag), name=label, mode='lines'), row=1,col=1)
        fig.add_trace(go.Scatter(x=w, y=np.rad2deg(ph), name=label, mode='lines', showlegend=False), row=2,col=1)
    fig.update_xaxes(type='log', row=1, col=1); fig.update_xaxes(type='log', row=2, col=1)
    fig.update_yaxes(dtick=10, row=1, col=1); fig.update_yaxes(dtick=10, row=2, col=1)
    def _add_vline(x, label):
        if x is None: return
        for r in (1,2):
            fig.add_vline(x=x, line_dash='dash', line_width=1, line_color='black', row=r, col=1)
        fig.add_annotation(x=x, y=1.02, xref='x', yref='paper', text=f'{label}={x:.3g}', showarrow=False)
    _add_vline(wgm, 'wgc'); _add_vline(wpm, 'wpc')
    fig.update_layout(title=title, template='plotly_white',
                      autosize=True, margin=dict(l=60,r=20,b=60,t=60),
                      legend=dict(x=0.02,y=0.98))
    return fig

def nyquist_plotly(series, w, title='Nyquist', ogata_axes=False, Mlist: Optional[List[float]]=None,
                   freq_marks: Optional[List[float]]=None):
    if not _HAVE_PLOTLY:
        raise RuntimeError('Plotly not available')
    fig=go.Figure()
    for label,G in series:
        Gjw=eval_L(ct.tf(G), w); track=np.concatenate([np.conj(Gjw[::-1]),Gjw])
        fig.add_trace(go.Scatter(x=track.real, y=track.imag, name=label, mode='lines'))
    if Mlist:
        for M in Mlist:
            x,y,_,_= _m_circle_xy(M)
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='gray', width=1), name=f'M={M:g}', showlegend=False))
    if freq_marks:
        pts = eval_L(ct.tf(series[-1][1]), np.asarray(freq_marks))
        fig.add_trace(go.Scatter(x=pts.real, y=pts.imag, mode='markers+text',
                                 text=[f'{w:g}' for w in freq_marks], textposition='top right',
                                 marker=dict(size=7), name='w marks'))
    fig.add_trace(go.Scatter(x=[-1],y=[0],mode='markers',marker=dict(color='black',size=8),name='-1+j0'))
    fig.update_layout(title=title, xaxis_title='Re{G(jw)}', yaxis_title='Im{G(jw)}',
                      template='plotly_white', autosize=True, margin=dict(l=60,r=20,b=60,t=60))
    fig.update_yaxes(scaleanchor='x', scaleratio=1)
    if ogata_axes:
        fig.update_xaxes(range=[-8,2]); fig.update_yaxes(range=[-8,2])
    return fig

def nichols_plotly(series, w, title='Nichols', templates=None):
    if not _HAVE_PLOTLY:
        raise RuntimeError('Plotly not available')
    fig=go.Figure()
    for label,G in series:
        mag,ph,_=frequency_response_arrays(G,w)
        fig.add_trace(go.Scatter(x=_wrap_nichols(ph), y=db(mag), name=label, mode='lines'))
    if templates:
        M_lines,N_lines=templates
        for phs,gdbs,name in M_lines:
            fig.add_trace(go.Scatter(x=phs, y=gdbs, mode='lines', line=dict(dash='dash', width=1, color='gray'), name=name, showlegend=False))
        for phs,gdbs,name in N_lines:
            fig.add_trace(go.Scatter(x=phs, y=gdbs, mode='lines', line=dict(dash='dot', width=1, color='gray'), name=name, showlegend=False))
    fig.update_layout(title=title, xaxis_title='Phase (deg)', yaxis_title='Gain (dB)',
                      template='plotly_white', autosize=True, margin=dict(l=60,r=20,b=60,t=60))
    fig.update_xaxes(range=[-360,0]); fig.update_yaxes(range=[-60,40], dtick=10)
    return fig
