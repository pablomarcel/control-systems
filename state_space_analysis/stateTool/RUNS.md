# README — `stateSpaceAnalysis.stateTool` Command Cookbook (Updated)

Run **from the repo root** (`modernControl/`).  
CLI entry point:
```bash
runroot python -m state_space_analysis.stateTool.cli [options]
```
> Heads‑up: shells like `zsh` will try to expand `[OPTIONS]`. Type actual flags (don’t include the square brackets).

## Output directory rule
All exported files are written **automatically** to:
```
stateSpaceAnalysis/stateTool/out/
```
When using `--export-json`, **pass only a filename** (not a path). Example:
```bash
--export-json sys_summary_state.json
```
…which will be saved as:
```
stateSpaceAnalysis/stateTool/out/sys_summary_state.json
```

## -1) One-time session bootstrap (copy/paste once per new shell)
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
runroot mkdir -p state_space_analysis/stateTool/out
# -----------------------------------------------------------------------------
```

---

## 0) Quick help & smoke

Show help
```bash
runroot python -m state_space_analysis.stateTool.cli --help
```

State‑space smoke (JSON to stdout)
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --C "3 1" \
  --mode all --log WARNING
```

TF smoke (JSON to stdout)
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --tf "(s + 3)/(s^2 + 3*s + 2)" \
  --mode all --log WARNING
```

---

## 1) Using state‑space matrices

Observability (rank test) — Ogata Ex. 9‑1
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --C "3 1" \
  --mode obs --pretty --log WARNING
```

Modal observability (diagonalizable case)
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --A "1 1; 2 -1" \
  --B "0; 1" \
  --C "1 0" \
  --mode obsalt --pretty --log WARNING
```

Detectability (unobservable unstable mode → NOT detectable)
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --A "1 0; 0 -1" --B "0; 1" --C "0 1" \
  --mode detect --log WARNING
```

Full battery (controllability + observability + stability checks)
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --C "3 1" \
  --D "0" \
  --mode all --pretty --log WARNING
```

Output controllability (needs `C` and `D`)
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --C "1 0" \
  --D "0" \
  --mode output --log WARNING
```

Stabilizability PBH with margin (`--eps`)
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --A "1 0; 0 -0.05" \
  --B "0; 1" \
  --mode stab --eps 0.01 --log WARNING
```

---

## 2) From a SISO transfer function (canonical realization inside)

s‑plane (no cancellation) → controllable & observable
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --tf "(s + 3)/(s^2 + 3*s + 2)" \
  --mode obssplane --log WARNING
```

s‑plane cancellation (Ogata Ex. 9‑13 / 9‑15 style)
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --tf "(s + 2.5)/((s + 2.5)*(s - 1))" \
  --mode obssplane --log WARNING
```

All checks built from TF
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --tf "(s + 3)/(s^2 + 3*s + 2)" \
  --mode all --pretty --log WARNING
```

Numeric printing (float matrices) for canonical model
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --tf "(s + 3)/(s^2 + 3*s + 2)" \
  --mode state --numeric --digits 6 --log WARNING
```

Alternate TF input style (`--num/--den`)
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --num "1, 3" \
  --den "1, 3, 2" \
  --mode all --log WARNING
```

---

## 3) Export artifacts (FILENAMES ONLY)

Export a summary JSON (state‑space)
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --C "3 1" \
  --D "0" \
  --mode all \
  --export-json sys_summary_state.json \
  --log INFO
# writes: state_space_analysis/stateTool/out/sys_summary_state.json
```

Export a summary JSON (TF)
```bash
runroot python -m state_space_analysis.stateTool.cli \
  --tf "(s + 3)/(s^2 + 3*s + 2)" \
  --mode all \
  --export-json sys_summary_tf.json \
  --log INFO
# writes: state_space_analysis/stateTool/out/sys_summary_tf.json
```

---

## 4) Mode cheat‑sheet

| Mode        | What it checks                                                                 |
|-------------|---------------------------------------------------------------------------------|
| `state`     | rank controllability: rank([B AB … A^{n-1}B])                                  |
| `alt`       | modal controllability for diagonalizable A: no zero row in \(P^{-1}B\)         |
| `splane`    | SISO s-plane minimality for controllability (no pole–zero cancellations)       |
| `output`    | output controllability (needs `C`, `D`)                                        |
| `stab`      | stabilizability via PBH on unstable/marginal eigenvalues (uses `--eps`)        |
| `obs`       | rank observability: rank([C; CA; …; CA^{n-1}])                                 |
| `obsalt`    | modal observability for diagonalizable A: no zero column in \(CP\)             |
| `obssplane` | SISO s-plane minimality for observability (no pole–zero cancellations)         |
| `detect`    | detectability via PBH on unstable/marginal eigenvalues (uses `--eps`)          |
| `all`       | runs all applicable checks                                                      |

---

## 5) Copy‑paste block

```bash
# Help
runroot python -m state_space_analysis.stateTool.cli --help

# State-space: full battery
runroot python -m state_space_analysis.stateTool.cli --A "0 1; -2 -3" --B "0; 1" --C "3 1" --D "0" --mode all --log WARNING

# Obs only
runroot python -m state_space_analysis.stateTool.cli --A "0 1; -2 -3" --B "0; 1" --C "3 1" --mode obs --pretty --log WARNING

# Obsalt
runroot python -m state_space_analysis.stateTool.cli --A "1 1; 2 -1" --B "0; 1" --C "1 0" --mode obsalt --pretty --log WARNING

# Detect
runroot python -m state_space_analysis.stateTool.cli --A "1 0; 0 -1" --B "0; 1" --C "0 1" --mode detect --log WARNING

# TF: all
runroot python -m state_space_analysis.stateTool.cli --tf "(s + 3)/(s^2 + 3*s + 2)" --mode all --pretty --log WARNING

# TF: cancellation
runroot python -m state_space_analysis.stateTool.cli --tf "(s + 2.5)/((s + 2.5)*(s - 1))" --mode obssplane --log WARNING

# Export JSON (state)
runroot python -m state_space_analysis.stateTool.cli --A "0 1; -2 -3" --B "0; 1" --C "3 1" --D "0" --mode all --export-json sys_summary_state.json --log INFO

# Export JSON (tf)
runroot python -m state_space_analysis.stateTool.cli --tf "(s + 3)/(s^2 + 3*s + 2)" --mode all --export-json sys_summary_tf.json --log INFO
```

### Sphinx

python -m state_space_analysis.stateTool.cli sphinx-skel state_space_analysis/stateTool/docs
python -m sphinx -b html docs docs/_build/html
open docs/_build/html/index.html
sphinx-autobuild docs docs/_build/html