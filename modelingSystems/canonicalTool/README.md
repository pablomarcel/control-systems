
# modelingSystems.canonicalTool

Refactored, OOP version of the SISO canonical forms demo (CCF / OCF / Modal-real).

## Run (from package dir)
```bash
python cli.py --num "2,3" --den "1,1,10" --symbolic --no-show --no-plots
```

## Run (from repo root)
```bash
python -m modelingSystems.canonicalTool.cli --num "1" --den "1,2,5" --tfinal 5 --no-show
```

## Generate Sphinx skeleton
```bash
python -m modelingSystems.canonicalTool.cli sphinx-skel docs
```

## Class diagram (.dot; PNG if Graphviz `dot` is available)
```bash
python -m modelingSystems.canonicalTool.tools.class_diagram
```
