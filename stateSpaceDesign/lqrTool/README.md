# stateSpaceDesign.lqrTool

Refactored, object‑oriented LQR design & simulation tool for **modernControl**.

## CLI

```bash
python -m stateSpaceDesign.lqrTool.cli --help
```

### Examples

Ogata Example 10‑13 — step (Ogata prefilter)
```bash
python -m stateSpaceDesign.lqrTool.cli   --A "0 1 0; 0 0 1; 0 -2 -3" --B "0; 0; 1"   --Q "diag:100,1,1" --R "0.01"   --C "1 0 0"   --step --prefilter ogata --tfinal 8 --dt 0.01 --plots mpl   --save_prefix stateSpaceDesign/lqrTool/out/ogata1013
```

Same with unity‑DC prefilter:
```bash
python -m stateSpaceDesign.lqrTool.cli   --A "0 1 0; 0 0 1; 0 -2 -3" --B "0; 0; 1"   --Q "diag:100,1,1" --R "0.01"   --C "1 0 0"   --step --prefilter dcgain --tfinal 8 --plots mpl   --save_prefix stateSpaceDesign/lqrTool/out/ogata1013_dc
```

Initial‑condition response only:
```bash
python -m stateSpaceDesign.lqrTool.cli   --A "0 1; 0 -1" --B "0; 1"   --Q "eye" --R "1"   --x0 "1 1" --tfinal 6 --plots mpl   --save_prefix stateSpaceDesign/lqrTool/out/ic_demo
```

## Class Diagram

```bash
python -m stateSpaceDesign.lqrTool.tools.tool_classdiagram --out stateSpaceDesign/lqrTool/out/lqrTool.dot
dot -Tpng stateSpaceDesign/lqrTool/out/lqrTool.dot -o stateSpaceDesign/lqrTool/out/lqrTool.png
```
