# RUNS — `stateSpaceAnalysis/stateTransTool` (run-from-anywhere edition)

> Paste these commands directly in your terminal **from inside this package** (or anywhere).
> The helper functions will hop to your repo root, run the command, and hop back.
> Works with **bash** and **zsh**.

---

## 0) One-time session bootstrap (copy/paste once per new shell)
```bash
# --- run-from-root helpers ----------------------------------------------------
# Find project root: prefer Git; otherwise, walk up until we see a marker file.
_mc_root() {
  if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git rev-parse --show-toplevel
    return
  fi
  # Fallback: ascend until we find a recognizable root marker.
  local d="$PWD"
  while [ "$d" != "/" ]; do
    if [ -d "$d/.git" ] || [ -f "$d/pytest.ini" ] || [ -f "$d/pyproject.toml" ]; then
      echo "$d"; return
    fi
    d="$(dirname "$d")"
  done
  echo "$PWD"
}

# Run a command from the project root (without changing your current shell dir)
runroot() { ( cd "$(_mc_root)" && "$@" ); }

# Ensure out/ exists where the app expects to write
runroot mkdir -p state_space_analysis/stateTransTool/out
# -----------------------------------------------------------------------------
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
runroot python -m state_space_analysis.stateTransTool.cli --help
```

Minimal smoke (pretty symbolic, Example 9‑1, controllable):
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --pretty
```

---

## 1) Ogata Example 9‑5 style (controllable companion)
Symbolic (pretty):
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --pretty
```
Evaluate numerically at _t = 1 s_:
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --eval 1 \
  --numeric
```
Export Φ(t) (symbolic) to JSON:
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --export-json state_space_analysis/stateTransTool/out/phi_ogata9_1_controllable.json
```

---

## 2) Other realizations (same TF)
Observable companion (pretty):
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical observable \
  --pretty
```

Diagonal/modal via partial fractions (simple poles at −1, −2):
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical diagonal \
  --pretty
```

Jordan canonical (useful mainly with repeated poles):
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --tf "(s+3)/(s^2+3*s+2)" \
  --canonical jordan \
  --pretty
```

---

## 3) Custom transfer functions
Rational expression:
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --tf "(2*s+5)/(s^2+4*s+5)" \
  --canonical controllable \
  --pretty
```

CSV coefficient lists (descending powers):
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --num "2, 5" \
  --den "1, 4, 5" \
  --canonical diagonal \
  --pretty
```

Inverse Φ⁻¹(t) as well (symbolic pretty):
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --tf "(s+3)/(s^2+3*s+2)" \
  --canonical controllable \
  --inverse \
  --pretty
```

Numerical evaluation + inverse at _t = 0.5 s_:
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
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
runroot python -m state_space_analysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical observable \
  --pretty \
  --export-json state_space_analysis/stateTransTool/out/phi_ogata9_1_observable.json
```

Eval @ t=1 (numeric) + JSON (symbolic):
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --eval 1 \
  --numeric \
  --export-json state_space_analysis/stateTransTool/out/phi_eval1s_controllable.json
```

Inverse included:
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --example ogata_9_1 \
  --canonical diagonal \
  --inverse \
  --export-json state_space_analysis/stateTransTool/out/phi_diag_with_inverse.json
```

Repeated‑pole (Jordan) case with export:
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --tf "1/((s+1)^2)" \
  --canonical jordan \
  --export-json state_space_analysis/stateTransTool/out/phi_jordan_repeated_pole.json
```

---

## 5) Edge‑case / fallback demonstrations
Diagonal fallback to eigen‑diagonalization (repeated poles):
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --tf "(s+0)/((s+1)^2)" \
  --canonical diagonal \
  --pretty
```

Observable vs. controllable consistency check (same TF, two views):
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --tf "(s+3)/(s^2+3*s+2)" \
  --canonical observable \
  --pretty
```

```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --tf "(s+3)/(s^2+3*s+2)" \
  --canonical controllable \
  --pretty
```

---

## 6) Logging verbosity (DEBUG/INFO/WARNING)
Show internal messages (e.g., diagonal fallback):
```bash
runroot python -m state_space_analysis.stateTransTool.cli \
  --tf "1/((s+1)^2)" \
  --canonical diagonal \
  --pretty \
  --log DEBUG
```

---

## 7) One‑liners (quick copy/paste)
```bash
runroot python -m state_space_analysis.stateTransTool.cli --example ogata_9_1 --canonical controllable --pretty
runroot python -m state_space_analysis.stateTransTool.cli --example ogata_9_1 --canonical controllable --eval 1 --numeric
runroot python -m state_space_analysis.stateTransTool.cli --example ogata_9_1 --canonical observable --pretty
runroot python -m state_space_analysis.stateTransTool.cli --example ogata_9_1 --canonical diagonal --pretty
runroot python -m state_space_analysis.stateTransTool.cli --tf "(s+3)/(s^2+3*s+2)" --canonical jordan --pretty
runroot python -m state_space_analysis.stateTransTool.cli --tf "(2*s+5)/(s^2+4*s+5)" --canonical controllable --pretty
runroot python -m state_space_analysis.stateTransTool.cli --num "2, 5" --den "1, 4, 5" --canonical diagonal --pretty
runroot python -m state_space_analysis.stateTransTool.cli --tf "(s+3)/(s^2+3*s+2)" --canonical controllable --inverse --pretty
runroot python -m state_space_analysis.stateTransTool.cli --example ogata_9_1 --canonical controllable --export-json state_space_analysis/stateTransTool/out/phi_ogata9_1_controllable.json
runroot python -m state_space_analysis.stateTransTool.cli --example ogata_9_1 --canonical controllable --eval 1 --numeric --export-json state_space_analysis/stateTransTool/out/phi_eval1s_controllable.json
runroot python -m state_space_analysis.stateTransTool.cli --tf "1/((s+1)^2)" --canonical jordan --export-json state_space_analysis/stateTransTool/out/phi_jordan_repeated_pole.json
```

---

## 8) Troubleshooting
- **SympifyError with strings like `3s`**: use explicit multiplication: `3*s`.
- **`--numeric` printed for general `t`?** `--numeric` is only applied when `--eval` is provided.
- **Exports not found**: ensure parent dir exists or use the `out/` paths shown above.

