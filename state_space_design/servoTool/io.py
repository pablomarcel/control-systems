from __future__ import annotations
import json, os
import numpy as np
from .core import ControllerPayload, ServoMode

PKG_ROOT = os.path.dirname(__file__)
IN_DIR  = os.path.join(PKG_ROOT, "in")
OUT_DIR = os.path.join(PKG_ROOT, "out")

def ensure_out_path(name: str | None, default_name: str) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    base = os.path.basename(name) if name else default_name
    return os.path.join(OUT_DIR, base)

def load_controller_json(path: str) -> ControllerPayload:
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    mode = str(payload.get("mode", "K")).upper()
    cp = ControllerPayload(
        mode=ServoMode(mode),
        A=np.array(payload["A"], dtype=float),
        B=np.array(payload["B"], dtype=float),
        C=np.array(payload.get("C")) if "C" in payload else None,
        K=np.array(payload.get("K")) if "K" in payload else None,
        kI=float(payload.get("kI")) if "kI" in payload else None,
        state_names=list(payload.get("state_names", [])) or None,
        output_names=list(payload.get("output_names", [])) or None,
    )
    return cp

def save_io_json(path: str, io_payload: dict) -> str:
    out_path = ensure_out_path(path, "servo_io.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(io_payload, f, indent=2)
    return out_path

def save_csv(path: str, T, Y, header: str = "t,y") -> str:
    import numpy as np
    out_path = ensure_out_path(path, "servo_step.csv")
    M = np.column_stack([T, Y])
    np.savetxt(out_path, M, delimiter=",", header=header, comments="")
    return out_path
