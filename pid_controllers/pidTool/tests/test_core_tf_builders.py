import types
import numpy as np
import sympy as sp
import control as ct
from pid_controllers.pidTool.core import tf_from_args, controller_tf, poly_from_string

class A: pass

def _args(**kw):
    o = A()
    for k,v in kw.items(): setattr(o,k,v)
    return o

def _flatten_coeffs(tf):
    # Works across python-control versions: pull first SISO path
    num = tf.num[0][0] if isinstance(tf.num[0], list) else tf.num[0]
    den = tf.den[0][0] if isinstance(tf.den[0], list) else tf.den[0]
    return np.asarray(num, dtype=float), np.asarray(den, dtype=float)

def test_tf_from_args_coeff():
    args = _args(plant_form="coeff", num="1 0", den="1 1")
    G = tf_from_args(args)
    assert isinstance(G, ct.TransferFunction)

def test_tf_from_args_poly():
    args = _args(plant_form="poly",
                 num_poly="2*s + 1",
                 den_poly="s**2 + 3*s + 2")
    G = tf_from_args(args)
    assert isinstance(G, ct.TransferFunction)

def test_tf_from_args_zpk():
    args = _args(plant_form="zpk", zeros="", poles="-1 -2", gain=2.0)
    G = tf_from_args(args)
    assert isinstance(G, ct.TransferFunction)

def test_controller_tf_variants():
    s = ct.TransferFunction.s
    G_pid = controller_tf("pid", {"Kp":1,"Ki":2,"Kd":3})
    # Expect numerator [Kd, Kp, Ki] and denominator [1, 0] for (Kp + Ki/s + Kd*s)
    num, den = _flatten_coeffs(G_pid)
    assert np.allclose(num, [3,1,2]) and np.allclose(den, [1,0])

    G_pi = controller_tf("pi", {"Kp":1,"Ki":2})
    num, den = _flatten_coeffs(G_pi)
    assert np.allclose(num, [1,2]) and np.allclose(den, [1,0])

    G_pd = controller_tf("pd", {"Kp":1,"Kd":3})
    num, den = _flatten_coeffs(G_pd)
    assert np.allclose(num, [3,1]) and np.allclose(den, [1])

    C = controller_tf("pid_dz", {"K":2,"a":0.5})
    assert isinstance(C, ct.TransferFunction)

def test_poly_from_string_basic():
    s = sp.Symbol("s")
    coeffs = poly_from_string("0.36*s**3 + 1.86*s**2 + 2.5*s + 1", s)
    assert len(coeffs) == 4 and abs(coeffs[0]-0.36) < 1e-9
