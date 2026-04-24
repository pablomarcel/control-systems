
# modelingSystems.converterTool — Run Commands (TF ↔ SS, Ogata §2‑6)

This sheet collects **all practical run commands** for the Converter Tool.  
Assumptions:
- You are currently inside: `modernControl/modelingSystems/converterTool`
- Inputs live in `modelingSystems/converterTool/in/`
- Outputs live in `modelingSystems/converterTool/out/`
- We always execute with `runroot python -m modelingSystems.converterTool.cli ...` so the module imports resolve from the repo root.

> Tip: Create the output directory once: `runroot mkdir -p modelingSystems/converterTool/out`

---

## -1) One‑time session bootstrap (copy/paste once per new shell)
```bash
# --- run-from-root helpers ----------------------------------------------------
# Find project root: prefer Git; otherwise, walk up until we see a marker file.
_mc_root() {
  if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git rev-parse --show-toplevel
    return
  fi
  # Fallback: ascend until we find a recognizable root marker typical of modernControl.
  local d="$PWD"
  while [ "$d" != "/" ]; do
    if [ -d "$d/.git" ] || [ -f "$d/pytest.ini" ] || [ -f "$d/pyproject.toml" ] || [ -f "$d/setup.cfg" ]; then
      echo "$d"; return
    fi
    d="$(dirname "$d")"
  done
  echo "$PWD"
}

# Run a command from the project root (without changing your current shell dir)
runroot() { ( cd "$(_mc_root)" && "$@" ); }

# Ensure out/ exists where the app expects to write
runroot mkdir -p modeling_control_systems/converterTool/out
# -----------------------------------------------------------------------------
```

---

## 0) Environment
```bash
# Optional: install extras used below (SymPy for pretty rational forms)
runroot python -m pip install sympy
```

---

## 1) Quick help / sanity
```bash
runroot python -m modeling_control_systems.converterTool.cli --help
```

---

## 2) TF → SS (with SymPy pretty print)
```bash
runroot python -m modeling_control_systems.converterTool.cli \
  --num "1,0" --den "1,14,56,160" --sympy
```

```bash
# Save a tiny JSON summary alongside printing
runroot python -m modeling_control_systems.converterTool.cli \
  --num "1,0" --den "1,14,56,160" --sympy \
  --save-json modeling_control_systems/converterTool/out/tf2ss_summary.json
```

---

## 3) SS → TF (SISO)
```bash
runroot python -m modeling_control_systems.converterTool.cli \
  --A "0 1 0; 0 0 1; -5 -25 -5" \
  --B "0; 25; -120" \
  --C "1 0 0" \
  --D "0" \
  --sympy
```

```bash
# No plots (CI‑friendly)
runroot python -m modeling_control_systems.converterTool.cli \
  --A "0 1 0; 0 0 1; -5 -25 -5" \
  --B "0; 25; -120" \
  --C "1 0 0" \
  --D "0" \
  --sympy --no-plot
```

---

## 4) TF ↔ SS cross‑check (SISO)
```bash
runroot python -m modeling_control_systems.converterTool.cli \
  --num "1,0" --den "1,14,56,160" \
  --A "0 1 0; 0 0 1; -160 -56 -14" \
  --B "0;1;-14" \
  --C "1 0 0" \
  --D "0" \
  --no-plot
```

---

## 5) SS → TF (MIMO), choose input channel for step plot
```bash
runroot python -m modeling_control_systems.converterTool.cli \
  --A "-1 -1; 6.5 0" \
  --B "1 1; 1 0" \
  --C "1 0; 0 1" \
  --D "0 0; 0 0" \
  --iu 0
```

```bash
# Same model, plot response for input u2 instead
runroot python -m modeling_control_systems.converterTool.cli \
  --A "-1 -1; 6.5 0" \
  --B "1 1; 1 0" \
  --C "1 0; 0 1" \
  --D "0 0; 0 0" \
  --iu 1
```

---

## 6) Performance/CI switches
```bash
# Disable all plots to keep tests/headless runs snappy
runroot python -m modeling_control_systems.converterTool.cli \
  --num "1,0" --den "1,14,56,160" \
  --no-plot
```

```bash
# Finer integration grid (if you want more resolution on the step response)
runroot python -m modeling_control_systems.converterTool.cli \
  --num "1,0" --den "1,14,56,160" \
  --tfinal 12.0 --dt 5e-4
```

---

## 7) Tools — Samples & Class Diagram (no system Graphviz required)
```bash
# Create a couple of small example JSON files in ./in
runroot python -m modeling_control_systems.converterTool.tools.samples
```

```bash
# Emit a Graphviz DOT file (safe on macOS 13.7.x without 'dot')
runroot python -m modeling_control_systems.converterTool.tools.class_diagram
# -> writes: modeling_control_systems/converterTool/out/converterTool_class_diagram.dot
# You can render it later on a machine with Graphviz:
# dot -Tpng modeling_control_systems/converterTool/out/converterTool_class_diagram.dot -o modeling_control_systems/converterTool/out/converterTool_class_diagram.png
```

---

## 8) Sphinx docs skeleton (autodoc‑ready)
```bash
runroot python -m modeling_control_systems.converterTool.cli sphinx-skel docs --force
# Then build docs (if Sphinx is installed):
# runroot sphinx-build -b html docs docs/_build/html
```

---

## 9) File cheat sheet
- Inputs: `modelingSystems/converterTool/in/*.json` (optional; CLI also accepts inline matrices/vectors)
- Outputs: `modelingSystems/converterTool/out/*.json`, plus any images/plots you save explicitly

---

## 10) Troubleshooting
```bash
# Sanity-check that 'control' is importable and version is visible
runroot python - <<'PY'
import control, sys
print("python-control", getattr(control, "__version__", "unknown"))
PY
```

```bash
# If SymPy pretty print doesn't show, ensure SymPy is present:
runroot python - <<'PY'
import sympy as sp
print("sympy", sp.__version__)
PY
```
