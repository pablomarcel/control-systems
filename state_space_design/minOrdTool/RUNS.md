# minOrdTool — RUNS.md (inside-package edition)

These commands are designed to be executed **from inside this folder**:
```
modernControl/stateSpaceDesign/minOrdTool/
```
Thanks to the import shim in `cli.py`, you can run:
```
python cli.py <args...>
```
(You can still use the project-root module form `python -m stateSpaceDesign.minOrdTool.cli`, but this doc focuses on *inside-package* usage.)

> Notes
> - Outputs default to `./out/` when you pass a basename or relative path.
> - When supplying values that start with `-` (e.g., `--poles -10 -10`), our CLI
>   coalesces consecutive negative tokens automatically; you can also use equals-form:
>   `--poles=-10,-10` or quoted CSV `" -10,-10 "`.
> - JSON payloads are **safe** (NumPy → lists; complex → `[re, im]` with tiny `im≈0` collapsed to real).

---

## 0) Help

```bash
python cli.py --help
```

---

## 1) Ogata Example 10-8 — explicit `K`

```bash
python cli.py   --A "0 1 0; 0 0 1; -6 -11 -6"   --B "0;0;1"   --C "1 0 0"   --K "90 29 4"   --poles -10 -10   --pretty --export-json out/ex108.json
```

### 1.1) Same, equals-form poles (robust with leading minus)

```bash
python cli.py   --A "0 1 0; 0 0 1; -6 -11 -6"   --B "0;0;1"   --C "1 0 0"   --K "90 29 4"   --poles=-10,-10   --pretty --export-json out/ex108_eq.json
```

---

## 2) Design `K` from poles

```bash
python cli.py   --A "0 1 0; 0 0 1; -6 -11 -6"   --B "0;0;1"   --C "1 0 0"   --K_poles "-2+2*sqrt(3)j" "-2-2*sqrt(3)j" "-6"   --poles -10 -10   --pretty --export-json out/ex108_fromKpoles.json
```

### 2.1) CSV `K_poles` (single-arg form)

```bash
python cli.py   --A "0 1 0; 0 0 1; -6 -11 -6"   --B "0;0;1"   --C "1 0 0"   --K_poles "-2+2*sqrt(3)j, -2-2*sqrt(3)j, -6"   --poles -10 -10   --export-json out/ex108_fromKpoles_csv.json
```

---

## 3) Rotate `C` (still p=1)

```bash
python cli.py   --A "0 1 0; 0 0 1; -6 -11 -6"   --B "0;0;1"   --C "0.6 0.8 0"   --poles -10 -10   --pretty --export-json out/ex108_rotatedC.json
```

---

## 4) Deep diagnostics

```bash
python cli.py   --A "0 1 0; 0 0 1; -6 -11 -6"   --C "1 0 0"   --poles -10 -10   --pretty --verbose   --export-json out/diag_verbose.json
```

---

## 5) Pseudoinverse path (diagnostic only)

If `S` is singular (e.g., deliberately constructed), inspect with pseudoinverse:

```bash
python cli.py   --A "0 0; 0 0"   --C "1 0"   --poles -1   --allow_pinv   --export-json out/allow_pinv_demo.json
```

---

## 6) Minimal runs (quiet / headless JSON)

```bash
python cli.py   --A "0 1 0; 0 0 1; -6 -11 -6"   --C "1 0 0"   --poles -10 -10   --export-json out/smoke.json
```

---

## 7) Complex poles with `sqrt()` helpers

```bash
python cli.py   --A "0 1 0; 0 0 1; -6 -11 -6"   --B "0;0;1"   --C "1 0 0"   --K_poles "-2+2*sqrt(3)j" "-2-2*sqrt(3)j" "-6"   --poles "-8+4j" "-8-4j"   --pretty --export-json out/complex_poles.json
```

---

## 8) Explicit `B` omitted (observer only)

```bash
python cli.py   --A "0 1; -2 -3"   --C "1 0"   --poles -6   --export-json out/observer_only.json
```

---

## 9) Robust negative tokens (CLI coalescing demo)

```bash
python cli.py   --A "0 1 0; 0 0 1; -6 -11 -6"   --C "1 0 0"   --poles -10 -10   --export-json out/neg_tokens.json
```

Equivalent (equals-form):

```bash
python cli.py   --A "0 1 0; 0 0 1; -6 -11 -6"   --C "1 0 0"   --poles=-10,-10   --export-json out/neg_tokens_eq.json
```

---

## 10) SymPy pretty print only (no `B`)

```bash
python cli.py   --A "0 1 0; 0 0 1; -6 -11 -6"   --C "1 0 0"   --poles -12 -12   --pretty --export-json out/sympy_pretty.json
```

---

## 11) JSON to a custom absolute path

```bash
python cli.py   --A "0 1; 0 -1"   --C "1 0"   --poles -5   --export-json "out/tmp/minord_custom.json"
```

---

## 12) Class Diagram (inside this folder)

If you have Graphviz `dot` installed, this produces a PNG; otherwise a `.dot` file is written.

```bash
python -m state_space_design.minOrdTool.tools.class_diagram --out out/minOrdTool_classes.png
# or run directly via module path from project root:
# python -m state_space_design.minOrdTool.tools.class_diagram --out state_space_design/minOrdTool/out/minOrdTool_classes.png
```

> If running *from inside* this folder and you prefer a plain `.dot`:
```bash
python -m state_space_design.minOrdTool.tools.class_diagram --out out/minOrdTool_classes.dot
```

---

## 13) Troubleshooting tips

- If `--K_poles` is used without `python-control` installed, the app will error.
  Install `python-control` or omit `--K_poles`.
- If you hit "Singular S" without `--allow_pinv`, consider rotating `C`
  (i.e., measure a different output) or re-run with `--allow_pinv` for diagnostics.
- For CI, stick to `--pretty` off for faster runs and smaller logs.

### Sphinx

python -m state_space_design.minOrdTool.cli sphinx-skel state_space_design/minOrdTool/docs
python -m sphinx -b html docs docs/_build/html
open docs/_build/html/index.html
sphinx-autobuild docs docs/_build/html