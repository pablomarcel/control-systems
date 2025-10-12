# README — `stateSpaceAnalysis.stateTransTool` Command Cookbook
_Run all commands from your **repo root** (`modernControl/`)._  
CLI entry point:
```bash
python -m stateSpaceAnalysis.stateTransTool.cli [OPTIONS]
```
All exported files in these recipes go to:
```
stateSpaceAnalysis/stateTransTool/out
```

> Notes
> - The parser expects explicit multiplication (use `3*s`, not `3s`).
> - `--numeric` only affects matrices when you also pass `--eval t0`.
> - `--export-json` writes symbolic Φ(t) (and Φ⁻¹(t) if requested).

---

## 0) Quick help / sanity
```bash
python -m stateSpaceAnalysis.stateTransTool.cli --help
```

Minimal smoke (pretty symbolic, Example 9‑1, controllable):
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --pretty
```

---

## 1) Ogata Example 9‑5 style (controllable companion)
Symbolic (pretty):
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --pretty
```
Evaluate numerically at _t = 1 s_:
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --eval 1 \
  --numeric
```
Export Φ(t) (symbolic) to JSON:
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --export-json stateSpaceAnalysis/stateTransTool/out/phi_ogata9_1_controllable.json
```

---

## 2) Other realizations (same TF)
Observable companion (pretty):
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical observable \
  --pretty
```

Diagonal/modal via partial fractions (simple poles at −1, −2):
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical diagonal \
  --pretty
```

Jordan canonical (useful mainly with repeated poles):
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --tf "(s+3)/(s^2+3*s+2)" \
  --canonical jordan \
  --pretty
```

---

## 3) Custom transfer functions
Rational expression:
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --tf "(2*s+5)/(s^2+4*s+5)" \
  --canonical controllable \
  --pretty
```

CSV coefficient lists (descending powers):
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --num "2, 5" \
  --den "1, 4, 5" \
  --canonical diagonal \
  --pretty
```

Inverse Φ⁻¹(t) as well (symbolic pretty):
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --tf "(s+3)/(s^2+3*s+2)" \
  --canonical controllable \
  --inverse \
  --pretty
```

Numerical evaluation + inverse at _t = 0.5 s_:
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --tf "(2*s+5)/(s^2+4*s+5)" \
  --canonical controllable \
  --eval 0.5 \
  --numeric \
  --inverse
```

---

## 4) JSON exports (organized filenames in `out/`)
Pretty + JSON (symbolic):
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical observable \
  --pretty \
  --export-json stateSpaceAnalysis/stateTransTool/out/phi_ogata9_1_observable.json
```

Eval @ t=1 (numeric) + JSON (symbolic):
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --eval 1 \
  --numeric \
  --export-json stateSpaceAnalysis/stateTransTool/out/phi_eval1s_controllable.json
```

Inverse included:
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical diagonal \
  --inverse \
  --export-json stateSpaceAnalysis/stateTransTool/out/phi_diag_with_inverse.json
```

Repeated‑pole (Jordan) case with export:
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --tf "1/((s+1)^2)" \
  --canonical jordan \
  --export-json stateSpaceAnalysis/stateTransTool/out/phi_jordan_repeated_pole.json
```

---

## 5) Edge‑case / fallback demonstrations
Diagonal fallback to eigen‑diagonalization (repeated poles):
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --tf "(s+0)/((s+1)^2)" \
  --canonical diagonal \
  --pretty
```

Observable vs. controllable consistency check (same TF, two views):
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --tf "(s+3)/(s^2+3*s+2)" \
  --canonical observable \
  --pretty
```

```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --tf "(s+3)/(s^2+3*s+2)" \
  --canonical controllable \
  --pretty
```

---

## 6) Logging verbosity (DEBUG/INFO/WARNING)
Show internal messages (e.g., diagonal fallback):
```bash
python -m stateSpaceAnalysis.stateTransTool.cli \
  --tf "1/((s+1)^2)" \
  --canonical diagonal \
  --pretty \
  --log DEBUG
```

---

## 7) One‑liners (quick copy/paste)
```bash
python -m stateSpaceAnalysis.stateTransTool.cli --example ogata_9_1 --canonical controllable --pretty
python -m stateSpaceAnalysis.stateTransTool.cli --example ogata_9_1 --canonical controllable --eval 1 --numeric
python -m stateSpaceAnalysis.stateTransTool.cli --example ogata_9_1 --canonical observable --pretty
python -m stateSpaceAnalysis.stateTransTool.cli --example ogata_9_1 --canonical diagonal --pretty
python -m stateSpaceAnalysis.stateTransTool.cli --tf "(s+3)/(s^2+3*s+2)" --canonical jordan --pretty
python -m stateSpaceAnalysis.stateTransTool.cli --tf "(2*s+5)/(s^2+4*s+5)" --canonical controllable --pretty
python -m stateSpaceAnalysis.stateTransTool.cli --num "2, 5" --den "1, 4, 5" --canonical diagonal --pretty
python -m stateSpaceAnalysis.stateTransTool.cli --tf "(s+3)/(s^2+3*s+2)" --canonical controllable --inverse --pretty
python -m stateSpaceAnalysis.stateTransTool.cli --example ogata_9_1 --canonical controllable --export-json stateSpaceAnalysis/stateTransTool/out/phi_ogata9_1_controllable.json
python -m stateSpaceAnalysis.stateTransTool.cli --example ogata_9_1 --canonical controllable --eval 1 --numeric --export-json stateSpaceAnalysis/stateTransTool/out/phi_eval1s_controllable.json
python -m stateSpaceAnalysis.stateTransTool.cli --tf "1/((s+1)^2)" --canonical jordan --export-json stateSpaceAnalysis/stateTransTool/out/phi_jordan_repeated_pole.json
```

---

## 8) Troubleshooting
- **SympifyError with strings like `3s`**: use explicit multiplication: `3*s`.
- **`--numeric` printed for general `t`?** `--numeric` is only applied when `--eval` is provided.
- **Exports not found**: ensure parent dir exists or use the `out/` paths shown above.

