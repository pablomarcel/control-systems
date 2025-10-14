# System Modeling — Run Commands (from repo root)

All commands **must be run from the root of the `modernControl` repo** and begin with `runroot python`.
Inputs live in `modelingSystems/systemTool/in/` and outputs in `modelingSystems/systemTool/out/`.

> Tip: Create the output directory once: `mkdir -p modelingSystems/systemTool/out`

---

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
runroot mkdir -p modelingSystems/systemTool/out
# -----------------------------------------------------------------------------
```

---

## 0) Environment
```bash
# Core libs used by systemTool
runroot python -m pip install control sympy numpy matplotlib

# (Optional) docs and diagram extras
runroot python -m pip install furo
```
> If you hit a backend warning from matplotlib in headless CI, you can set:  
> `MPLBACKEND=Agg` before a command (e.g., `MPLBACKEND=Agg runroot python -m modelingSystems.systemTool.cli msd-step --no-save`).

---

## 1) Running the CLI
You can invoke the tool two ways; both are supported by an **import shim**:
```bash
# Preferred (module form)
runroot python -m modelingSystems.systemTool.cli --help

# Direct script (equivalent)
runroot python modelingSystems/systemTool/cli.py --help
```

### 1.1 Mass–Spring–Damper step
```bash
# Basic (defaults: m=1, b=1, k=10, u0=1, tfinal=10, dt=1e-3)
runroot python -m modelingSystems.systemTool.cli msd-step --no-save
```

```bash
# With parameters and PNG output
runroot python -m modelingSystems.systemTool.cli msd-step \
  --m 1 --b 1 --k 10 --u0 1 --tfinal 5 --dt 0.001
# -> writes modelingSystems/systemTool/out/msd_y.png and msd_states.png
```

### 1.2 Compute G(s) from (A,B,C,D)
```bash
# Use default MSD model (C = [1,0]) and print transfer function(s)
runroot python -m modelingSystems.systemTool.cli tf-from-ss
```

```bash
# Pass explicit matrices (strings that parse as Python lists)
runroot python -m modelingSystems.systemTool.cli tf-from-ss \
  --A "[[0,1],[-10,-1]]" --B "[[0],[1]]" --C "[[1,0]]" --D "[[0]]"
```

```bash
# Or derive default from m,b,k parameters
runroot python -m modelingSystems.systemTool.cli tf-from-ss --m 1 --b 1 --k 10
```

### 1.3 MIMO demo (2×2 example)
```bash
runroot python -m modelingSystems.systemTool.cli mimo-demo
# Prints numeric TF matrix and symbolic common-denominator form.
# Also produces two step plots if saving is enabled by the app (defaults to no-save from CLI).
```

### 1.4 ODE → State Space (no derivatives of u)
```bash
# Provide denominator coefficients directly: y'' + a1 y' + a2 y = b0 u
runroot python -m modelingSystems.systemTool.cli ode-no-deriv \
  --a "[1, 10]" --b0 1 --tfinal 8 --dt 0.001
# -> writes modelingSystems/systemTool/out/ode_no_deriv_step.png
```

```bash
# Convenience MSD mapping: y'' + (b/m) y' + (k/m) y = (1/m) u
runroot python -m modelingSystems.systemTool.cli ode-no-deriv --msd --m 1 --b 1 --k 10 --tfinal 6 --dt 0.001
```

### 1.5 ODE with derivatives of u (Ogata §2-5 β-construction)
```bash
# Defaults show a D=b0 jump for a unit step
runroot python -m modelingSystems.systemTool.cli ode-with-deriv --tfinal 8 --dt 0.001
```

```bash
# Explicit numerator/denominator: y'' + a1 y' + a2 y = b0 u'' + b1 u' + b2 u
runroot python -m modelingSystems.systemTool.cli ode-with-deriv \
  --a "[1,10]" \
  --b "[0.5, 1.0, 0.0]" \
  --tfinal 8 --dt 0.001
# -> writes modelingSystems/systemTool/out/ode_with_deriv_step.png
```

### 1.6 Kelvin–Voigt vs Maxwell comparison
```bash
# Overlay y(t) and F(t) for both models
runroot python -m modelingSystems.systemTool.cli kv-vs-maxwell --u0 1 --tfinal 10 --dt 0.001
# -> writes modelingSystems/systemTool/out/kv_vs_maxwell_y.png
# -> writes modelingSystems/systemTool/out/kv_vs_maxwell_force.png
# -> optional: kv_states.png, maxwell_states.png
```

---

## 2) Class Diagram (Mermaid)
The tool emits a Mermaid diagram you can paste into GitHub/VS Code markdown previews.
```bash
# Write Mermaid to systemTool/out/systemTool_class_diagram.mmd
runroot python modelingSystems/systemTool/tools/class_diagram.py --out modelingSystems/systemTool/out/systemTool_class_diagram.mmd
```

---

## 3) Sphinx Docs Skeleton
A tiny helper creates a docs skeleton ready for autodoc.
```bash
# Create docs/ under the repo root (or pass another path)
runroot python -m modelingSystems.systemTool.cli sphinx-skel docs --force

# Build HTML (requires sphinx and recommended 'furo' theme)
runroot python -m pip install sphinx furo
runroot sphinx-build -b html docs docs/_build/html
```

---

## 4) File Cheat Sheet (inputs/outputs)

- **Inputs:** `modelingSystems/systemTool/in/` (you can place JSON/CSV/matrix files here if you extend the app).
- **Outputs:** PNGs, Mermaid files, and coverage/docs artifacts land in `modelingSystems/systemTool/out/`.

---

## 5) Troubleshooting

- **Matplotlib GUI warnings:** run with `MPLBACKEND=Agg` to render headless PNGs.
- **`python-control` version quirks:** our wrapper avoids passing `X0=None`; if you see dtype-related errors, update `control` or re-run with our CLI defaults.
- **Absolute vs relative imports:** both `python -m modelingSystems.systemTool.cli` and `python modelingSystems/systemTool/cli.py` work thanks to the import shim.
- **CI speed tips:** shrink `--tfinal` and increase `--dt` for very fast plots during testing.

Happy modeling 🎛️
