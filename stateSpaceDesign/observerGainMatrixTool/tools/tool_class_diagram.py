from __future__ import annotations
from pathlib import Path

MERMAID = """classDiagram
    class ObserverGainMatrixApp {
      +run(req: ObserverRequest) ObserverResponse
    }

    class ObserverRequest {
      +A: str
      +B: Optional[str]
      +C: str
      +poles: List[complex]
      +method: str
      +place_fallback: str
      +jitter_eps: float
      +K: Optional[str]
      +K_poles_csv: Optional[str]
      +K_poles_list: Optional[List[str]]
      +compute_closed_loop: bool
      +x0: Optional[str]
      +e0: Optional[str]
      +t_final: float
      +dt: float
      +pretty: bool
      +equations: bool
      +eq_style: str
      +latex_out: Optional[str]
    }

    class ObserverResponse {
      +data: Dict[str, Any]
      +pretty_blocks: List[str]
    }

    class ObserverDesigner {
      +compute(A,C,poles,method,place_fallback,jitter_eps) ObserverDesignResult
    }

    class ControllerDesigner {
      +compute_place(A,B,poles) np.ndarray
    }

    class OutputManager {
      +write_json(data, filename) Path
      +write_text(text, filename) Path
    }

    ObserverGainMatrixApp --> ObserverRequest
    ObserverGainMatrixApp --> ObserverResponse
    ObserverGainMatrixApp --> ObserverDesigner
    ObserverGainMatrixApp --> ControllerDesigner
    ObserverGainMatrixApp --> OutputManager
"""

def write_mermaid(path: str = "stateSpaceDesign/observerGainMatrixTool/out/observerGainMatrixTool.mmd") -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(MERMAID, encoding="utf-8")
    return str(p)
