from __future__ import annotations
from dataclasses import dataclass
import logging
import numpy as np
import control as ct

from .apis import RunRequest
from .utils import setup_logger, parse_vector, parse_matrix
from .core import SystemConverter, PrettyPrinter, Plotter
from .io import default_out

@dataclass
class AppResult:
    ok: bool
    message: str = ""

class ConverterApp:
    def __init__(self):
        self.conv = SystemConverter()
        self.pp = PrettyPrinter()
        self.plotter = Plotter()

    def detect_mode(self, req: RunRequest) -> str:
        has_tf = (req.num is not None and req.den is not None)
        has_ss = (req.A is not None and req.B is not None and req.C is not None)
        if has_tf and not has_ss:
            return "tf"
        if has_ss and not has_tf:
            return "ss"
        if has_tf and has_ss:
            return "both"
        return "none"

    def run(self, req: RunRequest) -> AppResult:
        setup_logger(req.log)
        mode = self.detect_mode(req)
        if mode == "none":
            return AppResult(False, "Provide either TF (--num/--den) or SS (--A/--B/--C [--D]).")

        tf_from_user = None
        ss_from_tf = None
        ss_from_user = None
        tf_from_ss = None

        try:
            # TF block
            if mode in ("tf", "both"):
                num = parse_vector(req.num)
                den = parse_vector(req.den)
                res_tf = self.conv.tf_to_ss(num, den)
                tf_from_user, ss_from_tf = res_tf.G, res_tf.SS

                print("\n=== TF → SS ===")
                print(self.pp.tf(tf_from_user))
                print("\nA =\n", ss_from_tf.A)
                print("B =\n", ss_from_tf.B)
                print("C =\n", ss_from_tf.C)
                print("D =\n", ss_from_tf.D)

                if req.sympy and getattr(tf_from_user, "ninputs", 1) == 1 and getattr(tf_from_user, "noutputs", 1) == 1:
                    print("\nSymPy rational form:")
                    print(self.pp.sympy_tf(tf_from_user))

                if not req.no_plot:
                    save_path = None
                    if req.out_prefix:
                        save_path = default_out(f"{req.out_prefix}_tf_step.png")
                    self.plotter.step_tf(tf_from_user, tfinal=req.tfinal, dt=req.dt, save=save_path, show=False)

            # SS block
            if mode in ("ss", "both"):
                A = parse_matrix(req.A)
                B = parse_matrix(req.B)
                C = parse_matrix(req.C)
                if req.D is None:
                    D = np.zeros((C.shape[0], B.shape[1]))
                else:
                    D = parse_matrix(req.D)

                res_ss = self.conv.ss_to_tf(A, B, C, D)
                ss_from_user, tf_from_ss = res_ss.SS, res_ss.G

                print("\n=== SS → TF ===")
                print("A =\n", A)
                print("B =\n", B)
                print("C =\n", C)
                print("D =\n", D)
                print(self.pp.tf(tf_from_ss))

                if req.sympy and getattr(tf_from_ss, "ninputs", 1) == 1 and getattr(tf_from_ss, "noutputs", 1) == 1:
                    print("\nSymPy rational form:")
                    print(self.pp.sympy_tf(tf_from_ss))

                if not req.no_plot:
                    save_path = None
                    if req.out_prefix:
                        save_path = default_out(f"{req.out_prefix}_ss_step.png")
                    self.plotter.step_ss(ss_from_user, iu=req.iu, tfinal=req.tfinal, dt=req.dt, save=save_path, show=False)

            # Equivalence check when both given (SISO)
            if mode == "both":
                try:
                    tf1 = ct.ss2tf(ss_from_tf)
                    tf2 = tf_from_ss
                    if (getattr(tf1, "ninputs", 1) == 1 and getattr(tf1, "noutputs", 1) == 1 and
                        getattr(tf2, "ninputs", 1) == 1 and getattr(tf2, "noutputs", 1) == 1):
                        ok = self.conv.equivalent_siso(tf1, tf2)
                        print("   Equal? ->", ok)
                except Exception as e:
                    logging.info("Equivalence check skipped: %s", e)

            return AppResult(True, "done")

        except Exception as e:
            logging.error("%s", e)
            return AppResult(False, str(e))
