import subprocess, sys, pathlib, json, os, shutil

def repo_root():
    return pathlib.Path(__file__).resolve().parents[3]

def test_cli_run_exports_json(tmp_path):
    root = repo_root()
    out_json = tmp_path / "k_run.json"
    cmd = [
        sys.executable, "-m", "state_space_design.gainMatrixTool.cli",
        "run",
        "--mode","K",
        "--A","0 1; -2 -3",
        "--B","0; 1",
        "--poles","-2","-5",
        "--verify",
        "--export_json", str(out_json)
    ]
    cp = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    assert cp.returncode == 0, cp.stderr
    data = json.loads(out_json.read_text())
    assert "K" in data and "poles_closed" in data

def test_cli_batch_csv_and_yaml(tmp_path):
    root = repo_root()
    csvp = tmp_path / "cases.csv"
    csvp.write_text('name,mode,A,B,C,poles,method\nexK,K,"0 1; -2 -3","0; 1",,"-2 -5",acker\nobs,L,"0 1; -2 -3",,"1 0","-10 -11",acker\n', encoding="utf-8")
    ymlp = tmp_path / "cases.yaml"
    ymlp.write_text("cases:\n  - {name: exK2, mode: K, A: '0 1; -2 -3', B: '0; 1', poles: '-2 -5', method: acker}\n", encoding="utf-8")
    outdir_csv = tmp_path / "out_csv"
    outdir_yaml = tmp_path / "out_yaml"
    outdir_csv.mkdir()
    outdir_yaml.mkdir()

    cmd_csv = [sys.executable, "-m", "state_space_design.gainMatrixTool.cli", "batch",
               "--csv", str(csvp), "--export_dir", str(outdir_csv), "--verify", "--pretty"]
    cp1 = subprocess.run(cmd_csv, cwd=root, capture_output=True, text=True)
    assert cp1.returncode == 0, cp1.stderr

    cmd_yaml = [sys.executable, "-m", "state_space_design.gainMatrixTool.cli", "batch",
                "--yaml", str(ymlp), "--export_dir", str(outdir_yaml)]
    cp2 = subprocess.run(cmd_yaml, cwd=root, capture_output=True, text=True)
    assert cp2.returncode == 0, cp2.stderr

    assert any(f.name.endswith("_K.json") for f in outdir_csv.iterdir())
    assert any(f.name.endswith("_K.json") for f in outdir_yaml.iterdir())

def test_cli_negatives_are_handled(tmp_path):
    root = repo_root()
    out_json = tmp_path / "neg.json"
    cmd = [
        sys.executable, "-m", "state_space_design.gainMatrixTool.cli",
        "run",
        "--mode","K",
        "--A","0 1; -2 -3",
        "--B","0; 1",
        "--poles","-2","-6",
        "--export_json", str(out_json)
    ]
    cp = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    assert cp.returncode == 0, cp.stderr
    assert out_json.exists()
