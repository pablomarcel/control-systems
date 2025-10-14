from __future__ import annotations
import logging, numpy as np, control as ct, matplotlib
matplotlib.use("Agg")  # ensure test-friendly
import matplotlib.pyplot as plt

from .apis import RunConfig, RunResult
from .utils import setup_logger, forced_response_safe, normalize_rows
from .core import (build_mass_spring_damper, build_kelvin_voigt, build_maxwell,
                   companion_state_space, build_ss_with_deriv)
from .io import parse_matrix, parse_list
from .design import symbolic_G, monic_fraction, charpoly_monic
import sympy as sp
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "out"

class SystemModelingApp:
    def __init__(self, level=logging.INFO):
        self.log = setup_logger(level)

    # ---- runners ----

    def run(self, cfg: RunConfig) -> RunResult:
        mode = cfg.mode
        try:
            if mode == "msd-step":
                return self._run_msd_step(cfg)
            if mode == "tf-from-ss":
                return self._run_tf_from_ss(cfg)
            if mode == "mimo-demo":
                return self._run_mimo_demo(cfg)
            if mode == "ode-no-deriv":
                return self._run_ode_no_deriv(cfg)
            if mode == "ode-with-deriv":
                return self._run_ode_with_deriv(cfg)
            if mode == "kv-vs-maxwell":
                return self._run_kv_vs_maxwell(cfg)
            return RunResult(ok=False, message=f"Unknown mode: {mode}")
        except Exception as e:
            return RunResult(ok=False, message=str(e))

    # ---- individual modes ----

    def _run_msd_step(self, cfg: RunConfig) -> RunResult:
        c = cfg.msd
        sys = build_mass_spring_damper(c.m, c.b, c.k)
        T = np.arange(0.0, c.tfinal + c.dt, c.dt)
        U = np.full_like(T, c.u0)
        X0 = np.array([c.y0, c.ydot0], dtype=float)
        t, y, x = forced_response_safe(sys, T, U, X0=X0)
        saved = []
        if c.save:
            OUT_DIR.mkdir(exist_ok=True, parents=True)
            fig1 = OUT_DIR/"msd_y.png"
            plt.figure(); plt.plot(t, y[0]); plt.grid(True); plt.title("MSD step y(t)"); plt.xlabel("t [s]"); plt.ylabel("y")
            plt.tight_layout(); plt.savefig(fig1, dpi=160); saved.append(str(fig1))
            if x is not None:
                fig2 = OUT_DIR/"msd_states.png"
                plt.figure(); plt.plot(t, x[0], label="y"); plt.plot(t, x[1], label="ydot"); plt.legend(); plt.grid(True); plt.title("MSD states"); plt.xlabel("t [s]")
                plt.tight_layout(); plt.savefig(fig2, dpi=160); saved.append(str(fig2))
        try:
            G = ct.ss2tf(sys)
            pretty = str(G)
        except Exception:
            pretty = None
        hints = [f"wn≈{(c.k/c.m)**0.5:.4g} rad/s", f"zeta≈{c.b/(2*(c.m*c.k)**0.5):.4g}"]
        return RunResult(ok=True, message="msd-step done", pretty_tf=pretty, saved_images=saved, hints=hints)

    def _run_tf_from_ss(self, cfg: RunConfig) -> RunResult:
        t = cfg.tfss
        if t.A and t.B and t.C and t.D:
            A = parse_matrix(t.A); B = parse_matrix(t.B); C = parse_matrix(t.C); D = parse_matrix(t.D)
        else:
            A = np.array([[0.0, 1.0], [-t.k/t.m, -t.b/t.m]])
            B = np.array([[0.0],[1.0/t.m]])
            C = np.array([[1.0,0.0]]); D = np.array([[0.0]])
        try:
            sys = ct.ss(A,B,C,D); Gpc = ct.ss2tf(sys)
            pretty = "\n".join([f"G[{i+1},{j+1}](s) = {Gpc[i,j]}" for i in range(Gpc.shape[0]) for j in range(Gpc.shape[1])])
        except Exception as e:
            pretty = f"[warn] ss2tf failed: {e}"
        # symbolic clean (monic)
        try:
            Gsym, s = symbolic_G(A,B,C,D)
            m,r = Gsym.shape
            lines = []
            for i in range(m):
                for j in range(r):
                    num, den = monic_fraction(Gsym[i,j], s)
                    lines.append(f"G[{i+1},{j+1}] = {sp.sstr(num)}/{sp.sstr(den)}")
            pretty += "\n" + "\n".join(lines)
        except Exception as e:
            pretty += f"\n[warn] symbolic failed: {e}"
        return RunResult(ok=True, message="tf-from-ss done", pretty_tf=pretty, saved_images=[], hints=[])

    def _run_mimo_demo(self, cfg: RunConfig) -> RunResult:
        A = np.array([[-1.0, -1.0],[6.5, 0.0]])
        B = np.array([[1.0, 1.0],[1.0, 0.0]])
        C = np.eye(2); D = np.zeros((2,2))
        sys = ct.ss(A,B,C,D)
        T = np.arange(0.0, 10.0 + 0.001, 0.001)
        saved = []
        for which in (0,1):
            U = np.zeros((B.shape[1], T.size)); U[which,:]=1.0
            t,y,_ = forced_response_safe(sys, T, U)
            OUT_DIR.mkdir(exist_ok=True, parents=True)
            f = OUT_DIR/f"mimo_step_u{which+1}.png"
            import matplotlib.pyplot as plt
            plt.figure(); plt.plot(t, y[0], label="y1"); plt.plot(t, y[1], label="y2"); plt.legend(); plt.grid(True); plt.title(f"u{which+1}=step")
            plt.tight_layout(); plt.savefig(f, dpi=160); saved.append(str(f))
        # pretty transfer
        try:
            Gpc = ct.ss2tf(sys)
            pretty = "\n".join([f"G[{i+1},{j+1}](s) = {Gpc[i,j]}" for i in range(Gpc.shape[0]) for j in range(Gpc.shape[1])])
        except Exception as e:
            pretty = f"[warn] ss2tf failed: {e}"
        return RunResult(ok=True, message="mimo-demo done", pretty_tf=pretty, saved_images=saved, hints=[])

    def _run_ode_no_deriv(self, cfg: RunConfig) -> RunResult:
        c = cfg.ode_nd
        if c.msd:
            a_list = [c.b/c.m, c.k/c.m]; b0 = 1.0/c.m
        else:
            if c.a: a_list = parse_list(c.a); b0 = c.b0
            else: a_list = [1.0, 10.0]; b0 = 1.0
        A,B,C,D = companion_state_space(a_list, b0)
        sys = ct.ss(A,B,C,D)
        T = np.arange(0.0, c.tfinal + c.dt, c.dt)
        U = np.full_like(T, c.u0)
        X0 = np.zeros((len(a_list),), dtype=float)
        if len(a_list)>=1: X0[0] = c.y0
        if len(a_list)>=2: X0[1] = c.ydot0
        t,y,_ = forced_response_safe(sys, T, U, X0=X0)
        saved=[]
        if c.save:
            OUT_DIR.mkdir(exist_ok=True, parents=True)
            f = OUT_DIR/"ode_no_deriv_step.png"
            import matplotlib.pyplot as plt
            plt.figure(); plt.plot(t, y[0]); plt.grid(True); plt.title("ODE no u-derivatives: step")
            plt.tight_layout(); plt.savefig(f, dpi=160); saved.append(str(f))
        # symbolic TF & char poly
        pretty = ""
        try:
            from .design import symbolic_G, monic_fraction
            Gsym, s = symbolic_G(A,B,C,D)
            num, den = monic_fraction(Gsym[0,0], s)
            pretty += f"G(s)={sp.sstr(num)}/{sp.sstr(den)}"
        except Exception as e:
            pretty += f"[warn] symbolic failed: {e}"
        try:
            pretty += "\ncharpoly=" + str(charpoly_monic(A))
        except Exception:
            pass
        return RunResult(ok=True, message="ode-no-deriv done", pretty_tf=pretty, saved_images=saved, hints=[])

    def _run_ode_with_deriv(self, cfg: RunConfig) -> RunResult:
        c = cfg.ode_d
        a = parse_list(c.a) if c.a else [1.0, 10.0]
        b = parse_list(c.b) if c.b else [0.5, 1.0, 0.0]
        A,B,C,D,beta = build_ss_with_deriv(a,b)
        sys = ct.ss(A,B,C,D)
        T = np.arange(0.0, c.tfinal + c.dt, c.dt)
        U = np.full_like(T, c.u0)
        t,y,_ = forced_response_safe(sys, T, U)
        saved=[]
        if c.save:
            OUT_DIR.mkdir(exist_ok=True, parents=True)
            f = OUT_DIR/"ode_with_deriv_step.png"
            import matplotlib.pyplot as plt
            plt.figure(); plt.plot(t, y[0]); plt.grid(True); plt.title("ODE with u-derivatives: step")
            plt.tight_layout(); plt.savefig(f, dpi=160); saved.append(str(f))
        pretty = f"beta={beta}"
        return RunResult(ok=True, message="ode-with-deriv done", pretty_tf=pretty, saved_images=saved, hints=[])

    def _run_kv_vs_maxwell(self, cfg: RunConfig) -> RunResult:
        c = cfg.kvmax
        m=b=k=1.0
        sys_kv = build_kelvin_voigt(m,b,k); sys_mw = build_maxwell(m,b,k)
        T = np.arange(0.0, c.tfinal + c.dt, c.dt)
        U = np.full_like(T, c.u0)
        tk, yk, _ = forced_response_safe(sys_kv, T, U)
        tm, ym, _ = forced_response_safe(sys_mw, T, U)
        OUT_DIR.mkdir(exist_ok=True, parents=True)
        import matplotlib.pyplot as plt
        saved=[]
        if c.save:
            f1 = OUT_DIR/"kv_vs_maxwell_y.png"
            plt.figure(); plt.plot(tk, yk[0], label="KV y"); plt.plot(tm, ym[0], label="Maxwell y", linestyle="--")
            plt.legend(); plt.grid(True); plt.title("KV vs Maxwell: y(t)"); plt.tight_layout(); plt.savefig(f1, dpi=160); saved.append(str(f1))
        return RunResult(ok=True, message="kv-vs-maxwell done", saved_images=saved, hints=[], pretty_tf=None)
