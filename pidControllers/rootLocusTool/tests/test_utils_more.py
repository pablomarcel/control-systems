from __future__ import annotations
from pidControllers.rootLocusTool.utils import ensure_out_path, parse_poly, complex_arg
import os, math

def test_parse_poly_variants():
    assert parse_poly("1, 2,3") == [1.0,2.0,3.0]
    assert parse_poly("1 2 3") == [1.0,2.0,3.0]
    assert parse_poly([4,5,6]) == [4.0,5.0,6.0]
    assert parse_poly(None) is None

def test_complex_arg_quadrants():
    assert math.isclose(complex_arg(1+0j), 0.0, abs_tol=1e-12)
    assert math.isclose(complex_arg(0+1j), math.pi/2, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(complex_arg(-1+0j), math.pi, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(complex_arg(0-1j), -math.pi/2, rel_tol=0, abs_tol=1e-12)

def test_ensure_out_path_relative(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = ensure_out_path("foo/bar.txt")
    assert p.endswith(os.path.join("out","foo","bar.txt"))
    assert os.path.isdir(os.path.join(tmp_path, "out","foo"))
