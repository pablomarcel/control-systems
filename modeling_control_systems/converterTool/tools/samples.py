
#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json

def main():
    Path("in").mkdir(exist_ok=True)
    (Path("in") / "tf_siso.json").write_text(json.dumps({"num":[1,0], "den":[1,14,56,160]}, indent=2))
    (Path("in") / "ss_siso.json").write_text(json.dumps({
        "A": [[0,1,0],[0,0,1],[-5,-25,-5]],
        "B": [[0],[25],[-120]],
        "C": [[1,0,0]],
        "D": [[0]]
    }, indent=2))
    print("Wrote: in/tf_siso.json, in/ss_siso.json")

if __name__ == "__main__":
    main()
