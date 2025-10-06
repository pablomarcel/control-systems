import control as ct
import numpy as np
from stateSpaceDesign.robustTool.core import Plant, Controller, Weights, LoopBuilder, FrequencyTools

def test_plant_tf_and_controller_variants():
    G = Plant("1", "1 1").tf()
    assert isinstance(G, ct.TransferFunction)

    Kpid = Controller(pid="1,2,0.3,15").tf()
    assert isinstance(Kpid, ct.TransferFunction)

    Ktf = Controller(pid=None, K_num="1 6 2", K_den="1 6 0").tf()
    assert isinstance(Ktf, ct.TransferFunction)

    Kunity = Controller().tf()
    num, den = Kunity.num[0][0], Kunity.den[0][0]
    assert list(num) == [1] and list(den) == [1]

def test_weights_and_loops_and_bode():
    G = Plant("10 20", "1 10 24 0").tf()
    K = Controller(pid="1,0,0").tf()
    L,S,T = LoopBuilder.loops(G,K)
    assert L.ninputs == 1 and S.noutputs == 1 and T.noutputs == 1

    Wm, Ws, Wa = Weights(Wm_num="0.3 1", Wm_den="0.03 1", Ws_num="2 0", Ws_den="1 0.2 0", Wa_num="1", Wa_den="1").get()
    assert Wa is not None

    w = np.logspace(-2, 2, 16)
    mag, phs = FrequencyTools.bode_mag_phase(T, w)
    assert mag.shape == w.shape and phs.shape == w.shape

def test_freq_tools_sigma_and_hinf():
    G = Plant("1", "1 1").tf()
    gamma, wpk, w, sig = FrequencyTools.hinf_sweep(G, 1e-2, 1e1, npts=32)
    assert gamma >= 0 and (w[0] >= 1e-2) and (w[-1] <= 1e1)
