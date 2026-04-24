from __future__ import annotations
import logging, math
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import control as ct

from .apis import LagDesignSpec, LagDesignResult
from .utils import (
    parse_params,
    db,
    _eval as u_eval,
    tf_from_expr,
)
from .core import frequency_response_arrays, get_margins, set_gain_for_Kv


# ----------------------------- Local parsers (params-aware) -------------------
def parse_vector(vec: str | None, params: dict) -> np.ndarray | None:
    """Parse a comma/space-separated vector with symbol support via params."""
    if vec is None:
        return None
    s = vec.strip()
    if s == "":
        return np.array([], dtype=float)
    parts = [p.strip() for p in (s.split(",") if "," in s else s.split())]
    return np.array([float(u_eval(p, params)) for p in parts], dtype=float)


def parse_matrix(mat: str, params: dict) -> np.ndarray:
    """Parse a semicolon/comma-separated matrix with symbol support via params."""
    rows = [r.strip() for r in mat.split(";")]
    data = []
    for r in rows:
        parts = [p.strip() for p in r.split(",")]
        data.append([float(u_eval(p, params)) for p in parts])
    return np.array(data, dtype=float)


# ----------------------------- Builders ---------------------------------------
def _build_plant(spec, params: dict) -> ct.lti:
    """
    Build the plant from PlantSpec using common precedence:
    State-Space > ZPK > TF expr (--tf) > TF arrays. All parsing honors `params`.
    """
    # State-space (highest priority)
    if spec.A and spec.B and spec.C:
        A = parse_matrix(spec.A, params)
        B = parse_matrix(spec.B, params)
        C = parse_matrix(spec.C, params)
        D = parse_matrix(spec.D, params) if spec.D else np.zeros((C.shape[0], B.shape[1]))
        logging.info("Plant from State-Space: A%s B%s C%s D%s", A.shape, B.shape, C.shape, D.shape)
        return ct.ss(A, B, C, D)

    # ZPK
    if (spec.z is not None) or (spec.p is not None) or (spec.k is not None):
        z = [] if spec.z is None else list(parse_vector(spec.z, params).ravel())
        p = [] if spec.p is None else list(parse_vector(spec.p, params).ravel())
        if spec.k is None:
            k = 1.0
        else:
            k = float(u_eval(spec.k, params))
        logging.info("Plant from ZPK: z=%s p=%s k=%.6g", z, p, k)
        return ct.zpk(z, p, k)

    # TF expression (safe, params-aware)
    if spec.tf_expr:
        G = tf_from_expr(spec.tf_expr, params)
        logging.info("Plant from --tf: %s", G)
        return G

    # TF arrays
    if (spec.num is not None) and (spec.den is not None):
        num = parse_vector(spec.num, params)
        den = parse_vector(spec.den, params)
        logging.info("Plant from TF: num=%s den=%s", num, den)
        return ct.tf(num, den)

    raise ValueError("Plant not specified. Use --tf or --num/--den or ZPK/SS options.")


# ----------------------------- Data models ------------------------------------
@dataclass(slots=True)
class LagStage:
    beta: float
    T: float
    wz: float
    wp: float


