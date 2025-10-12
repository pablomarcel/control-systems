# README — `stateSpaceAnalysis.mimoTool` Command Cookbook

Run everything from your **repo root** (`modernControl/`).  
CLI entrypoint: `runroot python -m stateSpaceAnalysis.mimoTool.cli`  
Default outputs land in: `stateSpaceAnalysis/mimoTool/out/`

> Tips
> - Matplotlib backend is already set to headless (`Agg`) inside the CLI.
> - Set logging verbosity with env var: `MIMOTOOL_LOG=DEBUG` (defaults to INFO).
> - Use quotes for file names with spaces. No need to quote simple names.

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
runroot mkdir -p stateSpaceAnalysis/mimoTool/out
# -----------------------------------------------------------------------------
```

---

## 0) Help / sanity

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli --help
```

Show subcommand help:

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli describe --help
runroot python -m stateSpaceAnalysis.mimoTool.cli steps --help
runroot python -m stateSpaceAnalysis.mimoTool.cli sigma --help
```

---

## 1) Describe plants (JSON dump)

Two built-in examples: `two_tank`, `two_zone_thermal`.

```bash
# Two-tank hydraulics (2x2)
runroot python -m stateSpaceAnalysis.mimoTool.cli describe --plant two_tank
```

```bash
# Two-zone thermal plate (2x2)
runroot python -m stateSpaceAnalysis.mimoTool.cli describe --plant two_zone_thermal
```

Save JSON to a file (macOS/Linux):

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli describe --plant two_tank   > out/two_tank_desc.json
```

---

## 2) Step responses (per input)

By default, **one figure per input** with all outputs overlayed.

### 2.1 Quick smoke (no save)

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli steps   --plant two_tank   --tfinal 10 --dt 0.5 --no-save
```

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli steps   --plant two_zone_thermal   --tfinal 20 --dt 0.5 --no-save
```

### 2.2 Save to out/ with a custom prefix

> Produces one PNG per input: `<prefix>_step_u1.png`, `<prefix>_step_u2.png`, ...

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli steps   --plant two_tank   --tfinal 60 --dt 0.2   --save --out-prefix two_tank
```

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli steps   --plant two_zone_thermal   --tfinal 120 --dt 0.5   --save --out-prefix two_zone_thermal
```

### 2.3 High-resolution export example

```bash
MIMOTOOL_LOG=INFO runroot python -m stateSpaceAnalysis.mimoTool.cli steps   --plant two_tank   --tfinal 200 --dt 0.25   --save --out-prefix tt_hi
```

---

## 3) Singular-value plots `σ(G(jω))`

### 3.1 Quick smoke (no save)

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli sigma   --plant two_tank --no-save
```

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli sigma   --plant two_zone_thermal --no-save
```

### 3.2 Save to out/ with a custom name

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli sigma   --plant two_tank   --save --out-name two_tank_sigma.png
```

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli sigma   --plant two_zone_thermal   --save --out-name thermal_sigma.png
```

> Note: Frequency grid is fixed in the current CLI. If you need custom
> `w_min/w_max/n_pts`, use the runroot python API (`apis.SigmaRequest`).

---

## 4) Logging / debugging

Increase verbosity (DEBUG) and run a command:

```bash
MIMOTOOL_LOG=DEBUG runroot python -m stateSpaceAnalysis.mimoTool.cli describe --plant two_tank
```

---

## 5) One-liners you can run now

Describe → file:

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli describe --plant two_zone_thermal   > out/two_zone_thermal_desc.json
```

Steps → PNGs (two_tank):

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli steps --plant two_tank --tfinal 30 --dt 0.25   --save --out-prefix tt_quick
```

Sigma → PNG (thermal):

```bash
runroot python -m stateSpaceAnalysis.mimoTool.cli sigma --plant two_zone_thermal   --save --out-name thermal_sigma_quick.png
```

---

## 6) (Optional) Generate a minimal class diagram

If **Graphviz** is installed (`dot -V` works), you can render a tiny diagram:

```bash
runroot python - <<'PY'
from stateSpaceAnalysis.mimoTool.tools.tool_classdiagram import emit_basic_diagram
p = emit_basic_diagram()  # returns None if Graphviz executables are missing
print("Diagram:", p)
PY
```

The image (if rendered) will be in `stateSpaceAnalysis/mimoTool/out/mimo_classes.png`.

---

## 7) Pytest quick check

```bash
pytest stateSpaceAnalysis/mimoTool/tests \
  --override-ini addopts= \
  --cov \
  --cov-config=stateSpaceAnalysis/mimoTool/.coveragerc \
  --cov-report=term-missing
```

Happy hacking 👾
