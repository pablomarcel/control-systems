from __future__ import annotations
import numpy as np
from root_locus_analysis.rootLocusTool.utils import parse_matrix, parse_list, safe_title_to_filename

def test_parse_matrix_basic():
    A = parse_matrix("0 1; -2 -3")
    assert A.shape == (2,2)
    assert np.isclose(A[1,0], -2)

def test_parse_list():
    assert parse_list("1, 2; 3") == [1.0, 2.0, 3.0]

def test_safe_title():
    assert safe_title_to_filename("Hello world!") == "Hello_world_"
