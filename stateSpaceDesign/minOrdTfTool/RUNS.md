
# minOrdTfTool — RUNS.md (inside-package edition)

Run all commands **from this folder**:
```
modernControl/stateSpaceDesign/minOrdTfTool/
```
Use the import shim:
```
python cli.py <args...>
```

> Notes
> - **Single-input only**: the minimum-order controller requires `m = 1` → `B` must be `n×1`.
> - **p = 1 only**: `C` must be `1×n`.
> - Prefer **equals-form + commas** when values start with `-` (e.g., `--poles=-5`, `--K_poles="-4,-6"`). Space-separated *negative* tokens can be interpreted as options by the shell/argparse.
> - `--poles` and `--K_poles` accept **space or comma** separated lists, but for negatives, **commas** are the most reliable.
> - Use `--export_json out/<name>.json` to keep artifacts in this package’s `out/` folder.

---

## 0) Help & Version

```bash
python cli.py --help
```

---

## 1) Sanity & Smoke

### 1.1) Minimal (explicit K, JSON only)
```bash
python cli.py \
  --A "0 1; -2 -3" \
  --B "0; 1" \
  --C "1 0" \
  --poles=-5 \
  --K "6 4" \
  --export_json out/run_basic.json
```

### 1.2) Pretty + DEBUG logging
```bash
python cli.py \
  --A "0 1; -2 -3" --B "0; 1" --C "1 0" \
  --poles=-5 \
  --K "6 4" \
  --pretty --precision 6 --log DEBUG \
  --export_json out/run_debug.json
```

---

## 2) Designing **K** via poles (requires `python-control`)

### 2.1) **Reliable** comma list (equals-form safest) ✅
```bash
python cli.py \
  --A "0 1; -2 -3" --B "0; 1" --C "1 0" \
  --poles=-5 \
  --K_poles="-4,-6" \
  --export_json out/run_acker_commas.json
```

### 2.2) Complex poles — **use conjugate pair** (comma list) ✅
```bash
python cli.py \
  --A "0 1; -2 -3" --B "0; 1" --C "1 0" \
  --poles=-6 \
  --K_poles="-2+2*sqrt(3)j,-2-2*sqrt(3)j" \
  --export_json out/run_acker_complex.json
```

> You can try space lists like `--K_poles "-4" "-6"`, but some shells/argparse combos may still treat `-6` as a new option. When in doubt, prefer the **comma** form above.

---

## 3) Observer poles input variants (`--poles`)

- Space list (ok here because only one negative):  
```bash
python cli.py --A "0 1; -2 -3" --B "0; 1" --C "1 0" --poles -5 --K "6 4"
```

- Comma list (equals-form):  
```bash
python cli.py --A "0 1; -2 -3" --B "0; 1" --C "1 0" --poles="-5" --K "6 4"
```

---

## 4) Pseudoinverse diagnostic path

```bash
python cli.py \
  --A "0 1; -2 -3" --B "0; 1" --C "1 0" \
  --poles=-5 \
  --K "6 4" \
  --allow_pinv \
  --export_json out/run_allow_pinv.json
```

---

## 5) Tests

- **Quick smoke (no coverage config needed):**
```bash
pytest stateSpaceDesign/minOrdTfTool/tests -q
```

- **With coverage** (only if `.coveragerc` exists at the path below):  
```bash
pytest stateSpaceDesign/minOrdTfTool/tests \
  --override-ini addopts= \
  --cov \
  --cov-config=stateSpaceDesign/minOrdTfTool/.coveragerc \
  --cov-report=term-missing
```

If you see `Couldn't read '.coveragerc' as a config file`, run the **Quick smoke** command instead or supply a valid coverage config.

---

## 6) Class diagram (PlantUML)

```bash
plantuml stateSpaceDesign/minOrdTfTool/tools/class_diagram.puml
```

---

## 7) CI-friendly quick run (headless, JSON only)

```bash
python cli.py \
  --A "0 1; -2 -3" --B "0; 1" --C "1 0" \
  --poles=-5 \
  --K "6 4" \
  --export_json out/smoke.json
```
