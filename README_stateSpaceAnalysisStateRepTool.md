
# stateSpaceAnalysis.stateRepTool — Run Command Cookbook
_Run all commands from your **repo root** (`modernControl/`)._
Package entrypoint:
```bash
python -m stateSpaceAnalysis.stateRepTool.cli [OPTIONS]
```
Default output dir (for JSON): `stateSpaceAnalysis/stateRepTool/out/`

---

## 0) Help / sanity
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --help
```

---

## 1) Exhibit 1 (Ogata 9-1) — all canonical forms
Jordan is auto-skipped if poles are distinct.
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --example ogata_9_1 --canonical all
```

### 1.a) Explicit rational expression
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --tf "(s+3)/(s^2+3*s+2)" --canonical all
```

### 1.b) CSV coefficients (descending powers)
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --num "1, 3" --den "1, 3, 2" --canonical all
```

---

## 2) Individual canonical forms
Controllable:
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --tf "(s+3)/(s^2+3*s+2)" --canonical controllable
```
Observable:
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --tf "(s+3)/(s^2+3*s+2)" --canonical observable
```
Diagonal (modal): uses partial fractions for simple poles; falls back to eigen-diagonalization when possible.
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --tf "(s+3)/(s^2+3*s+2)" --canonical diagonal
```
Jordan (forced even when distinct poles):
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --tf "(s+3)/(s^2+3*s+2)" --canonical jordan
```

---

## 3) Repeated poles (Jordan auto-included)
Example: \( G(s) = 1/(s+1)^2 \). Diagonal may be **absent** if the system is defective (non-diagonalizable), but Jordan will be present.
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --tf "1/(s+1)^2" --canonical all
```

---

## 4) Numeric printing (float matrices) and precision
All forms (8 digits):
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --example ogata_9_1 --canonical all --numeric --digits 8
```
Controllable only, numeric:
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --tf "(s+3)/(s^2+3*s+2)" --canonical controllable --numeric
```
CSV + all + numeric (6 digits):
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --num "1, 3" --den "1, 3, 2" --canonical all --numeric --digits 6
```

---

## 5) JSON export
Export to default out dir (`stateSpaceAnalysis/stateRepTool/out/`):
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --example ogata_9_1 --canonical all --export-json ogata9_1_all.json
```
Export to a nested file in out dir:
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --tf "(s+3)/(s^2+3*s+2)" --canonical all --export-json runs/explicit_all.json
```
Export using CSV inputs:
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --num "1, 3" --den "1, 3, 2" --canonical all --export-json csv_all.json
```

> Tip: If you pass an **absolute** path to `--export-json`, it writes there. Relative paths are resolved under `stateSpaceAnalysis/stateRepTool/out/`.

---

## 6) Verification controls
By default, symbolic verification ensures each realization matches the original \(G(s)\). To disable (faster runs / numeric exploration):
```bash
python -m stateSpaceAnalysis.stateRepTool.cli --example ogata_9_1 --canonical all --no-verify
```

---

## 7) Mixed recipes (handy one-liners)

### 7.a) Simple poles, all + numeric + export
```bash
python -m stateSpaceAnalysis.stateRepTool.cli   --tf "(s+3)/(s^2+3*s+2)"   --canonical all --numeric --digits 8   --export-json examples/ogata_9_1_all_numeric.json
```

### 7.b) Force Jordan on distinct poles
```bash
python -m stateSpaceAnalysis.stateRepTool.cli   --tf "(s+3)/(s^2+3*s+2)"   --canonical jordan
```

### 7.c) Repeated pole case, skip verification, export
```bash
python -m stateSpaceAnalysis.stateRepTool.cli   --tf "1/(s+1)^2"   --canonical all --no-verify   --export-json examples/repeated_pole_all.json
```

---

## 8) Notes
- Inputs accepted:
  - `--example ogata_9_1` (prefilled)
  - `--tf "<rational in s>"` e.g. `"(s+3)/(s^2+3*s+2)"`
  - `--num "<csv>" --den "<csv>"` with descending powers
- Canonical options: `all | controllable | observable | diagonal | jordan`
- `--numeric/--digits` control float printing; JSON always stores exact SymPy strings.
- Output JSON structure per form: `{A: [[...]], B: [[...]], C: [[...]], D: "…", P: [[...]]?}`
