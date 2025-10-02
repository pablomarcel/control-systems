# frequencyResponse / bodeTool — Runbook

This markdown is a **click-to-run** cookbook for the `bodeTool` CLI.
All commands assume you run them **from the repo root** (`modernControl/`).

> Tip (macOS): if plot windows don’t appear, ensure Python is allowed to create windows
> and that you’re not running within a fully headless shell. The tool auto-selects
> an interactive Matplotlib backend on macOS/Linux when possible.

---

## 0) Quick sanity check
```bash
python -m frequencyResponse.bodeTool.cli -h
```

---

## 1) Basic Bode with margins (Matplotlib)
```bash
python -m frequencyResponse.bodeTool.cli --num 1 --den "1, 0.8, 1" --bode
```

## 2) Interactive Plotly Bode + HTML export
```bash
python -m frequencyResponse.bodeTool.cli --num 1 --den "1, 0.8, 1"   --bode --plotly --save-html frequencyResponse/bodeTool/out/bode.html
```

## 3) Bode + Nyquist + Nichols; autoscaled grid; save PNGs
```bash
python -m frequencyResponse.bodeTool.cli --num 1 --den "1, 0.8, 1"   --bode --nyquist --nichols --save-png frequencyResponse/bodeTool/out
```

## 4) Provide H(s) (non-unity feedback), coefficient mode
```bash
python -m frequencyResponse.bodeTool.cli --num 10 --den "0.2, 1.2, 1"   --hnum 1 --hden 1 --bode
```

## 5) Manual frequency span + npts
```bash
python -m frequencyResponse.bodeTool.cli --num 1 --den "1, 0.8, 1"   --bode --wmin 0.2 --wmax 10 --npts 2000
```

## 6) JSON numeric report
```bash
python -m frequencyResponse.bodeTool.cli --num 1 --den "1, 0.8, 1"   --bode --save-json frequencyResponse/bodeTool/out/report.json
```

## 7) With closed-loop step response
```bash
python -m frequencyResponse.bodeTool.cli --num 20 --den "1, 1, 0"   --bode --step
```

## 8) “Large” plant + H(s); export everything
```bash
python -m frequencyResponse.bodeTool.cli   --num 40 --den "1, 0, 0"   --hnum 1 --hden "1, 2"   --bode --nyquist --nichols --step   --save-png frequencyResponse/bodeTool/out   --save-json frequencyResponse/bodeTool/out/results.json
```

## 9) 2nd-order + Nyquist + Nichols + step + exports
```bash
python -m frequencyResponse.bodeTool.cli --num 1 --den "1, 0.8, 1"   --bode --nyquist --nichols --step   --save-png frequencyResponse/bodeTool/out   --save-json frequencyResponse/bodeTool/out/report.json
```

## 10) Zeros/Poles/Gain (complex zeros supported)
```bash
python -m frequencyResponse.bodeTool.cli   --gain 5 --zeros "0.5, -1, 2+3j, 2-3j" --poles "-0.2, -2, -10"   --bode --nyquist
```

## 11) Factorized G(s) with symbolic K
```bash
python -m frequencyResponse.bodeTool.cli   --fnum "K (s+1)" --fden "s (s+5) (s+10)" --K 4.2   --bode --save-json frequencyResponse/bodeTool/out/factored.json
```

## 12) Factorized H(s) (measurement lag) + Plotly
```bash
python -m frequencyResponse.bodeTool.cli   --fnum "(s+2)" --fden "s (s+1)"   --hfnum "1" --hfden "(s/20 + 1)"   --bode --plotly --save-html frequencyResponse/bodeTool/out/factored_bode.html
```

## 13) Dense grid + single PNG file + custom title
```bash
python -m frequencyResponse.bodeTool.cli   --num 1 --den "1, 0.8, 1" --npts 4000   --bode --title "Bode — ζ≈0.4 style plant"   --save-png frequencyResponse/bodeTool/out/bode_only.png
```

## 14) Nichols-only quick look
```bash
python -m frequencyResponse.bodeTool.cli --num 1 --den "1, 0.8, 1" --nichols
```

## 15) Nyquist-only + JSON for CI checks
```bash
python -m frequencyResponse.bodeTool.cli   --num 1 --den "1, 0.8, 1" --nyquist   --save-json frequencyResponse/bodeTool/out/nyquist_check.json
```

## 16) Unity loop with explicit breakpoints using time constants (supported)
```bash
python -m frequencyResponse.bodeTool.cli   --fnum "1" --fden "(s/0.5 + 1) (s/5 + 1) (s/50 + 1)"   --wmin 0.05 --wmax 500 --npts 3000   --bode --nyquist
```

## 17) Lead-ish plant (zero before pole), margins + step (supported)
```bash
python -m frequencyResponse.bodeTool.cli   --fnum "(s/3 + 1)" --fden "s (s/30 + 1)"   --bode --step --save-json frequencyResponse/bodeTool/out/leadish.json
```

## 18) Non-unity H(s) via zeros/poles (measurement pole at −20 rad/s)
```bash
python -m frequencyResponse.bodeTool.cli   --fnum "10" --fden "s (s/5 + 1) (s/50 + 1)"   --hgain 1 --hpoles "-20"   --bode --nyquist --save-png frequencyResponse/bodeTool/out
```

---

## Troubleshooting

- **Plots not showing (macOS):** a non-interactive backend might be selected. The tool tries `MacOSX` automatically; if it still fails, try running from a normal Terminal app (not fully headless) or set `MPLBACKEND=MacOSX`.
- **Headless CI:** set `MPLBACKEND=Agg` to save images without opening windows.
- **Deprecation warnings:** the tool prefers `control.frequency_response()` and falls back to `freqresp()` if needed.
