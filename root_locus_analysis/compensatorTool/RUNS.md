 # rootLocus / compensatorTool — Runbook (inside‑package)

> Run these from **inside the package directory**:
>
> ```bash
> cd root_locus_analysis/compensatorTool
 > python cli.py --help
 > ```

 ---

 ## 1) Lag‑only — quick auto design (size β from `--factor`, auto z,p near origin)
 ```bash
 python cli.py lag       --num "1"       --den "1, 2, 0"       --zeta 0.45 --wn 1.8       --err kv --factor 10 --thetamax 5
 ```

 ## 2) Lag‑only — manual β and T (use z=1/T, p=1/(βT))
 ```bash
 python cli.py lag       --num "1"       --den "1, 2, 0"       --zeta 0.45 --wn 1.8       --beta 8 --T 2.0
 ```

 ## 3) Lead‑only — Method 1 (bisector)
 ```bash
 python cli.py lead       --num "1"       --den "1, 2, 0"       --zeta 0.45 --wn 1.8       --method 1
 ```

 ## 4) Lead‑only — Method 2 (cancel a real plant pole at s = −1)
 ```bash
 python cli.py lead       --num "1"       --den "1, 2, 1"       --zeta 0.5 --wn 2.0       --method 2 --cancel-at 1.0
 ```

 ## 5) Multi‑lead design — independent sizing, two leads, locus + step plots
 ```bash
 python cli.py design       --num "4"       --den "1, 2, 0"       --zeta 0.45 --wn 1.8       --case indep       --nlead 2 --phi-per-lead 28 --phi-cap 60       --err kv --factor 12       --plot locus --plot step -v
 ```

 ## 6) Multi‑lead design — manual lead tuple (T1, γ)
 ```bash
python cli.py design \
  --num "1" \
  --den "1, 1, 0" \
  --sreal -0.9 --wimag 1.5 \
  --lead-method manual --T1 0.8 --gamma 4.0 \
  --err kv --target 2.0 \
  --plot locus
 ```

 ## 7) Parallel compensation — build F from blocks (G1 → G2 in series, H feedback)
 ```bash
 python cli.py parallel       --g1-num "1" --g1-den "1, 1"       --g2-num "1" --g2-den "0.5, 1"       --h-num "1" --h-den "1"       --zeta 0.5 --wn 2.0       --plot locus --k-pts 400
 ```

 ## 8) Parallel compensation — direct F(s); Plotly HTML exports for locus & step
 ```bash
 python cli.py parallel       --F-num "1, 1.2" --F-den "1, 3, 2"       --sreal -1.0 --wimag 1.8       --plot locus --plot step       --plotly-locus "out/parallel_locus.html"       --plotly-step  "out/parallel_step.html"
 ```

 ## 9) Parallel compensation — A + K·B split and explicit K sweep on locus
 ```bash
 python cli.py parallel       --A-num "1, 2, 0"       --B-num "4"       --zeta 0.45 --wn 1.8       --plot locus --k-range "0,200" --k-pts 600
 ```

 ---

 ### Notes
 * Coefficient lists accept commas or semicolons; spaces are ignored (e.g., `"1,2,0"` or `"1; 2; 0"`).
 * All commands write artifacts (when applicable) to `rootLocus/compensatorTool/out/`.
 * Use `-v` or `-vv` for more logging detail.
 * For Plotly HTML, pass `--plotly-locus` / `--plotly-step` with output paths (they'll be created).
