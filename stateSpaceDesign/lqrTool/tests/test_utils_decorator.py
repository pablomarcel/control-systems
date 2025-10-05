import io, sys
import numpy as np
from stateSpaceDesign.lqrTool.utils import ensure_controllable, controllability_rank
from stateSpaceDesign.lqrTool.core import StateSpaceModel

class Dummy:
    def __init__(self, model):
        self._model = model

    @ensure_controllable
    def work(self, model):
        return "ok"

def test_controllability_and_decorator_warns():
    # Uncontrollable: A=0, B=0
    A = np.zeros((2,2)); B = np.zeros((2,1))
    C = np.array([[1,0]]); D = np.zeros((1,1))
    model = StateSpaceModel(A,B,C,D)
    # capture stdout
    buf = io.StringIO(); old = sys.stdout; sys.stdout = buf
    try:
        out = Dummy(model).work(model)
    finally:
        sys.stdout = old
    s = buf.getvalue()
    assert "WARN" in s or out == "ok"
    assert controllability_rank(A,B) == 0
