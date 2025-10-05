
# minOrdTfTool — Minimum-Order Observer Controller TF (Ogata §10-5, p=1)

**Module path:** `stateSpaceDesign/minOrdTfTool`  
**I/O dirs:** `stateSpaceDesign/minOrdTfTool/in`, `stateSpaceDesign/minOrdTfTool/out`

## CLI
```bash
python -m stateSpaceDesign.minOrdTfTool.cli --help
```

### Example (explicit K, pretty + JSON)
```bash
python -m stateSpaceDesign.minOrdTfTool.cli \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --C "1 0" \
  --poles -5 \
  --K "6 4" \
  --pretty \
  --export_json "stateSpaceDesign/minOrdTfTool/out/run_basic.json"
```

### Example (design K via poles; requires `python-control`)
```bash
python -m stateSpaceDesign.minOrdTfTool.cli \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --C "1 0" \
  --poles -5 \
  --K_poles "-4,-6" \
  --export_json "stateSpaceDesign/minOrdTfTool/out/run_acker.json"
```

## Tests
```bash
pytest stateSpaceDesign/minOrdTfTool/tests -q
```

## Class Diagram (PlantUML)
The PlantUML source is in `tools/class_diagram.puml`.
Render with local PlantUML if available:
```bash
plantuml stateSpaceDesign/minOrdTfTool/tools/class_diagram.puml
```
