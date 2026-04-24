# root_locus_analysis/systemResponseTool/utils.py
from __future__ import annotations
import logging
import math
import sys
from typing import List
import numpy as np
import plotly.graph_objects as go

# ---------- logging ----------
def make_logger(name: str = "systemResponseTool", level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        h = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter("%(levelname)-7s %(name)s:%(filename)s:%(funcName)s()- %(message)s")
        h.setFormatter(fmt)
        logger.addHandler(h)
    return logger

# ---------- time grid ----------
def time_grid(tfinal: float, dt: float) -> np.ndarray:
    n = int(math.floor(tfinal / dt)) + 1
    return np.linspace(0.0, tfinal, n)

# ---------- plot shell ----------
def default_palette():
    return [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
        "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
        "#bcbd22", "#17becf",
    ]

def make_figure(title: str, ylab: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title=title, template="plotly_white", width=1200, height=650,
        xaxis_title="Time (s)", yaxis_title=ylab,
        legend=dict(x=0.02, y=0.98),
        margin=dict(l=50, r=30, t=70, b=50),
    )
    return fig

def add_trace(fig: go.Figure, T, y, name, color, dash, width):
    fig.add_trace(go.Scatter(
        x=T, y=y, mode="lines", name=name,
        line=dict(color=color, dash=dash, width=width)
    ))

# ---------- parsing utils ----------
def _strip_brackets(s: str) -> str:
    return s.replace("[", " ").replace("]", " ").strip()

def parse_vector(s: str) -> np.ndarray:
    s = _strip_brackets(s)
    toks = [t for t in s.replace(",", " ").replace(";", " ").split() if t.strip()]
    return np.array([float(t) for t in toks], dtype=float)

def parse_matrix(s: str) -> np.ndarray:
    s = _strip_brackets(s)
    rows = [r for r in s.split(";") if r.strip()]
    data: List[List[float]] = []
    for r in rows:
        toks = [t for t in r.replace(",", " ").split() if t.strip()]
        if toks:
            data.append([float(t) for t in toks])
    return np.array(data, dtype=float)

def split_top_level(s: str, sep: str = ";") -> List[str]:
    out, buf = [], []
    depth, in_quote, q = 0, False, ""
    for ch in s:
        if in_quote:
            buf.append(ch)
            if ch == q:
                in_quote = False
            continue
        if ch in ("'", '"'):
            in_quote, q = True, ch; buf.append(ch); continue
        if ch == "[":
            depth += 1; buf.append(ch); continue
        if ch == "]":
            depth = max(0, depth-1); buf.append(ch); continue
        if ch == sep and depth == 0:
            tok = "".join(buf).strip()
            if tok: out.append(tok)
            buf = []; continue
        buf.append(ch)
    tok = "".join(buf).strip()
    if tok: out.append(tok)
    return out

def _split_mul(expr: str) -> List[str]:
    out, buf, depth = [], [], 0
    for ch in expr:
        if ch == "(":
            depth += 1; buf.append(ch); continue
        if ch == ")":
            depth = max(0, depth-1); buf.append(ch); continue
        if ch == "*" and depth == 0:
            tok = "".join(buf).strip()
            if tok: out.append(tok)
            buf = []; continue
        buf.append(ch)
    tok = "".join(buf).strip();
    if tok: out.append(tok)
    return out

def poly_from_factor_expr(expr: str) -> np.ndarray:
    e = expr.strip().replace(" ", "")
    if not e:
        raise ValueError("Empty polynomial expression.")
    terms = _split_mul(e)
    coef = 1.0
    poly = np.array([1.0])
    for t in terms:
        if t == "s":
            poly = np.convolve(poly, np.array([1.0, 0.0]))
        elif t.startswith("(s+"):
            a = float(t[3:-1]); poly = np.convolve(poly, np.array([1.0, a]))
        elif t.startswith("(s-"):
            a = float(t[3:-1]); poly = np.convolve(poly, np.array([1.0, -a]))
        elif t.replace(".", "", 1).replace("-", "", 1).isdigit() or \
             (t and t[0] in "+-" and t[1:].replace(".", "", 1).isdigit()):
            coef *= float(t)
        else:
            if t.startswith("(") and t.endswith(")") and ("s+" in t or "s-" in t):
                inner = t[1:-1]
                for sub in _split_mul(inner.replace(")(", ")*(")):
                    poly = np.convolve(poly, poly_from_factor_expr(sub))
            else:
                raise ValueError(f"Unsupported factor '{t}' in '{expr}'")
    return (coef * poly).astype(float)

def parse_poly(s: str) -> np.ndarray:
    if "s" in s or "(" in s:
        return poly_from_factor_expr(s)
    s2 = _strip_brackets(s)
    toks = [t for t in s2.replace(",", " ").split() if t.strip()]
    return np.array([float(t) for t in toks], dtype=float)
