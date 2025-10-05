
# README — `stateSpaceAnalysis.converterTool` Command Cookbook

Run **all commands from your project root** (e.g., `…/modernControl`).  
CLI entry point:
```bash
python -m stateSpaceAnalysis.converterTool.cli [OPTIONS]
```

Outputs (plots) default to the package `out/` directory when you pass `--out-prefix`:
```
stateSpaceAnalysis/converterTool/out/
```

> Tip: Always quote matrices/vectors that contain spaces or semicolons.
> Numbers are plain floats; matrices use row separators with semicolons (`;`).

---

## 0) Help & sanity checks

### Show help
```bash
python -m stateSpaceAnalysis.converterTool.cli --help
```

### Minimal smoke (no plot)
```bash
python -m stateSpaceAnalysis.converterTool.cli   --num "1,0" --den "1,14,56,160"   --no-plot --log INFO
```

---

## 1) TF → SS

### A) Basic TF→SS (SISO), print matrices only
```bash
python -m stateSpaceAnalysis.converterTool.cli   --num "1,0" --den "1,14,56,160"   --no-plot
```

### B) TF→SS with SymPy pretty-print (SISO)
```bash
python -m stateSpaceAnalysis.converterTool.cli   --num "1,0" --den "1,14,56,160"   --sympy --no-plot
```

### C) TF→SS + Step plot saved under `out/`
```bash
python -m stateSpaceAnalysis.converterTool.cli   --num "1,0" --den "1,14,56,160"   --tfinal 2.0 --dt 0.01   --out-prefix "tf2ss_demo"
```
This will save a file:
```
stateSpaceAnalysis/converterTool/out/tf2ss_demo_tf_step.png
```

---

## 2) SS → TF

### A) SISO SS→TF (explicit D)
```bash
python -m stateSpaceAnalysis.converterTool.cli   --A "0 1 0; 0 0 1; -5 -25 -5"   --B "0; 25; -120"   --C "1 0 0"   --D "0"   --no-plot
```

### B) SISO SS→TF (D omitted → auto zeros)
```bash
python -m stateSpaceAnalysis.converterTool.cli   --A "0 1; -1 -1"   --B "0; 1"   --C "1 0"   --no-plot
```

### C) SS→TF with step plots saved
```bash
python -m stateSpaceAnalysis.converterTool.cli   --A "0 1; -1 -1"   --B "0; 1"   --C "1 0"   --D "0"   --tfinal 1.0 --dt 0.02   --out-prefix "ss2tf_demo"
```
This will save a file:
```
stateSpaceAnalysis/converterTool/out/ss2tf_demo_ss_step.png
```

### D) MIMO SS→TF, step on chosen input `--iu`
System: 2×2 MIMO with 2 states. Step the **first** input (`--iu 0`) and plot both outputs.
```bash
python -m stateSpaceAnalysis.converterTool.cli   --A "-1 -1; 6.5 0"   --B "1 1; 1 0"   --C "1 0; 0 1"   --D "0 0; 0 0"   --iu 0 --tfinal 1.0 --dt 0.01   --out-prefix "mimo_demo"
```
Saves:
```
stateSpaceAnalysis/converterTool/out/mimo_demo_ss_step.png
```

---

## 3) TF + SS together (cross-check equivalence)

When both TF and SS are provided, the app prints both conversions and attempts a SISO equivalence check (numerator/denominator match, up to scale).

### A) Provide TF and SS (SISO), no plot
```bash
python -m stateSpaceAnalysis.converterTool.cli   --num "1,0" --den "1,1,1"   --A "0 1; -1 -1"   --B "0; 1"   --C "1 0"   --D "0"   --no-plot --log INFO
```

### B) Same, with saved plots
```bash
python -m stateSpaceAnalysis.converterTool.cli   --num "1,0" --den "1,1,1"   --A "0 1; -1 -1"   --B "0; 1"   --C "1 0"   --D "0"   --tfinal 1.0 --dt 0.02   --out-prefix "both_demo"
```
Saves:
```
stateSpaceAnalysis/converterTool/out/both_demo_tf_step.png
stateSpaceAnalysis/converterTool/out/both_demo_ss_step.png
```

---

## 4) Quality-of-life & diagnostics

### A) Silent plotting (skip plots)
```bash
python -m stateSpaceAnalysis.converterTool.cli   --num "1,0" --den "1,14,56,160"   --no-plot
```

### B) Logging level (DEBUG for extra internals)
```bash
python -m stateSpaceAnalysis.converterTool.cli   --num "1,0" --den "1,14,56,160"   --no-plot --log DEBUG
```

### C) Short-step test (fast render)
```bash
python -m stateSpaceAnalysis.converterTool.cli   --A "0 1; -1 -1" --B "0; 1" --C "1 0" --D "0"   --tfinal 0.1 --dt 0.05   --out-prefix "quick_ss"
```

---

## 5) Notes

- **Matrices**: rows separated by `;`, elements by space or commas. Examples:  
  `--A "0 1; -1 -1"` or `--A "0,1; -1,-1"`
- **Indexing**: `--iu` is **0-based**.
- **SymPy**: `--sympy` enables rational pretty-print for SISO TFs. If SymPy isn’t installed, a fallback message prints.
- **Outputs**: files are written under `stateSpaceAnalysis/converterTool/out/` when `--out-prefix` is provided.

Happy converting! 🚀
