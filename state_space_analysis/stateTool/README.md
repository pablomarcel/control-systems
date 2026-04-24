# README — `stateSpaceAnalysis.stateTool` Command Cookbook (Updated)

Run **from the repo root** (`modernControl/`).  
CLI entry point:
```bash
python -m state_space_analysis.stateTool.cli [options]
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

---

## 0) Quick help & smoke

Show help
```bash
python -m state_space_analysis.stateTool.cli --help
```

State‑space smoke (JSON to stdout)
```bash
python -m state_space_analysis.stateTool.cli \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --C "3 1" \
  --mode all --log WARNING
```

TF smoke (JSON to stdout)
```bash
python -m state_space_analysis.stateTool.cli \
  --tf "(s + 3)/(s^2 + 3*s + 2)" \
  --mode all --log WARNING
```

---

## 1) Using state‑space matrices

Observability (rank test) — Ogata Ex. 9‑1
```bash
python -m state_space_analysis.stateTool.cli \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --C "3 1" \
  --mode obs --pretty --log WARNING
```

Modal observability (diagonalizable case)
```bash
python -m state_space_analysis.stateTool.cli \
  --A "1 1; 2 -1" \
  --B "0; 1" \
  --C "1 0" \
  --mode obsalt --pretty --log WARNING
```

Detectability (unobservable unstable mode → NOT detectable)
```bash
python -m state_space_analysis.stateTool.cli \
  --A "1 0; 0 -1" --B "0; 1" --C "0 1" \
  --mode detect --log WARNING
```

Full battery (controllability + observability + stability checks)
```bash
python -m state_space_analysis.stateTool.cli \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --C "3 1" \
  --D "0" \
  --mode all --pretty --log WARNING
```

Output controllability (needs `C` and `D`)
```bash
python -m state_space_analysis.stateTool.cli \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --C "1 0" \
  --D "0" \
  --mode output --log WARNING
```

Stabilizability PBH with margin (`--eps`)
```bash
python -m state_space_analysis.stateTool.cli \
  --A "1 0; 0 -0.05" \
  --B "0; 1" \
  --mode stab --eps 0.01 --log WARNING
```

---

## 2) From a SISO transfer function (canonical realization inside)

s‑plane (no cancellation) → controllable & observable
```bash
python -m state_space_analysis.stateTool.cli \
  --tf "(s + 3)/(s^2 + 3*s + 2)" \
  --mode obssplane --log WARNING
```

s‑plane cancellation (Ogata Ex. 9‑13 / 9‑15 style)
```bash
python -m state_space_analysis.stateTool.cli \
  --tf "(s + 2.5)/((s + 2.5)*(s - 1))" \
  --mode obssplane --log WARNING
```

All checks built from TF
```bash
python -m state_space_analysis.stateTool.cli \
  --tf "(s + 3)/(s^2 + 3*s + 2)" \
  --mode all --pretty --log WARNING
```

Numeric printing (float matrices) for canonical model
```bash
python -m state_space_analysis.stateTool.cli \
  --tf "(s + 3)/(s^2 + 3*s + 2)" \
  --mode state --numeric --digits 6 --log WARNING
```

Alternate TF input style (`--num/--den`)
```bash
python -m state_space_analysis.stateTool.cli \
  --num "1, 3" \
  --den "1, 3, 2" \
  --mode all --log WARNING
```

---

## 3) Export artifacts (FILENAMES ONLY)

Export a summary JSON (state‑space)
```bash
python -m state_space_analysis.stateTool.cli \
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
python -m state_space_analysis.stateTool.cli \
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
python -m state_space_analysis.stateTool.cli --help

# State-space: full battery
python -m state_space_analysis.stateTool.cli --A "0 1; -2 -3" --B "0; 1" --C "3 1" --D "0" --mode all --log WARNING

# Obs only
python -m state_space_analysis.stateTool.cli --A "0 1; -2 -3" --B "0; 1" --C "3 1" --mode obs --pretty --log WARNING

# Obsalt
python -m state_space_analysis.stateTool.cli --A "1 1; 2 -1" --B "0; 1" --C "1 0" --mode obsalt --pretty --log WARNING

# Detect
python -m state_space_analysis.stateTool.cli --A "1 0; 0 -1" --B "0; 1" --C "0 1" --mode detect --log WARNING

# TF: all
python -m state_space_analysis.stateTool.cli --tf "(s + 3)/(s^2 + 3*s + 2)" --mode all --pretty --log WARNING

# TF: cancellation
python -m state_space_analysis.stateTool.cli --tf "(s + 2.5)/((s + 2.5)*(s - 1))" --mode obssplane --log WARNING

# Export JSON (state)
python -m state_space_analysis.stateTool.cli --A "0 1; -2 -3" --B "0; 1" --C "3 1" --D "0" --mode all --export-json sys_summary_state.json --log INFO

# Export JSON (tf)
python -m state_space_analysis.stateTool.cli --tf "(s + 3)/(s^2 + 3*s + 2)" --mode all --export-json sys_summary_tf.json --log INFO
```
