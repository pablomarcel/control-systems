
from __future__ import annotations
from pidControllers.tuningTool.apis import PrintAPI, ExportAPI
from pidControllers.tuningTool.core import TuningResult

def make_res():
    return TuningResult(
        method="M", controller="PID", inputs={"L":0.8,"T":3.0},
        Kp=4.5, Ti=1.6, Td=0.4, Ki=2.8125, Kd=1.8,
        controller_zeros_location=-1.25, controller_zeros_multiplicity=2
    )

def test_print_and_export_apis():
    res = make_res()
    text = PrintAPI().render_text(res, precision=4)
    # Ensure critical fields are present (don't assert brand prefix absence)
    assert "M • PID" in text
    assert "Gains:" in text and "Kp=4.5" in text and "Ti=1.6" in text and "Td=0.4" in text
    assert "Implied controller zeros" in text
    d = ExportAPI().to_json(res)
    assert d["Kp"] == 4.5 and "controller_zeros" in d and d["controller_zeros"]["multiplicity"] == 2
