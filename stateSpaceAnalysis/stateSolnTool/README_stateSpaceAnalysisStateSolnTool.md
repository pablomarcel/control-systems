
# README — `stateSpaceAnalysis.stateSolnTool` Command Cookbook

Run these from your **project root** (e.g., `modernControl/`).  
CLI entry point:
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli [OPTIONS]
```

> Tips
> - Use quotes around polynomials to avoid shell expansion.
> - `--pretty` prints Unicode matrices; omit it for plain strings.
> - `--verify` checks Ogata 9‑41/42 residuals (symbolic first; numeric fallback with `--tol`).  
> - Inputs/outputs: you can write JSON with `--export-json "stateSpaceAnalysis/stateSolnTool/out/<name>.json"`.
> - Use `--log DEBUG` while debugging.

---

## 0) Quick help
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli --help
```

---

## 1) Canonical Ogata Example 9‑1 (G(s) = (s+3)/(s²+3s+2))

### A) Unit step, x(0)=0, controllable companion + verification
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --u 1 \
  --pretty \
  --verify
```

### B) Same but evaluate numerically at t = 1
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --u 1 \
  --eval 1 \
  --numeric \
  --verify
```

### C) Nonzero initial condition x(0) = [1, 0]^T
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --u 1 \
  --x0 "1,0" \
  --pretty \
  --verify
```

---

## 2) Different realizations (same TF)

### A) Observable canonical
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --canonical observable \
  --u 1 \
  --pretty \
  --verify
```

### B) Diagonal / modal (simple poles only; falls back if repeated)
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --canonical diagonal \
  --u 1 \
  --pretty \
  --verify
```

### C) Jordan form (useful with repeated poles as well)
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --tf "(s+3)/(s^2+3*s+2)" \
  --canonical jordan \
  --u 1 \
  --pretty \
  --verify
```

---

## 3) Inputs and verification tuning

### A) Exponential input, tighter numeric tolerance
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --canonical controllable \
  --u "exp(-t)" \
  --pretty \
  --verify \
  --tol 1e-10
```

### B) Sinusoidal input (symbolic)
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --u "sin(2*t)" \
  --pretty \
  --verify
```

### C) Arbitrary symbolic input — polynomial in t
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --u "t**2 + 3*t + 1" \
  --pretty \
  --verify
```

---

## 4) Time-shifted initial time `t0`

### A) Start at t0 = 1.5 (checks Φ(t−t0) usage)
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --u 1 \
  --t0 1.5 \
  --pretty \
  --verify
```

### B) Start at t0 = 2.0 and evaluate at t = 3.0
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --u 1 \
  --t0 2.0 \
  --eval 3.0 \
  --numeric \
  --verify
```

---

## 5) Alternate TF inputs

### A) Rational string via `--tf`
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --tf "(s+3)/(s^2+3*s+2)" \
  --u 1 \
  --pretty \
  --verify
```

### B) Coefficients via `--num/--den` (CSV)
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --num "1,3" \
  --den "1,3,2" \
  --u 1 \
  --pretty \
  --verify
```

### C) Polynomial strings via `--num/--den`
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --num "s + 3" \
  --den "s^2 + 3*s + 2" \
  --u 1 \
  --pretty \
  --verify
```

---

## 6) JSON export (for downstream pipelines)

### A) Export symbolic Φ, x_hom, x_part, x(t)
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --u 1 \
  --export-json "stateSpaceAnalysis/stateSolnTool/out/ogata_9_1_step.json" \
  --verify
```

### B) Export after numeric evaluation (useful snapshot at t=1)
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --u 1 \
  --eval 1 \
  --numeric \
  --export-json "stateSpaceAnalysis/stateSolnTool/out/ogata_9_1_step_t1.json" \
  --verify
```

---

## 7) Numeric printing controls

### A) Evaluate and print with 12 digits
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --u 1 \
  --eval 1.2345 \
  --numeric \
  --digits 12 \
  --verify
```

---

## 8) Logging

### A) Verbose debugging (parsing / realization decisions)
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli \
  --example ogata_9_1 \
  --u 1 \
  --verify \
  --log DEBUG
```

---

## 9) Smoke checks

### A) Minimal symbolic solve (no pretty)
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli --example ogata_9_1 --u 1 --verify
```

### B) Failure mode (missing `--den`): should print an error & nonzero exit
```bash
python -m stateSpaceAnalysis.stateSolnTool.cli --num "1,2,3"
```

---

### Notes
- **Diagonal** canonical uses partial fractions (simple poles). With repeated poles, the tool falls back to controllable form.
- **Jordan** form routes through SymPy’s Jordan decomposition (can be slower for higher order systems).
- All inputs are treated **exactly** (symbolically) whenever possible, with numeric fallbacks only for verification when the residual isn’t identically zero.

