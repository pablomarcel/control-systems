# stateSpaceDesign.regulatorTool — OOP Refactor

Run commands (from your repo root):

```bash
python -m stateSpaceDesign.regulatorTool.cli \
  --num "10 20" --den "1 10 24 0" \
  --K_poles "-1+2j,-1-2j,-5" --obs_poles "-10,-10" \
  --x0 "1 0 0" --e0 "1 0" \
  --pretty --plots both --save_prefix sys_explicit
```

```bash
python -m stateSpaceDesign.regulatorTool.cli \
  --num "10 20" --den "1 10 24 0" \
  --K_poles "-1+2j,-1-2j,-5" --obs_poles "-4.5,-4.5" \
  --x0 "1 0 0" --e0 "1 0" \
  --pretty --plots both --save_prefix sys_second
```

```bash
python -m stateSpaceDesign.regulatorTool.cli \
  --num "10 20" --den "1 10 24 0" \
  --ts 4.0 --undershoot "0.25,0.35" --obs_speed_factor 5 \
  --x0 "1 0 0" --e0 "1 0" \
  --pretty --plots mpl --save_prefix sys_auto_mpl
```

```bash
python -m stateSpaceDesign.regulatorTool.cli \
  --num "10 20" --den "1 10 24 0" \
  --ts 4.0 --undershoot "0.25,0.35" --obs_speed_factor 5 \
  --x0 "1 0 0" --e0 "1 0" \
  --pretty --plots plotly --save_prefix sys_auto_ply
```

```bash
python -m stateSpaceDesign.regulatorTool.cli \
  --num "10 20" --den "1 10 24 0" \
  --K_poles "-1+2j,-1-2j,-5" --obs_poles "-4.5,-4.5" \
  --x0 "1 0 0" --e0 "1 0" \
  --plots mpl --rl_axes "-20,5,-12,12"
```
