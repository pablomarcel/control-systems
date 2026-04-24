
# README — `stateSpaceAnalysis.canonicalTool` Command Cookbook (v2)

Run from the **repo root** (`…/modernControl`). Outputs default to
`stateSpaceAnalysis/canonicalTool/out/`. Use quotes around coefficient lists.

> CLI:
>
> ```bash
> runroot python -m state_space_analysis.canonicalTool.cli [COMMAND] [OPTIONS]
> ```
>
> Current command: **`compare`** — Builds CCF/OCF/Modal, checks TF equality, and plots step responses.

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
runroot mkdir -p state_space_analysis/canonicalTool/out
# -----------------------------------------------------------------------------
```

---

## 0) Help / sanity

```bash
runroot python -m state_space_analysis.canonicalTool.cli --help
runroot python -m state_space_analysis.canonicalTool.cli compare --help
```

---

## 1) Minimal, CI‑safe runs (MPL, no GUI)

```bash
runroot python -m state_space_analysis.canonicalTool.cli compare   --num "2,3" --den "1,1,10"   --tfinal 0.5 --dt 0.01   --no_show   --backend mpl   --save "stateSpaceAnalysis/canonicalTool/out/canonical_compare_{kind}.png"
```

---

## 2) Canonical comparisons (various plants)

### A) Ogata‑style demo
```bash
runroot python -m state_space_analysis.canonicalTool.cli compare   --num "2, 3" --den "1, 1, 10"   --tfinal 8 --dt 0.001 --no_show   --backend mpl   --save "stateSpaceAnalysis/canonicalTool/out/ogata_demo_{kind}.png"
```

### B) 2nd‑order underdamped
```bash
runroot python -m state_space_analysis.canonicalTool.cli compare   --num "1" --den "1, 1.2, 4"   --tfinal 4 --dt 0.002 --no_show   --backend mpl   --save "stateSpaceAnalysis/canonicalTool/out/so_ud_{kind}.png"
```

### C) Relative degree 2 (cubic denominator)
```bash
runroot python -m state_space_analysis.canonicalTool.cli compare   --num "1" --den "1, 3, 3, 1"   --tfinal 5 --dt 0.002 --no_show   --backend mpl   --save "stateSpaceAnalysis/canonicalTool/out/cubic_den_{kind}.png"
```

### D) Short numerator (auto left‑pad)
```bash
runroot python -m state_space_analysis.canonicalTool.cli compare   --num "5, 1" --den "2, 0, 3, 4"   --tfinal 5 --dt 0.002 --no_show   --backend mpl   --save "stateSpaceAnalysis/canonicalTool/out/short_num_{kind}.png"
```

---

## 3) Symbolic \(G(s)\) print (SymPy)

```bash
runroot python -m state_space_analysis.canonicalTool.cli compare   --num "2, 3" --den "1, 1, 10"   --tfinal 1.0 --dt 0.01   --symbolic --no_show   --backend mpl   --save "stateSpaceAnalysis/canonicalTool/out/symbolic_demo_{kind}.png"
```

---

## 4) Plotly path (and clean fallback behavior)

The app tries Plotly **first** when `--backend plotly`:

- **HTML** always works with Plotly (no extra deps):
  ```bash
  runroot python -m state_space_analysis.canonicalTool.cli compare     --num "2, 3" --den "1, 1, 10"     --tfinal 2.0 --dt 0.005 --no_show     --backend plotly     --save "stateSpaceAnalysis/canonicalTool/out/plotly_compare_{kind}.html"
  ```
- **Static images** (PNG/SVG) with Plotly require **Kaleido**: pip install -U plotly kaleido

```bash
runroot python -m state_space_analysis.canonicalTool.cli compare     --num "1" --den "1, 0.6, 1"     --tfinal 3.0 --dt 0.002 --no_show     --backend plotly     --save "stateSpaceAnalysis/canonicalTool/out/plotly_compare_{kind}.png"
```

**Auto‑fallback:** If Plotly isn’t available or its image export fails, the app
falls back to Matplotlib. If you passed an `*.html` save path, it **auto‑rewrites**
to `*.png` so the run won’t crash. You’ll see a short stderr note about the fallback.

---

## 5) Edge‑case normalization

```bash
# Leading zeros in denominator (normalized internally)
runroot python -m state_space_analysis.canonicalTool.cli compare   --num "0, 2, 3" --den "0, 1, 1, 10"   --tfinal 1.5 --dt 0.005 --no_show   --backend mpl   --save "stateSpaceAnalysis/canonicalTool/out/leading_zeros_den_{kind}.png"
```

```bash
# Constant numerator, 2nd‑order denominator
runroot python -m state_space_analysis.canonicalTool.cli compare   --num "1" --den "1, 2, 2"   --tfinal 2.0 --dt 0.002 --no_show   --backend mpl   --save "stateSpaceAnalysis/canonicalTool/out/const_num_{kind}.png"
```

---

## 6) Batch runs

```bash
# Sweep two systems (MPL)
for spec in "2,3|1,1,10" "1|1,2,2"; do
  IFS="|" read n d <<< "$spec"
  runroot python -m state_space_analysis.canonicalTool.cli compare     --num "$n" --den "$d"     --tfinal 2.0 --dt 0.005 --no_show     --backend mpl     --save "stateSpaceAnalysis/canonicalTool/out/batch_${n//[, ]/_}_${d//[, ]/_}_{kind}.png"
done
```

```bash
# Compare MPL vs Plotly (HTML) for the same plant
runroot python -m state_space_analysis.canonicalTool.cli compare   --num "2,3" --den "1,1,10"   --tfinal 1.5 --dt 0.002 --no_show   --backend mpl   --save "stateSpaceAnalysis/canonicalTool/out/mpl_batch_{kind}.png"

runroot python -m state_space_analysis.canonicalTool.cli compare   --num "2,3" --den "1,1,10"   --tfinal 1.5 --dt 0.002 --no_show   --backend plotly   --save "stateSpaceAnalysis/canonicalTool/out/plotly_batch_{kind}.html"
```

---

## 7) CI tips

```bash
export MPLBACKEND=Agg
runroot python -m state_space_analysis.canonicalTool.cli compare   --num "2,3" --den "1,1,10"   --tfinal 0.5 --dt 0.01 --no_show   --backend mpl   --save "stateSpaceAnalysis/canonicalTool/out/ci_smoke_{kind}.png"
```

---

## 8) Programmatic API quickstart

```bash
runroot python - << 'PY'
from stateSpaceAnalysis.canonicalTool.apis import CanonicalAPI
api = CanonicalAPI()
res = api.compare(num=[2,3], den=[1,1,10], tfinal=0.5, dt=0.01, symbolic=True,
                  backend="plotly", show=False,
                  save="stateSpaceAnalysis/canonicalTool/out/api_{kind}.html")
print("TF Equal:", res["tf_equal"])
print("Has symbolic G(s):", bool(res["symbolic"]))
PY
```
