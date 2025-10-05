# stateSpaceDesign.servoTool — OOP Servo I/O Builder

Refactor of `servos.py` into a clean, testable OOP package.

## Run (from repo root)
```bash
python -m stateSpaceDesign.servoTool.cli --help
```

### K mode (plant already type-1; provide C if missing in JSON)
```bash
python -m stateSpaceDesign.servoTool.cli   --data stateSpaceDesign/servoTool/in/K_controller.json   --C "1 0 0"   --r 1   --export_json k_mode_io.json   --t "0:0.01:5"   --save_csv k_mode_step.csv   --backend none
```

### KI mode (type-0 + added integrator; C, K, kI must be in JSON)
```bash
python -m stateSpaceDesign.servoTool.cli   --data stateSpaceDesign/servoTool/in/KI_controller.json   --r 1   --export_json ki_mode_io.json   --t "0:0.01:5"   --save_csv ki_mode_step.csv   --backend none
```

Outputs are written to `stateSpaceDesign/servoTool/out/`.
