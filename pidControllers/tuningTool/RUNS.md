# RUNS — tuningTool (run from inside `pidControllers/tuningTool/`)

Each command below is in its **own** bash block. Run with:
- `cd modernControl/pidControllers/tuningTool`
- `python cli.py ...`

Exports go to `./out/`. Rules are read from `./in/` by default.

---

## 0) Help / sanity
```bash
python cli.py --help
```

## 1) Discover what’s in your rules JSON

```bash
python cli.py --file tuning_rules.json --list methods
```

```bash
python cli.py --file tuning_rules.json --method ZN_step --list controllers
```

```bash
python cli.py --file tuning_rules.json --method ZN_ultimate --list formulas
```

## 2) Ziegler–Nichols First Method (reaction-curve / step-response)

```bash
python cli.py --file tuning_rules.json --method ZN_step --controller P --L 0.8 --T 3.0
```

```bash
python cli.py --file tuning_rules.json --method ZN_step --controller PI --L 0.8 --T 3.0
```

```bash
python cli.py --file tuning_rules.json --method ZN_step --controller PID --L 0.8 --T 3.0
```

### 2a) Export results (JSON / CSV → `./out/`)

```bash
python cli.py --file tuning_rules.json --method ZN_step --controller PID --L 0.8 --T 3.0 --export-json zn_step_pid_L0p8_T3p0.json
```

```bash
python cli.py --file tuning_rules.json --method ZN_step --controller PID --L 0.8 --T 3.0 --export-csv zn_step_pid_L0p8_T3p0.csv
```

```bash
python cli.py --file tuning_rules.json --method ZN_step --controller PI --L 0.6 --T 2.5 --export-json zn_step_pi_L0p6_T2p5.json --export-csv zn_step_pi_L0p6_T2p5.csv
```

### 2b) Pretty print with custom precision

```bash
python cli.py --file tuning_rules.json --method ZN_step --controller PID --L 0.8 --T 3.0 --precision 4
```

## 3) Ziegler–Nichols Second Method (ultimate gain / sustained oscillation)

```bash
python cli.py --file tuning_rules.json --method ZN_ultimate --controller P --Kcr 7.5 --Pcr 2.2
```

```bash
python cli.py --file tuning_rules.json --method ZN_ultimate --controller PI --Kcr 7.5 --Pcr 2.2
```

```bash
python cli.py --file tuning_rules.json --method ZN_ultimate --controller PID --Kcr 7.5 --Pcr 2.2
```

### 3a) Export results (JSON / CSV)

```bash
python cli.py --file tuning_rules.json --method ZN_ultimate --controller PID --Kcr 6.2 --Pcr 1.9 --export-json zn_ult_pid_K6p2_P1p9.json --export-csv zn_ult_pid_K6p2_P1p9.csv
```

## 4) Use **Cohen–Coon** (alternate rules file in `./in/`)

```bash
python cli.py --file tuning_rules_cohen_coon.json --list methods
```

```bash
python cli.py --file tuning_rules_cohen_coon.json --method CC_step --controller PID --L 0.8 --T 3.0 --export-json cc_step_pid_L0p8_T3p0.json
```

## 5) Minimal smoke (no exports)

```bash
python cli.py --file tuning_rules.json --method ZN_step --controller PID --L 1.0 --T 2.5
```

```bash
python cli.py --file tuning_rules.json --method ZN_ultimate --controller PI --Kcr 8.0 --Pcr 2.0
```

## 6) Typical validation error (shows required inputs)

```bash
python cli.py --file tuning_rules.json --method ZN_step --controller PID
```