# ----------------------------- Designer ---------------------------------------
class LagDesigner:
    """Lag-only designer (Ogata-style; single-stage auto/manual)."""

    def run(self, spec: LagDesignSpec) -> LagDesignResult:
        params = parse_params(spec.plant.params)
        G1 = _build_plant(spec.plant, params)

        # Optional Kv scaling (type-1)
        if spec.design.Kv is not None:
            G1, Kscale, Kv_old = set_gain_for_Kv(G1, float(spec.design.Kv))
            logging.info(
                "Kv scaling: Kv_old=%.6g -> Kv_target=%.6g ; Kscale=%.6g",
                Kv_old, spec.design.Kv, Kscale
            )

        # Frequency grid
        w = np.logspace(
            np.log10(spec.grid.wmin), np.log10(spec.grid.wmax), spec.grid.wnum
        )

        # Manual vs auto design
        stages: List[LagStage] = []
        wc = float("nan")
        Kc = 1.0 if (spec.design.Kc is None) else float(spec.design.Kc)

        if (spec.design.beta is not None) and (spec.design.T is not None):
            beta = max(1.0001, float(spec.design.beta))
            T = float(spec.design.T)
            stages = [LagStage(beta=beta, T=T, wz=1.0 / T, wp=1.0 / (beta * T))]
        else:
            if spec.design.pm_target is None:
                raise ValueError(
                    "Lag design requires either (lag_beta & lag_T) or lag_pm_target."
                )
            stages, Kc, wc = self._auto_design(
                G1,
                float(spec.design.pm_target),
                float(spec.design.pm_add),
                float(spec.design.w_ratio_z),
                w,
            )

        # Compose compensator Gc(s) = Kc * Π (T s + 1) / (β T s + 1)
        Gc = ct.tf([1], [1])
        for st in stages:
            Gc *= ct.tf([st.T, 1.0], [st.beta * st.T, 1.0])
        if not math.isnan(Kc):
            Gc *= Kc

        # Compensated open-loop
        G_ol_c = ct.minreal(Gc * G1, verbose=False)

        # Margins
        gm_u, pm_u, wgm_u, wpm_u = get_margins(G1)
        gm_c, pm_c, wgm_c, wpm_c = get_margins(G_ol_c)

        # Pack results
        # For convenience (and tests), mirror the first stage at top-level when present.
        beta_top = stages[0].beta if stages else float("nan")
        T_top = stages[0].T if stages else float("nan")
        wz_top = stages[0].wz if stages else float("nan")
        wp_top = stages[0].wp if stages else float("nan")

        pack = {
            "uncomp_margins": {
                "PM_deg": pm_u,
                "w_PM": wpm_u,
                "GM_abs": gm_u,
                "GM_dB": (db(gm_u) if np.isfinite(gm_u) else float("inf")),
                "w_GM": wgm_u,
            },
            "comp_margins": {
                "PM_deg": pm_c,
                "w_PM": wpm_c,
                "GM_abs": gm_c,
                "GM_dB": (db(gm_c) if np.isfinite(gm_c) else float("inf")),
                "w_GM": wgm_c,
            },
            "lag": {
                # top-level single-stage mirror (equals first stage if present)
                "beta": float(beta_top),
                "T": float(T_top),
                "wz": float(wz_top),
                "wp": float(wp_top),
                "Kc": float(Kc),
                "wc": float(wc),
                # full stage list (future-proof)
                "stages": [
                    {"beta": st.beta, "T": st.T, "wz": st.wz, "wp": st.wp} for st in stages
                ],
            },
        }

        files: List[str] = []
        # Reuse common rendering/export path (consistent with laglead/lead)
        try:
            from . import io as io_mod  # type: ignore
            plot = spec.plot
            if plot.export_json:
                import json, os

                path = plot.export_json
                os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(pack, f, indent=2, default=lambda o: [o.real, o.imag])
                files.append(path)

            if plot.export_csv_prefix:
                files.extend(io_mod.export_csvs(plot.export_csv_prefix, G1, G_ol_c, w))

            files += io_mod.render_plots(
                backend=plot.backend,
                wants=[s.strip().lower() for s in plot.plots.split(",") if s.strip()],
                G1=G1,
                G_ol_c=G_ol_c,
                w=w,
                ogata_axes=bool(plot.ogata_axes),
                nichols_templates=bool(plot.nichols_templates),
                nichols_Mdb=plot.nichols_Mdb,
                nichols_Ndeg=plot.nichols_Ndeg,
                nyquist_M=plot.nyquist_M,
                nyquist_marks=plot.nyquist_marks,
                save_tmpl=plot.save,
                save_img_tmpl=plot.save_img,
                no_show=plot.no_show,
                show_unstable=plot.show_unstable,
            )
        except Exception:
            # Keep the designer robust in no-plot/no-io contexts (unit tests)
            pass

        return LagDesignResult(pack=pack, files=files)

    # ------------------------- Auto design (phase method) ---------------------
    def _auto_design(
        self,
        G1: ct.lti,
        pm_target: float,
        pm_add: float,
        w_ratio_z: float,
        w: np.ndarray,
    ) -> Tuple[List[LagStage], float, float]:
        """
        Compute a single-stage lag from target PM using Ogata's approach.
        Returns (stages, Kc, wc).
        """
        _gm, _pm, _wgm, _wpm = get_margins(G1)
        target_phase = -180.0 + pm_target + pm_add

        mag, ph, ww = frequency_response_arrays(G1, w)
        ph_deg = np.rad2deg(ph)
        idx = int(np.argmin(np.abs(ph_deg - target_phase)))

        # Walk down in frequency until |G1(jω)| >= 1 so β > 1
        while idx > 0 and mag[idx] < 1.0:
            idx -= 1
        wc = float(ww[idx])

        M = float(mag[idx])  # |G1(jωc)|
        beta = max(1.0001, M)
        wz = wc / max(1.001, float(w_ratio_z))
        T = 1.0 / wz

        stages_out = [LagStage(beta=beta, T=T, wz=1.0 / T, wp=1.0 / (beta * T))]
        Kc = 1.0
        return stages_out, float(Kc), float(wc)
