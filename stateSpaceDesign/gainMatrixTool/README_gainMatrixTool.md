# stateSpaceDesign.gainMatrixTool — Gain Matrix (K, L, kI)

Run from **repo root** (`modernControl/`). Default I/O:
- Inputs: `stateSpaceDesign/gainMatrixTool/in/`
- Outputs: `stateSpaceDesign/gainMatrixTool/out/`

## CLI
```
python -m stateSpaceDesign.gainMatrixTool.cli [run|batch] [OPTIONS]
```

### Single-case examples
```bash
# 1) Auto (Ogata 10-1)
python -m stateSpaceDesign.gainMatrixTool.cli run \
  --mode K \
  --A "0 1 0; 0 0 1; -1 -5 -6" \
  --B "0; 0; 1" \
  --poles "-2+4j" "-2-4j" "-10" \
  --method auto --pretty --verify --log stateSpaceDesign/gainMatrixTool/out/gain_auto.log

# 2) Ackermann
python -m stateSpaceDesign.gainMatrixTool.cli run \
  --mode K \
  --A "0 1 0; 0 0 1; -1 -5 -6" \
  --B "0; 0; 1" \
  --poles "-2+4j" "-2-4j" "-10" \
  --method acker --pretty --verify

# 3) place()
python -m stateSpaceDesign.gainMatrixTool.cli run \
  --mode K \
  --A "0 1 0; 0 0 1; -1 -5 -6" \
  --B "0; 0; 1" \
  --poles "-2+4j" "-2-4j" "-10" \
  --method place --pretty --verify

# 4) 2×2 sanity
python -m stateSpaceDesign.gainMatrixTool.cli run \
  --mode K \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --poles "-2" "-5" \
  --pretty --verify

# 5) JSON export
python -m stateSpaceDesign.gainMatrixTool.cli run \
  --mode K \
  --A "0 1 0; 0 0 1; -1 -5 -6" \
  --B "0; 0; 1" \
  --poles "-2+4j" "-2-4j" "-10" \
  --method auto --verify \
  --export_json stateSpaceDesign/gainMatrixTool/out/ex10_1_gain.json

# 6) Observer gain L (single output)
python -m stateSpaceDesign.gainMatrixTool.cli run \
  --mode L \
  --A "0 1 0; 0 0 1; -1 -5 -6" \
  --C "1 0 0" \
  --poles "-20" "-21" "-22" \
  --method acker --pretty --verify

# 7) Observer gain L (multi-output, place)
python -m stateSpaceDesign.gainMatrixTool.cli run \
  --mode L \
  --A "0 1 0; 0 0 1; -1 -5 -6" \
  --C "1 0 0; 0 1 0" \
  --poles "-15" "-16" "-17" \
  --method place --pretty --verify
```

### Batch
```bash
python -m stateSpaceDesign.gainMatrixTool.cli batch \
  --csv stateSpaceDesign/gainMatrixTool/in/cases.csv \
  --verify --pretty \
  --export_dir stateSpaceDesign/gainMatrixTool/out_json

python -m stateSpaceDesign.gainMatrixTool.cli batch \
  --yaml stateSpaceDesign/gainMatrixTool/in/cases.yaml \
  --verify --pretty \
  --export_dir stateSpaceDesign/gainMatrixTool/out_json
```

## Python API
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
    pretty=False
)
print(payload["K"])
```

## Notes
- Depends on: `numpy`, `control>=0.10.2`, `pyyaml` (for YAML batch), `tqdm` (batch progress).
- Outputs JSON to the path you choose; logs go where you point `--log`.
