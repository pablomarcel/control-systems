
# canonicalTool — Run Commands (modernControl)

All commands below assume you’re working *anywhere inside the repo* and want to run
the canonical forms tool reliably from the project root using a tiny helper (`runroot`).  
Inputs live in `modelingSystems/canonicalTool/in/` and outputs in `modelingSystems/canonicalTool/out/`.

> Tip: The **canonical** entry point is the CLI module:
> `python -m modelingSystems.canonicalTool.cli`

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
runroot mkdir -p modeling_control_systems/canonicalTool/out
# -----------------------------------------------------------------------------
```

---

## 0) Environment (optional)
```bash
# Core deps used by this tool.
runroot python -m pip install "control>=0.10" matplotlib scipy sympy
```

---

## 1) Quick help / sanity
```bash
runroot python -m modeling_control_systems.canonicalTool.cli --help
```

```bash
# Also available when running from inside the package (import shim enabled)
runroot python modeling_control_systems/canonicalTool/cli.py --help
```

---

## 2) Minimal runs (no plots)
```bash
# Original example (normalized internally). Prints equality checks.
runroot python -m modeling_control_systems.canonicalTool.cli   --num "2,3" --den "1,1,10" --no-plots --no-show
```

```bash
# Another plant, shorter horizon
runroot python -m modeling_control_systems.canonicalTool.cli   --num "1" --den "1,2,5" --tfinal 5 --no-plots --no-show
```

---

## 3) Symbolic transfer function (SymPy)
```bash
# Prints G(s) in symbolic form using the CCF (if SymPy is available).
runroot python -m modeling_control_systems.canonicalTool.cli   --num "2,3" --den "1,1,10" --symbolic --no-plots --no-show
```

---

## 4) Plots (headless or interactive)

```bash
# Interactive (opens a window)
runroot python -m modeling_control_systems.canonicalTool.cli   --num "2,3" --den "1,1,10"
```

```bash
# Headless PNG render (no GUI); useful for CI
runroot python -m modeling_control_systems.canonicalTool.cli   --num "2,3" --den "1,1,10" --save-png "modelingSystems/canonicalTool/out/ccf_ocf_modal.png"   --no-show
```

---

## 5) Run from within the package folder (import shim)
```bash
# cd into the package and still get absolute imports resolved correctly
runroot bash -lc 'cd modeling_control_systems/canonicalTool && python cli.py --num "2,3" --den "1,1,10" --no-plots --no-show'
```

---

## 6) Docs skeleton (Sphinx)
```bash
# Writes docs/ with conf.py, index.rst, api.rst, and a Makefile
runroot python -m modeling_control_systems.canonicalTool.cli sphinx-skel modeling_control_systems/canonicalTool/docs
```

```bash
# Build HTML docs (requires sphinx + furo)
runroot python -m pip install sphinx furo
runroot bash -lc 'cd modeling_control_systems/canonicalTool/docs && make html'
```

---

## 7) Class diagram (DOT → PNG if Graphviz `dot` is available)
```bash
# Always writes the DOT file; PNG is best-effort if 'dot' is on PATH
runroot python -m modeling_control_systems.canonicalTool.tools.class_diagram
```

```bash
# Manual Graphviz render (if you prefer explicit control)
runroot dot -Tpng modeling_control_systems/canonicalTool/out/canonicalTool_class_diagram.dot   -o modeling_control_systems/canonicalTool/out/canonicalTool_class_diagram.png
```

---

## 8) Tests (package-only quick check)
```bash
# Run this package's tests (pytest must be installed)
runroot pytest modeling_control_systems/canonicalTool/tests -q
```

---

## 9) File cheat sheet (inputs/outputs)

- **Inputs**: place any future data in `modelingSystems/canonicalTool/in/` (not required for the current CLI).
- **Outputs**: plots and artifacts go to `modelingSystems/canonicalTool/out/`.

---

## 10) Troubleshooting

- **Matplotlib backend / macOS CI** → add `--no-show` for headless runs; PNGs still save with `--save-png`.
- **Graphviz not installed** → `tools.class_diagram` still writes the `.dot` file; PNG render is skipped gracefully.
- **Equality checks** → Both OCF and Modal-real should be TF-equivalent to CCF for controllable, observable SISO systems.
- **From-anywhere runs** → Prefer `runroot` so relative paths resolve to the repo root consistently.
