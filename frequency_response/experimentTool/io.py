from __future__ import annotations
from dataclasses import asdict
from typing import Dict
import os, json, math
import numpy as np
import control as ct

from .design import ModelSpec
from .core import build_rational_tf, bode_arrays
from .utils import ensure_dir, info, np2list


def read_csv(csv_path: str) -> Dict[str, np.ndarray]:
    data = np.genfromtxt(csv_path, delimiter=",", names=True, dtype=float, encoding=None)
    names = [n.lower() for n in data.dtype.names]

    def col(*cands):
        for c in cands:
            if c in names:
                return np.asarray(data[c])
        raise KeyError(f"CSV missing any of columns {cands}")

    w = col("omega", "w")
    mag_db = col("mag_db", "mag")
    phase_deg = col("phase_deg", "phase")
    idx = np.argsort(w)
    D = {"w": w[idx], "mag_db": mag_db[idx], "phase_deg": phase_deg[idx]}
    info(f"CSV loaded: N={len(D['w'])}, w∈[{D['w'][0]:.3g},{D['w'][-1]:.3g}] rad/s")
    return D


def save_bode_csv(path_prefix: str, bode) -> str:
    outdir = ensure_dir(os.path.dirname(path_prefix) or ".")
    csv_path = os.path.join(outdir, f"{os.path.basename(path_prefix)}_bode.csv")
    np.savetxt(
        csv_path,
        np.column_stack([bode.w, bode.mag_db, bode.phase_deg]),
        delimiter=",",
        header="w,mag_db,phase_deg",
        comments=""
    )
    return csv_path


def export_summary(
    path_prefix: str,
    spec: ModelSpec,
    sys_for_freq,
    delay_method: str,
    pade_order: int | None,
    diagnostics: dict | None
) -> str:
    """
    JSON-safe export. Ensures all arrays are converted to plain lists.
    Poles/zeros are exported as [real, imag] pairs via np2list.
    """
    outdir = ensure_dir(os.path.dirname(path_prefix) or ".")
    js = os.path.join(outdir, f"{os.path.basename(path_prefix)}_summary.json")

    # Rational model (without Padé) for clean poles/zeros reporting
    G_rational = build_rational_tf(spec)

    # Numerator/denominator of the system used for frequency response (may include Padé TF)
    if hasattr(sys_for_freq, "num") and hasattr(sys_for_freq, "den"):
        try:
            num_list = np2list(sys_for_freq.num[0][0])
            den_list = np2list(sys_for_freq.den[0][0])
        except Exception:
            # Fallback for other shapes
            num_list = np2list(np.array(sys_for_freq.num, dtype=object))
            den_list = np2list(np.array(sys_for_freq.den, dtype=object))
    else:
        num_list = None
        den_list = None

    summary = {
        "spec": asdict(spec),
        "diagnostics": diagnostics if diagnostics else None,
        "rational_num": num_list,
        "rational_den": den_list,
        "delay_method": delay_method,
        "pade_order": pade_order,
        "poles": np2list(ct.poles(G_rational)),
        "zeros": np2list(ct.zeros(G_rational)),
    }

    with open(js, "w") as f:
        json.dump(summary, f, indent=2)
    return js


def make_synth_csv(
    spec: ModelSpec,
    wmin: float,
    wmax: float,
    npts: int,
    path: str,
    delay_method: str,
    noise_db: float,
    noise_deg: float
) -> str:
    ensure_dir(os.path.dirname(path) or ".")
    G = build_rational_tf(spec)
    sys_for_freq = G
    if delay_method == "pade" and spec.delay > 0:
        numd, dend = ct.pade(spec.delay, 6)
        sys_for_freq = G * ct.TransferFunction(numd, dend)
    w = np.logspace(math.log10(wmin), math.log10(wmax), npts)
    bode = bode_arrays(sys_for_freq, w, spec.delay, delay_method=delay_method)
    mag_db, phase_deg = bode.mag_db.copy(), bode.phase_deg.copy()
    if noise_db > 0:
        mag_db = mag_db + np.random.normal(0, noise_db, size=mag_db.shape)
    if noise_deg > 0:
        phase_deg = phase_deg + np.random.normal(0, noise_deg, size=phase_deg.shape)
    np.savetxt(
        path,
        np.column_stack([w, mag_db, phase_deg]),
        delimiter=",",
        header="w,mag_db,phase_deg",
        comments=""
    )
    return path
