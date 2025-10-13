
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import logging
import numpy as np
import control as ct
from .apis import ConverterConfig, ConverterResult
from .core import TFModel, SSModel, ConverterEngine
from .design import pretty_tf_any, ConverterPretty, plot_step_tf, plot_step_ss
from .io import parse_vector, parse_matrix, ensure_out_path, write_json
from .utils import setup_logger


@dataclass(slots=True)
class ConverterApp:
    level: int | str = logging.INFO
    from .core import ConverterEngine
    from dataclasses import field
    eng: ConverterEngine = field(init=False, repr=False)

    def __post_init__(self):
        setup_logger(self.level)
        self.eng = ConverterEngine()
        setup_logger(self.level)
        self.eng = ConverterEngine()

    def _detect_mode(self, cfg: ConverterConfig) -> str:
        has_tf = (cfg.num is not None and cfg.den is not None)
        has_ss = (cfg.A is not None and cfg.B is not None and cfg.C is not None)
        if has_tf and not has_ss: return "tf"
        if has_ss and not has_tf: return "ss"
        if has_tf and has_ss: return "both"
        return "none"

    def _parse_tf(self, cfg: ConverterConfig) -> TFModel:
        num = parse_vector(cfg.num); den = parse_vector(cfg.den)
        if num is None or den is None:
            raise ValueError("Both --num and --den are required for TF mode.")
        return TFModel(num, den)

    def _parse_ss(self, cfg: ConverterConfig) -> SSModel:
        A = parse_matrix(cfg.A); B = parse_matrix(cfg.B); C = parse_matrix(cfg.C)
        if A is None or B is None or C is None:
            raise ValueError("A, B, and C are required for SS mode.")
        if cfg.D is None:
            D = np.zeros((C.shape[0], B.shape[1]))
            logging.debug("D not provided; using zeros with shape %s", D.shape)
        else:
            D = parse_matrix(cfg.D)
        return SSModel(A,B,C,D)

    def run(self, cfg: ConverterConfig) -> ConverterResult:
        mode = self._detect_mode(cfg)
        if mode == "none":
            raise SystemExit("Provide either TF (--num/--den) or SS (--A/--B/--C [--D]).")

        tf_from_user = ss_from_tf = ss_from_user = tf_from_ss = None

        if mode in ("tf", "both"):
            tf_from_user = self._parse_tf(cfg).to_ct()
            ss_from_tf = self.eng.tf_to_ss(TFModel(*self.eng.normalize(*self.eng.coeffs_from_tf(tf_from_user)))).to_ct()

        if mode in ("ss", "both"):
            ss_model = self._parse_ss(cfg)
            ss_from_user = ss_model.to_ct()
            tf_from_ss = self.eng.ss_to_tf(ss_model)

        # Assemble result preference: if both, prefer SS pretty from TF and TF pretty from SS
        result_tf = tf_from_ss if tf_from_ss is not None else tf_from_user
        result_ss = ss_from_tf if ss_from_tf is not None else ss_from_user

        pretty = pretty_tf_any(result_tf) if result_tf is not None else None
        pretty_sym = ConverterPretty.sympy_rat(result_tf) if (result_tf is not None and cfg.sympy and getattr(result_tf, 'ninputs', 1)==1 and getattr(result_tf, 'noutputs', 1)==1) else None

        res = ConverterResult(mode=mode, tf=result_tf, ss=result_ss, pretty_tf=pretty, pretty_sympy=pretty_sym)

        # Optional plotting (interactive)
        if not cfg.no_plot and result_tf is not None and mode in ("tf","both"):
            plot_step_tf(result_tf, tfinal=cfg.tfinal, dt=cfg.dt, title="Step response (from TF)")
        if not cfg.no_plot and result_ss is not None and mode in ("ss","both"):
            plot_step_ss(result_ss, iu=cfg.iu, tfinal=cfg.tfinal, dt=cfg.dt, title="Step response (from SS)")

        # Optional JSON export
        if cfg.save_json:
            outp = ensure_out_path(None, cfg.save_json if cfg.save_json.endswith(".json") else cfg.save_json, suffix="" if cfg.save_json.endswith(".json") else ".json")
            write_json({
                "mode": res.mode,
                "pretty_tf": res.pretty_tf,
                "pretty_sympy": res.pretty_sympy,
            }, outp)

        return res
