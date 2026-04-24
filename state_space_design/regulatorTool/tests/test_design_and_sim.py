
import numpy as np
from state_space_design.regulatorTool.design import PlantFactory, RegulatorDesigner
from state_space_design.regulatorTool.core import RegulatorParams, SimulationSpec

def test_design_run_and_simulate_manual_poles():
    plant = PlantFactory.from_tf(np.array([10.0,20.0]), np.array([1.0,10.0,24.0,0.0]))
    params = RegulatorParams(
        K_poles=np.array([-1+2j, -1-2j, -5], complex),
        obs_poles=np.array([-4.5, -4.5], float)
    )
    des = RegulatorDesigner(plant, params)
    res = des.run()
    assert res.Gc is not None and res.T is not None
    sig = des.simulate_initial(res, SimulationSpec(
        x0=np.array([1.0,0.0,0.0]), e0=np.array([1.0,0.0]), t_final=0.5, dt=0.05))
    assert sig.X.shape[1] > 0 and sig.E.shape[1] > 0

def test_design_bode_and_rootlocus_auto():
    plant = PlantFactory.from_tf(np.array([10.0,20.0]), np.array([1.0,10.0,24.0,0.0]))
    params = RegulatorParams(ts=4.0, undershoot=(0.25,0.35), obs_speed_factor=5.0)
    des = RegulatorDesigner(plant, params)
    res = des.run()
    (mag_ol, ph_ol), (mag_cl, ph_cl), w_ol, w_cl = des.bode_open_closed(res)
    assert mag_ol.size == w_ol.size and mag_cl.size == w_cl.size
    r,k = des.root_locus(res, "1e-4, 1e4, 25")
    assert r.shape[1] == k.size
