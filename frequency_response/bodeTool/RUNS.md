# frequencyResponse / bodeTool — Runbook (in-package)

This markdown lets you run everything **from inside the package**.

## How to use
1) Open a terminal at your repo root, then:
```bash
cd frequency_response/bodeTool
```
2) Run any of the commands below directly with `python cli.py ...`

> The CLI now has an import shim, so running `python cli.py` here works the same as
> `python -m frequencyResponse.bodeTool.cli` from the repo root.

---

## 0) Quick sanity check
```bash
python cli.py -h
```

## 1) Basic Bode with margins (Matplotlib)
```bash
python cli.py --num 1 --den "1, 0.8, 1" --bode
```

## 2) Interactive Plotly Bode + HTML export
```bash
python cli.py --num 1 --den "1, 0.8, 1" --bode --plotly --save-html ./out/bode.html
```

## 3) Bode + Nyquist + Nichols; autoscaled grid; save PNGs
```bash
python cli.py --num 1 --den "1, 0.8, 1" --bode --nyquist --nichols --save-png ./out
```

## 4) Provide H(s) (non-unity feedback), coefficient mode
```bash
python cli.py --num 10 --den "0.2, 1.2, 1" --hnum 1 --hden 1 --bode
```

## 5) Manual frequency span + npts
```bash
python cli.py --num 1 --den "1, 0.8, 1" --bode --wmin 0.2 --wmax 10 --npts 2000
```

## 6) JSON numeric report
```bash
python cli.py --num 1 --den "1, 0.8, 1" --bode --save-json ./out/report.json
```

## 7) With closed-loop step response
```bash
python cli.py --num 20 --den "1, 1, 0" --bode --step
```

## 8) “Large” plant + H(s); export everything
```bash
python cli.py --num 40 --den "1, 0, 0" --hnum 1 --hden "1, 2" --bode --nyquist --nichols --step --save-png ./out --save-json ./out/results.json
```

## 9) 2nd-order + Nyquist + Nichols + step + exports
```bash
python cli.py --num 1 --den "1, 0.8, 1" --bode --nyquist --nichols --step --save-png ./out --save-json ./out/report.json
```

## 10) Zeros/Poles/Gain (complex zeros supported)
```bash
python cli.py --gain 5 --zeros "0.5, -1, 2+3j, 2-3j" --poles "-0.2, -2, -10" --bode --nyquist
```

## 11) Factorized G(s) with symbolic K
```bash
python cli.py --fnum "K (s+1)" --fden "s (s+5) (s+10)" --K 4.2 --bode --save-json ./out/factored.json
```

## 12) Factorized H(s) (measurement lag) + Plotly
```bash
python cli.py --fnum "(s+2)" --fden "s (s+1)" --hfnum "1" --hfden "(s/20 + 1)" --bode --plotly --save-html ./out/factored_bode.html
```

## 13) Dense grid + single PNG file + custom title
```bash
python cli.py --num 1 --den "1, 0.8, 1" --npts 4000 --bode --title "Bode — ζ≈0.4 style plant" --save-png ./out/bode_only.png
```

## 14) Nichols-only quick look
```bash
python cli.py --num 1 --den "1, 0.8, 1" --nichols
```

## 15) Nyquist-only + JSON for CI checks
```bash
python cli.py --num 1 --den "1, 0.8, 1" --nyquist --save-json ./out/nyquist_check.json
```

## 16) Unity loop with explicit breakpoints using time constants (supported)
```bash
python cli.py --fnum "1" --fden "(s/0.5 + 1) (s/5 + 1) (s/50 + 1)" --wmin 0.05 --wmax 500 --npts 3000 --bode --nyquist
```

## 17) Lead-ish plant (zero before pole), margins + step (supported)
```bash
python cli.py --fnum "(s/3 + 1)" --fden "s (s/30 + 1)" --bode --step --save-json ./out/leadish.json
```

## 18) Non-unity H(s) via zeros/poles (measurement pole at −20 rad/s)
```bash
python cli.py --fnum "10" --fden "s (s/5 + 1) (s/50 + 1)" --hgain 1 --hpoles "-20" --bode --nyquist --save-png ./out
```

---

### Notes
- Paths in this doc assume you are inside `frequencyResponse/bodeTool/` and use `../out` for outputs.
- To revert to the old style (run from repo root): `python -m frequencyResponse.bodeTool.cli ...`

### Sphinx

python -m frequency_response.bodeTool.cli sphinx-skel frequency_response/bodeTool/docs
python -m sphinx -b html docs docs/_build/html
open docs/_build/html/index.html
sphinx-autobuild docs docs/_build/html