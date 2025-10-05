import pathlib, tempfile, json
from stateSpaceDesign.gainMatrixTool.app import GainMatrixApp

def test_app_run_and_logging(tmp_path):
    app = GainMatrixApp.default()
    logp = tmp_path / "log.txt"
    app.configure_logging(str(logp), verbose=True)
    payload = app.run_single(
        mode="K",
        A="0 1; -2 -3",
        B="0; 1",
        C=None,
        poles=["-2","-5"],
        method="acker",
        verify=True,
        pretty=False
    )
    assert "K" in payload
    assert logp.exists()

def test_app_run_batch_csv(tmp_path):
    app = GainMatrixApp.default()
    csvp = tmp_path / "cases.csv"
    csvp.write_text('name,mode,A,B,C,poles,method\nex,K,"0 1; -2 -3","0; 1",,"-2 -5",acker\n', encoding="utf-8")
    outdir = tmp_path / "out"
    app.run_batch(str(csvp), None, str(outdir), verify=True, pretty=False)
    assert any(p.name.endswith("_K.json") for p in outdir.iterdir())
