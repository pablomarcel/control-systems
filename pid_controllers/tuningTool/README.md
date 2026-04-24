# README — pidControllers.tuningTool Run Commands (Project Root)

Run these from the **repo root** (`modernControl/`).  
**Entrypoint:** `python -m pidControllers.tuningTool.cli`  
**I/O:** Rules live in `pidControllers/tuningTool/in/`, exports go to `pidControllers/tuningTool/out/`.

> **Important path rule**  
> The CLI resolves `--file` **relative to** `pidControllers/tuningTool/in/`.  
> - To use the default Ogata ZN rules, either **omit `--file`** or pass **`--file tuning_rules.json`**.  
> - To use Cohen–Coon (or any other), pass just the **filename**, e.g. **`--file tuning_rules_cohen_coon.json`**.  
> - If you pass an **absolute path**, it will be used as-is.

---

## 0) Help / sanity

```bash
python -m pid_controllers.tuningTool.cli --help
```

## 1) Discover what’s in your rules JSON

```bash
# List methods in the default ZN file
python -m pid_controllers.tuningTool.cli --file tuning_rules.json --list methods
```

```bash
# List controllers for a given method
python -m pid_controllers.tuningTool.cli --file tuning_rules.json --method ZN_step --list controllers
```

```bash
# List raw formulas (Kp, Ti, Td) for a method
python -m pid_controllers.tuningTool.cli --file tuning_rules.json --method ZN_ultimate --list formulas
```

## 2) Ziegler–Nichols First Method (reaction-curve / step-response)
Requires **L** and **T**.

```bash
# P
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_step --controller P --L 0.8 --T 3.0
```

```bash
# PI
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_step --controller PI --L 0.8 --T 3.0
```

```bash
# PID (prints implied controller zeros if present)
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_step --controller PID --L 0.8 --T 3.0
```

### 2a) Export results (JSON / CSV → `pidControllers/tuningTool/out/`)

```bash
# JSON export
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_step --controller PID --L 0.8 --T 3.0   --export-json zn_step_pid_L0p8_T3p0.json
```

```bash
# CSV export
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_step --controller PID --L 0.8 --T 3.0   --export-csv zn_step_pid_L0p8_T3p0.csv
```

```bash
# Both at once
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_step --controller PI --L 0.6 --T 2.5   --export-json zn_step_pi_L0p6_T2p5.json   --export-csv  zn_step_pi_L0p6_T2p5.csv
```

### 2b) Pretty print with custom precision

```bash
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_step --controller PID --L 0.8 --T 3.0 --precision 4
```

## 3) Ziegler–Nichols Second Method (ultimate gain / sustained oscillation)
Requires **Kcr** and **Pcr**.

```bash
# P
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_ultimate --controller P --Kcr 7.5 --Pcr 2.2
```

```bash
# PI
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_ultimate --controller PI --Kcr 7.5 --Pcr 2.2
```

```bash
# PID (prints implied zeros if specified in JSON)
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_ultimate --controller PID --Kcr 7.5 --Pcr 2.2
```

### 3a) Export results (JSON / CSV)

```bash
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_ultimate --controller PID --Kcr 6.2 --Pcr 1.9   --export-json zn_ult_pid_K6p2_P1p9.json   --export-csv  zn_ult_pid_K6p2_P1p9.csv
```

## 4) Use **Cohen–Coon** (or any alternate rules file)
Place your file in `pidControllers/tuningTool/in/` and pass only the **filename**.

```bash
# Discover methods in Cohen–Coon
python -m pid_controllers.tuningTool.cli --file tuning_rules_cohen_coon.json --list methods
```

```bash
# Example compute (keys depend on your JSON)
python -m pid_controllers.tuningTool.cli --file tuning_rules_cohen_coon.json   --method CC_step --controller PID --L 0.8 --T 3.0   --export-json cc_step_pid_L0p8_T3p0.json
```

## 5) Minimal smoke (no exports)

```bash
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_step --controller PID --L 1.0 --T 2.5
```

```bash
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_ultimate --controller PI --Kcr 8.0 --Pcr 2.0
```

## 6) Typical validation error (shows required inputs)
```bash
# Missing L/T for ZN_step → prints which inputs are required
python -m pid_controllers.tuningTool.cli --file tuning_rules.json   --method ZN_step --controller PID
```
