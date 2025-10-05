# stateSpaceDesign.minOrdTool — Minimum-Order Observer (Ogata §10-5)

Object-oriented refactor of a working standalone script into a testable, scalable package.

- **Entry point (CLI):**
  ```bash
  python -m stateSpaceDesign.minOrdTool.cli --help
  ```
- **Inputs** live in: `stateSpaceDesign/minOrdTool/in/`
- **Outputs** land in: `stateSpaceDesign/minOrdTool/out/` by default

## Quick start

Ogata Example 10-8 (C = [1 0 0]), explicit `K`:
```bash
python -m stateSpaceDesign.minOrdTool.cli   --A "0 1 0; 0 0 1; -6 -11 -6"   --B "0;0;1"   --C "1 0 0"   --K "90 29 4"   --poles -10 -10   --pretty --export-json "stateSpaceDesign/minOrdTool/out/ex108.json"
```

Design `K` from poles:
```bash
python -m stateSpaceDesign.minOrdTool.cli   --A "0 1 0; 0 0 1; -6 -11 -6"   --B "0;0;1"   --C "1 0 0"   --K_poles "-2+2*sqrt(3)j, -2-2*sqrt(3)j, -6"   --poles -10 -10   --pretty --export-json "stateSpaceDesign/minOrdTool/out/ex108_from_poles.json"
```

Rotate `C`:
```bash
python -m stateSpaceDesign.minOrdTool.cli   --A "0 1 0; 0 0 1; -6 -11 -6"   --B "0;0;1"   --C "0.6 0.8 0"   --poles -10 -10   --pretty --export-json "stateSpaceDesign/minOrdTool/out/ex108_rotatedC.json"
```

Diagnostics:
```bash
python -m stateSpaceDesign.minOrdTool.cli ... --pretty --verbose
```

Use pseudoinverse if S is singular (diagnostic only):
```bash
python -m stateSpaceDesign.minOrdTool.cli ... --allow_pinv --pretty
```

## Class Diagram
Generate Graphviz PNG (optional):
```bash
python -m stateSpaceDesign.minOrdTool.tools.class_diagram   --out "stateSpaceDesign/minOrdTool/out/minOrdTool_classes.png"
```

## Testing
```bash
pytest stateSpaceDesign/minOrdTool/tests -q
```
