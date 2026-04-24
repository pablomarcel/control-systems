# io.py
from __future__ import annotations

import json
import logging
import os
from typing import List, Optional, Sequence

import numpy as np
import control as ct

from .utils import db
from .core import frequency_response_arrays
from . import plots as plots_mod


def write_json(path: str, obj) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=lambda o: [o.real, o.imag])
    logging.info("Exported JSON -> %s", path)
    return path


def export_csvs(prefix: str, G_u: ct.lti, G_c: ct.lti, w: np.ndarray) -> list[str]:
    mu, pu, _ = frequency_response_arrays(G_u, w)
    mc, pc, _ = frequency_response_arrays(G_c, w)
    os.makedirs(os.path.dirname(prefix) or ".", exist_ok=True)
    bode = f"{prefix}_bode.csv"
    nich = f"{prefix}_nichols.csv"
    with open(bode, "w", encoding="utf-8") as f:
        f.write(
            "omega,mag_db_uncomp,phase_deg_uncomp,mag_db_comp,phase_deg_comp\n"
        )
        for wi, mu_i, pu_i, mc_i, pc_i in zip(
            w, db(mu), np.rad2deg(pu), db(mc), np.rad2deg(pc)
        ):
            f.write(f"{wi},{mu_i},{pu_i},{mc_i},{pc_i}\n")
    with open(nich, "w", encoding="utf-8") as f:
        f.write("phase_deg_uncomp,mag_db_uncomp,phase_deg_comp,mag_db_comp\n")

        def _wrap(ph):
            deg = np.rad2deg(ph)
            deg = (deg + 360.0) % 360.0
            return deg - 360.0

        for pu_i, mu_i, pc_i, mc_i in zip(_wrap(pu), db(mu), _wrap(pc), db(mc)):
            f.write(f"{pu_i},{mu_i},{pc_i},{mc_i}\n")
    logging.info("Exported CSVs -> %s, %s", bode, nich)
    return [bode, nich]


def render_plots(
    *,
    backend: str,
    wants: Sequence[str],
    G1: ct.lti,
    G_ol_c: ct.lti,
    w,
    ogata_axes: bool,
    nichols_templates: bool,
    nichols_Mdb,
    nichols_Ndeg,
    nyquist_M,
    nyquist_marks,
    save_tmpl: Optional[str],
    save_img_tmpl: Optional[str],
    no_show: bool,
    show_unstable: bool = False,  # NEW
) -> list[str]:
    files: list[str] = []
    backend = backend.lower()
    wants_set = set(wants)

    if backend == "mpl":
        # Import locally so the environment can decide the interactive backend
        import matplotlib.pyplot as plt

        figs = []
        if "bode" in wants_set:
            gm, pm, wgm, wpm = plots_mod.get_margins_safe(G_ol_c)
            figs.append(
                (
                    "bode",
                    plots_mod.plot_bode_mpl(
                        [("G1", G1), ("Gc*G1", G_ol_c)], w, "Bode", wgm=wgm, wpm=wpm
                    ),
                )
            )
        if "nyquist" in wants_set:
            figs.append(
                (
                    "nyquist",
                    plots_mod.plot_nyquist_mpl(
                        [("G1", G1), ("Gc*G1", G_ol_c)],
                        w,
                        "Nyquist",
                        ogata_axes=ogata_axes,
                        Mlist=nyquist_M,
                        freq_marks=nyquist_marks,
                    ),
                )
            )
        if "nichols" in wants_set:
            templates = (
                plots_mod.build_nichols_templates(nichols_Mdb, nichols_Ndeg)
                if nichols_templates
                else None
            )
            figs.append(
                (
                    "nichols",
                    plots_mod.plot_nichols_mpl(
                        [("G1", G1), ("Gc*G1", G_ol_c)], w, "Nichols", templates
                    ),
                )
            )
        if "step" in wants_set:
            figs.append(
                (
                    "step",
                    plots_mod.plot_step_mpl(
                        G1, G_ol_c, w, ogata_axes, show_unstable=show_unstable
                    ),
                )
            )
        if "ramp" in wants_set:
            figs.append(
                (
                    "ramp",
                    plots_mod.plot_ramp_mpl(
                        G1, G_ol_c, w, ogata_axes, show_unstable=show_unstable
                    ),
                )
            )

        # Save if requested
        if save_tmpl:
            for kind, fig in figs:
                path = save_tmpl.format(kind=kind)
                os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                fig.savefig(path, dpi=160, bbox_inches="tight")
                files.append(path)

        # Show interactive windows unless suppressed
        if not no_show:
            plt.show()

        # Always close to free memory after show/save decisions
        for _, fig in figs:
            plt.close(fig)

    else:
        # Plotly branch
        htmls = []
        if "bode" in wants_set:
            gm, pm, wgm, wpm = plots_mod.get_margins_safe(G_ol_c)
            htmls.append(
                (
                    "bode",
                    plots_mod.bode_plotly(
                        [("G1", G1), ("Gc*G1", G_ol_c)], w, "Bode", wgm=wgm, wpm=wpm
                    ),
                )
            )
        if "nyquist" in wants_set:
            htmls.append(
                (
                    "nyquist",
                    plots_mod.nyquist_plotly(
                        [("G1", G1), ("Gc*G1", G_ol_c)],
                        w,
                        "Nyquist",
                        ogata_axes=ogata_axes,
                        Mlist=nyquist_M,
                        freq_marks=nyquist_marks,
                    ),
                )
            )
        if "nichols" in wants_set:
            templates = (
                plots_mod.build_nichols_templates(nichols_Mdb, nichols_Ndeg)
                if nichols_templates
                else None
            )
            htmls.append(
                (
                    "nichols",
                    plots_mod.nichols_plotly(
                        [("G1", G1), ("Gc*G1", G_ol_c)], w, "Nichols", templates
                    ),
                )
            )
        # (optional step/ramp omitted for plotly)

        if save_tmpl:
            for kind, fig in htmls:
                path = save_tmpl.format(kind=kind)
                os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                fig.write_html(
                    path,
                    include_plotlyjs="cdn",
                    full_html=True,
                    default_width="100%",
                    config={"responsive": True},
                )
                files.append(path)
            if save_img_tmpl:
                for kind, fig in htmls:
                    p = save_img_tmpl.format(kind=kind)
                    try:
                        fig.write_image(p, scale=2)
                        files.append(p)
                    except Exception:
                        # Image export requires kaleido; ignore if unavailable
                        pass

    return files
