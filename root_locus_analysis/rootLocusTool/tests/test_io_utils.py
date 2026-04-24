
from __future__ import annotations
import logging, os
from pathlib import Path
import numpy as np
from root_locus_analysis.rootLocusTool.io import OutputSpec, ensure_outdir
from root_locus_analysis.rootLocusTool.utils import make_logger, parse_list, safe_title_to_filename, parse_matrix

def test_outputspec_resolve_absolute_and_relative(tmp_path: Path):
    outdir = tmp_path / "o"
    ensure_outdir(str(outdir))
    spec = OutputSpec(out_dir=str(outdir), html="file.html", png="p.png", csv="c.csv")
    html, png, csv = spec.resolve("ignored_title")
    assert html.endswith("file.html")
    assert png.endswith("p.png")
    assert csv.endswith("c.csv")

    # absolute paths should pass through unchanged
    apng = os.path.join(str(tmp_path), "abs.png")
    spec2 = OutputSpec(out_dir=str(outdir), html=os.path.join(str(tmp_path), "abs.html"), png=apng, csv=None)
    html2, png2, csv2 = spec2.resolve("t")
    assert html2 == os.path.join(str(tmp_path), "abs.html")
    assert png2 == apng
    assert csv2 is None

def test_make_logger_levels_and_single_handler():
    lg1 = make_logger(False)
    lg2 = make_logger(True)
    assert isinstance(lg1, logging.Logger)
    # ensure we didn't double-add handlers
    n1 = len(lg1.handlers)
    make_logger(False)
    assert len(lg1.handlers) == n1
    # check levels
    assert lg1.level in (logging.INFO, logging.DEBUG)
    assert lg2.level == logging.DEBUG

def test_parse_helpers_and_matrix():
    assert parse_list("1; 2, 3") == [1.0, 2.0, 3.0]
    assert safe_title_to_filename("Hello World!") == "Hello_World_"
    m = parse_matrix("0 1 0; 0 0 1; -1 -2 -3")
    assert m.shape == (3,3)
    # commas and bars
    m2 = parse_matrix("0,1,0|0,0,1|-1,-2,-3")
    assert np.allclose(m, m2)
