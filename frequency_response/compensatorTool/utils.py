
from __future__ import annotations
import math, numpy as np, control as ct
from typing import Optional

_EPS = np.finfo(float).tiny

def db(x):
    arr = np.asanyarray(x)
    arr = np.maximum(arr, _EPS)
    return 20.0*np.log10(arr)

def undb(x_db):
    return 10.0**(np.asanyarray(x_db)/20.0)

def parse_list_floats(s) -> Optional[list[float]]:
    if s is None:
        return None
    if isinstance(s, (list, tuple, np.ndarray)):
        return [float(v) for v in s]
    vals=[]
    for tok in str(s).replace(',', ' ').split():
        try: vals.append(float(tok))
        except: pass
    return vals or None

SAFE_FUNCS = {k: getattr(math, k) for k in [
    'sin','cos','tan','asin','acos','atan','atan2','sinh','cosh','tanh',
    'exp','log','log10','sqrt','pi','e'
]}
SAFE_FUNCS.update({'j':1j,'J':1j})

def _eval(expr: str, params: dict) -> float:
    return float(eval(expr, {'__builtins__': {}}, {**SAFE_FUNCS, **params}))

def parse_params(s: str) -> dict:
    if not s: return {}
    out={}
    for tok in s.split(','):
        tok = tok.strip()
        if not tok:
            continue
        k,v = tok.split('=')
        out[k.strip()] = float(eval(v.strip(), {'__builtins__': {}}, {**SAFE_FUNCS, **out}))
    return out

class _RF:
    def __init__(self, num, den=1.0):
        import numpy as _np
        self.num = _np.poly1d(num if isinstance(num,_np.poly1d) else [float(num)] if _np.isscalar(num) else list(num))
        self.den = _np.poly1d(den if isinstance(den,_np.poly1d) else [float(den)] if _np.isscalar(den) else list(den))
    def _rf(self,o):
        return o if isinstance(o,_RF) else _RF(o,1.0)
    def __add__(self,o):
        o=self._rf(o)
        return _RF(self.num*o.den + o.num*self.den, self.den*o.den)
    __radd__=__add__
    def __sub__(self,o):
        o=self._rf(o)
        return _RF(self.num*o.den - o.num*self.den, self.den*o.den)
    def __rsub__(self,o):
        o=self._rf(o)
        return _RF(o.num*self.den - self.num*o.den, self.den*o.den)
    def __mul__(self,o):
        o=self._rf(o)
        return _RF(self.num*o.num, self.den*o.den)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=self._rf(o)
        return _RF(self.num*o.den, self.den*o.num)
    def __rtruediv__(self,o):
        o=self._rf(o)
        return _RF(o.num*self.den, o.den*self.num)
    def __neg__(self):
        return _RF(-self.num, self.den)
    def __pow__(self,n):
        if int(n)!=n or n<0:
            raise ValueError('Only non-negative integer powers supported in --tf.')
        n=int(n)
        return _RF([1.0],[1.0]) if n==0 else _RF(self.num**n, self.den**n)
    def tf(self):
        return ct.tf(self.num.c, self.den.c)

def tf_from_expr(expr: str, params: dict) -> ct.TransferFunction:
    if not expr or not expr.strip():
        raise ValueError('Empty --tf expression.')
    e = expr.replace('^','**')
    env = {'__builtins__': {}}
    env.update({k:float(v) for k,v in params.items()})
    s=_RF([1.0,0.0],1.0)
    env['s']=s; env['rf']=_RF
    val=eval(e, env, {})
    if isinstance(val,_RF):
        return val.tf()
    try:
        c=float(val)
        return ct.tf([c],[1.0])
    except Exception:
        raise ValueError('Could not parse --tf expression.')
