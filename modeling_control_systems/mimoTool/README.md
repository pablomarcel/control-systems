
# modelingSystems.mimoTool

Object-oriented refactor of the educational MIMO examples (two-tank hydraulics and two-zone thermal),
with CLI, plotting, Sphinx helper, and pytest-friendly APIs.

## Quickstart

```bash
# From inside the package directory
python cli.py --plant two_tank --plant two_zone_thermal --no-show \
  --save-png "out/{plant}_{kind}.png" --save-json "out/{plant}_summary.json"
```

Generate a Sphinx skeleton:

```bash
python cli.py sphinx-skel docs
```
