# modelingSystems.mimoTool — Run Commands (from *mimoTool* folder, using `runroot`)

This is the complete, copy‑pasteable set of commands to exercise **modelingSystems.mimoTool**.
Inputs live in `modelingSystems/mimoTool/in/` and outputs in `modelingSystems/mimoTool/out/`.

> Convention: We run everything from **inside** `modelingSystems/mimoTool`, but we execute with
> `runroot` so Python resolves modules and relative paths from the **project root**.

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
runroot mkdir -p modelingSystems/mimoTool/out
# -----------------------------------------------------------------------------
```

---

## 0) Environment helpers
```bash
```

---

## 1) Sanity checks (headless)
```bash
# Print poles for a quick smoke check (JSON to stdout; no plots shown)
runroot python -m modelingSystems.mimoTool.cli --plant two_tank --no-show --no-steps --no-sigma \
  --save-json "modelingSystems/mimoTool/out/{plant}_summary.json"
```

```bash
# Thermal plant only
runroot python -m modelingSystems.mimoTool.cli --plant two_zone_thermal --no-show --no-steps --no-sigma \
  --save-json "modelingSystems/mimoTool/out/{plant}_summary.json"
```

---

## 2) Steps per input (time domain)
```bash
# Two‑tank: step responses, no GUI, save PNGs
runroot python -m modelingSystems.mimoTool.cli \
  --plant two_tank \
  --no-show \
  --save-png "modelingSystems/mimoTool/out/{plant}_{kind}.png"
```

```bash
# Thermal: denser time grid (dt=0.1, tfinal=200)
runroot python -m modelingSystems.mimoTool.cli \
  --plant two_zone_thermal \
  --tfinal 200 --dt 0.1 \
  --no-show \
  --save-png "modelingSystems/mimoTool/out/{plant}_{kind}.png"
```

---

## 3) Singular values σ(G(jω)) (frequency domain)
```bash
# Two‑tank: only σ(G(jω)); logspace grid
runroot python -m modelingSystems.mimoTool.cli \
  --plant two_tank \
  --no-show --no-steps \
  --wmin 1e-3 --wmax 30 --npts 600 \
  --save-png "modelingSystems/mimoTool/out/{plant}_{kind}.png"
```

```bash
# Thermal: only σ(G(jω))
runroot python -m modelingSystems.mimoTool.cli \
  --plant two_zone_thermal \
  --no-show --no-steps \
  --save-png "modelingSystems/mimoTool/out/{plant}_{kind}.png"
```

---

## 4) Full run (both plants): steps + σ(G(jω)) + JSON summaries
```bash
runroot python -m modelingSystems.mimoTool.cli \
  --plant two_tank --plant two_zone_thermal \
  --tfinal 200 --dt 0.25 --wmin 1e-3 --wmax 31.62 --npts 400 \
  --no-show \
  --save-png "modelingSystems/mimoTool/out/{plant}_{kind}.png" \
  --save-json "modelingSystems/mimoTool/out/{plant}_summary.json"
```

---

## 5) Documentation scaffold (Sphinx)
```bash
# Create minimal Sphinx docs (conf.py, index.rst, api.rst, Makefile)
runroot python -m modelingSystems.mimoTool.cli sphinx-skel modelingSystems/mimoTool/docs
```

```bash
# Build HTML docs to _build/html (requires sphinx, furo)
runroot python -m sphinx -b html modelingSystems/mimoTool/docs modelingSystems/mimoTool/docs/_build/html
```

---

---

## 7) Pytest (module‑local)
```bash
# Run mimoTool tests with coverage
runroot pytest modelingSystems/mimoTool/tests \
  --override-ini addopts= \
  --cov \
  --cov-config=modelingSystems/mimoTool/.coveragerc \
  --cov-report=term-missing
```

---

## 8) Troubleshooting
- **Matplotlib on CI / headless**: use `--no-show` (as above). Backend is chosen automatically; you can also export PNGs.
- **JSON with complex poles**: The CLI and writers encode complex numbers as `{"re": ..., "im": ...}` for strict JSON compliance.
- **Run directory**: Stay inside `modelingSystems/mimoTool` to copy/paste these, but all commands execute from the repo root via `runroot`.
