# -*- coding: utf-8 -*-
import numpy as np
from stateSpaceDesign.controllerTool.design import (
    place_controller_acker, reduced_order_observer_gain, choose_N_for_feedback
)
import control as ct

def test_place_controller_and_observer_gain_shapes():
    # Companion A for 1/(s(s^2+1))
    den = np.array([1.0, 0.0, 1.0, 0.0])
    # Build A,B like in core (short re-creation for test)
    a = den[1:]
    A = np.zeros((3,3)); A[0,1]=1; A[1,2]=1; A[2,:] = -a[::-1]
    B = np.array([[0.0],[0.0],[1.0]])
    Kres = place_controller_acker(A,B,np.array([-1+1j,-1-1j,-8],complex))
    assert Kres.K.shape == (1,3)
    # Observer (r=n-1=2)
    Aab = A[0:1,1:]; Abb = A[1:,1:]
    Ores = reduced_order_observer_gain(Abb, Aab, np.array([-4,-4],complex))
    assert Ores.Ke.shape == (2,1)

def test_choose_N_non_integrator_case():
    # Non-integrator plant: (s+1)/(s^2+3s+2)
    G = ct.tf([1.0,1.0],[1.0,3.0,2.0])
    Gc = ct.tf([2.0,1.0],[1.0,2.0])  # (2s+1)/(s+2)
    N = choose_N_for_feedback(G,Gc)
    # Finite, non-zero
    assert abs(N) > 1e-12 and abs(N) < 1e6
