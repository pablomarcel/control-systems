from __future__ import annotations
import numpy as np
import control as ct

# ---- canonical plant builders ----

def build_mass_spring_damper(m: float, b: float, k: float) -> ct.StateSpace:
    A = np.array([[0.0, 1.0], [-k/m, -b/m]])
    B = np.array([[0.0], [1.0/m]])
    C = np.array([[1.0, 0.0]])
    D = np.array([[0.0]])
    return ct.ss(A, B, C, D)

def build_kelvin_voigt(m: float, b: float, k: float) -> ct.StateSpace:
    A = np.array([[0.0, 1.0], [-k/m, -b/m]])
    B = np.array([[0.0], [1.0/m]])
    C = np.array([[1.0, 0.0],[k, b]])
    D = np.zeros((2,1))
    return ct.ss(A, B, C, D)

def build_maxwell(m: float, b: float, k: float) -> ct.StateSpace:
    A = np.array([[0.0, 1.0, 0.0],
                  [0.0, 0.0, -1.0/m],
                  [0.0, k,   -k/b]])
    B = np.array([[0.0],[1.0/m],[0.0]])
    C = np.array([[1.0, 0.0, 0.0],[0.0, 0.0, 1.0]])
    D = np.zeros((2,1))
    return ct.ss(A, B, C, D)

# ---- companion & Ogata beta mapping ----

def companion_state_space(a_list, b0=1.0):
    a = np.asarray(a_list, dtype=float).ravel()
    n = a.size
    if n<1: raise ValueError("need n>=1")
    A = np.zeros((n,n), dtype=float)
    for i in range(n-1): A[i,i+1] = 1.0
    A[-1,:] = -a[::-1]
    B = np.zeros((n,1), dtype=float); B[-1,0] = float(b0)
    C = np.zeros((1,n), dtype=float); C[0,0] = 1.0
    D = np.array([[0.0]])
    return A,B,C,D

def betas_from_ab(a: list[float], b: list[float]) -> list[float]:
    n = len(a)
    if len(b) != n+1:
        raise ValueError("b must have length n+1")
    beta = [0.0]*(n+1)
    beta[0] = b[0]
    for k in range(1, n):
        acc = b[k]
        for i in range(1, k+1):
            acc -= a[i-1]*beta[k-i]
        beta[k] = acc
    acc = b[n]
    for i in range(1, n+1):
        acc -= a[i-1]*beta[n-i]
    beta[n] = acc
    return beta

def build_ss_with_deriv(a: list[float], b: list[float]):
    a = np.asarray(a, dtype=float).ravel()
    n = a.size
    beta = betas_from_ab(list(a), list(b))
    A = np.zeros((n,n), dtype=float)
    for i in range(n-1): A[i,i+1] = 1.0
    A[-1,:] = -a[::-1]
    B = np.array(beta[1:], dtype=float).reshape(n,1)
    C = np.zeros((1,n), dtype=float); C[0,0]=1.0
    D = np.array([[beta[0]]], dtype=float)
    return A,B,C,D,beta
