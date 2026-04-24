from __future__ import annotations
import logging
from .apis import StateTransRequest
from .design import StateTransApp
from .io import export_json_phi, format_matrix

def run(req: StateTransRequest) -> str:
    """Run the app and return a human-readable report string."""
    logging.basicConfig(level=getattr(logging, req.log_level.upper(), logging.INFO),
                        format="%(levelname)s: %(message)s")
    app = StateTransApp(req)
    res = app.run()

    report_lines = []
    report_lines.append(f"== State-Transition Matrix for A ({req.canonical}) ==")

    if req.eval_time is not None:
        report_lines.append(f"Φ({req.eval_time}) =\n{format_matrix(res.Phi_eval, numeric=req.numeric, digits=req.digits, pretty=req.pretty)}")
        if res.Phi_inv is not None and res.Phi_inv_eval is not None:
            report_lines.append(f"\nΦ^(-1)({req.eval_time}) =\n{format_matrix(res.Phi_inv_eval, numeric=req.numeric, digits=req.digits, pretty=req.pretty)}")
    else:
        report_lines.append(f"Φ(t) =\n{format_matrix(res.Phi, numeric=False, pretty=req.pretty)}")
        if res.Phi_inv is not None:
            report_lines.append(f"\nΦ^(-1)(t) =\n{format_matrix(res.Phi_inv, numeric=False, pretty=req.pretty)}")

    if req.export_json:
        path = export_json_phi(req.export_json, res.Phi, res.Phi_inv)
        report_lines.append(f"\nSaved JSON to: {path}")

    return "\n".join(report_lines)
