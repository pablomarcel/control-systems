
import numpy as np
import pytest
from state_space_design.minOrdTfTool.utils import poly_from_roots
from state_space_design.minOrdTfTool.design import MinOrderObserverDesigner

def test_poly_from_roots_requires_conjugate_pairs():
    # Single complex root => should raise
    with pytest.raises(ValueError):
        poly_from_roots(np.array([-2+1j]))

def test_must_be_single_input():
    A = np.array([[0,1],[-2,-3]], float)
    B = np.array([[0,0],[1,0]], float)  # m=2
    C = np.array([[1,0]], float)
    with pytest.raises(ValueError):
        MinOrderObserverDesigner(A,B,C)
