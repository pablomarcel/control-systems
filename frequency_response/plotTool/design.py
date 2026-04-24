from __future__ import annotations
from typing import List, Tuple, Optional
import numpy as np
import control as ct
from .utils import parse_list, parse_roots, parse_factors

def tf_arrays(G: ct.TransferFunction):
    try:
        num, den = ct.tfdata(G, squeeze=True)
    except TypeError:
        num, den = ct.tfdata(G)
        def _flat(a):
            while isinstance(a, (list, tuple, np.ndarray)):
                if isinstance(a, np.ndarray) and a.ndim == 1: break
                a = a[0]
            return a
        num, den = _flat(num), _flat(den)
    return np.asarray(num, float).ravel(), np.asarray(den, float).ravel()

def build_tf_from_modes(
    num: Optional[str], den: Optional[str],
    gain: Optional[float], zeros: Optional[str], poles: Optional[str],
    fnum: Optional[str], fden: Optional[str], K: Optional[float]
) -> ct.TransferFunction:
    mode = 0
    if num or den: mode += 1
    if (gain is not None) or zeros or poles: mode += 1
    if fnum or fden: mode += 1
    if mode != 1:
        raise ValueError("Use exactly one: (--num/--den) OR (--gain/--zeros/--poles) OR (--fnum/--fden).")
    if fnum or fden:
        kval = 1.0 if K is None else K
        n = parse_factors(fnum or "1", Kval=kval)
        d = parse_factors(fden or "1", Kval=kval)
        return ct.tf(n, d)
    if (gain is not None) or zeros or poles:
        z = parse_roots(zeros); p = parse_roots(poles)
        n = np.poly(z) if z else np.array([1.0])
        n = (gain if gain is not None else 1.0) * n
        d = np.poly(p) if p else np.array([1.0])
        return ct.tf(n, d)
    return ct.tf(parse_list(num or "1"), parse_list(den or "1"))

def build_L_from_args(args) -> Tuple[List[ct.TransferFunction], List[str]]:
    chans: List[ct.TransferFunction] = []; names: List[str] = []
    if getattr(args, "A", None) and getattr(args, "B", None) and getattr(args, "C", None):
        import numpy as np
        from .utils import parse_matrix
        A = parse_matrix(args.A); B = parse_matrix(args.B)
        C = parse_matrix(args.C); D = parse_matrix(args.D) if args.D else np.zeros((C.shape[0], B.shape[1]))
        SS = ct.ss(A, B, C, D)
        TFm = ct.ss2tf(SS)
        for i in range(TFm.noutputs):
            for j in range(TFm.ninputs):
                G = ct.tf(np.asarray(TFm.num[i][j]).ravel(), np.asarray(TFm.den[i][j]).ravel())
                if args.scale is not None:
                    G = args.scale * G
                chans.append(ct.minreal(G, verbose=False))
                names.append(f"y{i+1} from u{j+1}")
        return chans, names
    G = build_tf_from_modes(args.num, args.den, args.gain, args.zeros, args.poles, args.fnum, args.fden, args.K)
    if args.scale is not None:
        G = args.scale * G
    return [ct.minreal(G, verbose=False)], ["y1 from u1"]
