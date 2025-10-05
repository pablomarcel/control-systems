# gainMatrixTool — RUNS.md (inside-folder, correct paths)

**You are here:** `stateSpaceDesign/gainMatrixTool/`  
All commands below are meant to be run **from THIS folder**.  
They use the import shim in `cli.py`, and they write outputs into `out/` or `out_json/` here.

> If you prefer running from the **project root** instead, a mirror set of commands is at the end.

---

## Quick help
```bash
python cli.py --help
```

### Tips
- For pole values that start with `-`, the CLI now auto-normalizes consecutive negative tokens (e.g. `--poles -2 -5 -8` is accepted).  
  Still, the **equals form is bulletproof**: `--poles=-2 -5 -8`.
- Outputs:
  - Figures/JSON: `out/`
  - Batch JSON: `out_json/`
- Inputs (for batch mode): `in/`

---

## A) Single-case designs (run from inside this folder)

### A1. Auto (Ogata 10-1)
```bash
python cli.py run   --mode K   --A "0 1 0; 0 0 1; -1 -5 -6"   --B "0; 0; 1"   --poles "-2+4j" "-2-4j" "-10"   --method auto --pretty --verify   --log "out/gain_auto.log"
```

### A2. Ackermann
```bash
python cli.py run   --mode K   --A "0 1 0; 0 0 1; -1 -5 -6"   --B "0; 0; 1"   --poles "-2+4j" "-2-4j" "-10"   --method acker --pretty --verify
```

### A3. place()
```bash
python cli.py run   --mode K   --A "0 1 0; 0 0 1; -1 -5 -6"   --B "0; 0; 1"   --poles "-2+4j" "-2-4j" "-10"   --method place --pretty --verify
```

### A4. 2×2 sanity
```bash
python cli.py run   --mode K   --A "0 1; -2 -3"   --B "0; 1"   --poles -2 -5   --pretty --verify
```

### A5. JSON export (single case)
```bash
python cli.py run   --mode K   --A "0 1 0; 0 0 1; -1 -5 -6"   --B "0; 0; 1"   --poles "-2+4j" "-2-4j" "-10"   --method auto --verify   --export_json "out/ex10_1_gain.json"
```

### A6. Observer gain L (single output, Ackermann)
```bash
python cli.py run   --mode L   --A "0 1 0; 0 0 1; -1 -5 -6"   --C "1 0 0"   --poles -20 -21 -22   --method acker --pretty --verify
```

### A7. Observer gain L (multi-output, place)
```bash
python cli.py run   --mode L   --A "0 1 0; 0 0 1; -1 -5 -6"   --C "1 0 0; 0 1 0"   --poles -15 -16 -17   --method place --pretty --verify
```

### A8. Servo (kI) via augmentation (type-1)
```bash
python cli.py run   --mode KI   --A "0 1; -2 -3"   --B "0; 1"   --C "1 0"   --poles -2 -5 -8   --method acker --pretty --verify
```

---

## B) Batch mode (CSV / YAML)

> Defaults when running **inside this folder**:  
> - Inputs in `in/`  
> - Outputs in `out_json/`

### B1. CSV
```bash
python cli.py batch   --csv "in/cases.csv"   --verify --pretty   --export_dir "out"
```

### B2. YAML
```bash
python cli.py batch   --yaml "in/cases.yaml"   --verify --pretty   --export_dir "out"
```

---

## C) Python API (from a Python REPL in project venv)
```python
from stateSpaceDesign.gainMatrixTool.apis import GainMatrixAPI

api = GainMatrixAPI.default()
payload = api.single(
    mode="K",
    A="0 1; -2 -3",
    B="0; 1",
    C=None,
    poles=["-2","-5"],
    method="acker",
    verify=True,
    pretty=False,
)
print(payload["K"])
```

---

## D) Alternative: project-root commands (mirror set)

If you run from the **project root** (`modernControl/`), use:
```bash
python -m stateSpaceDesign.gainMatrixTool.cli --help
```

And mirror the examples like so:
```bash
python -m stateSpaceDesign.gainMatrixTool.cli run   --mode K   --A "0 1 0; 0 0 1; -1 -5 -6"   --B "0; 0; 1"   --poles "-2+4j" "-2-4j" "-10"   --method auto --pretty --verify   --log stateSpaceDesign/gainMatrixTool/out/gain_auto.log
```

Batch from root:
```bash
python -m stateSpaceDesign.gainMatrixTool.cli batch   --csv stateSpaceDesign/gainMatrixTool/in/cases.csv   --verify --pretty   --export_dir stateSpaceDesign/gainMatrixTool/out_json
```

---

## Requirements & Notes
- Python packages: `numpy`, `control>=0.10.2`, `pyyaml` (for YAML), `tqdm` (for batch progress).
- Outputs go where you point `--export_json` or `--export_dir`. Inside-folder runs should prefer `out/` and `out_json/`.
