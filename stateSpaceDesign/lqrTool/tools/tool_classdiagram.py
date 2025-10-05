#!/usr/bin/env python3
"""Generate a simple Graphviz DOT class diagram for lqrTool.

Usage:
  python -m stateSpaceDesign.lqrTool.tools.tool_classdiagram --out stateSpaceDesign/lqrTool/out/lqrTool.dot
Then render with:
  dot -Tpng stateSpaceDesign/lqrTool/out/lqrTool.dot -o stateSpaceDesign/lqrTool/out/lqrTool.png
"""
from __future__ import annotations
import argparse
import os

DOT = r"""digraph LQRTool {
  rankdir=LR;
  node [shape=record, style=rounded];

  StateSpaceModel [label="{StateSpaceModel|+A: ndarray\l+B: ndarray\l+C: ndarray\l+D: ndarray\l|+as_control(): StateSpace\l+n,m,p}"];
  LQRDesigner [label="{LQRDesigner|+model: StateSpaceModel|+design(Q,R): LQRDesignResult\l+prefilter(K,mode,C): float}"];
  Simulator [label="{Simulator|+initial(...) : Trajectory\l+forced_step(...) : Trajectory}"];
  LQRApp [label="{LQRApp|+req: LQRRunRequest|+build_model(): StateSpaceModel\l+run(): LQRRunResult}"];
  LQRRunRequest [label="{LQRRunRequest|...}"];
  LQRRunResult [label="{LQRRunResult|...}"];

  LQRApp -> StateSpaceModel [label="build_model()"];
  LQRApp -> LQRDesigner [label="uses"];
  LQRDesigner -> StateSpaceModel;
  Simulator -> StateSpaceModel [style=dashed, label="reads"];
}
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="stateSpaceDesign/lqrTool/out/lqrTool.dot")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(DOT)
    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
