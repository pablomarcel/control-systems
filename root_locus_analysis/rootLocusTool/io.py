from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any, List
import os

@dataclass(slots=True)
class OutputSpec:
    out_dir: str = "."
    html: Optional[str] = "root_locus.html"
    png: Optional[str] = None
    csv: Optional[str] = None

    def resolve(self, title: str) -> Tuple[str, Optional[str], Optional[str]]:
        base = os.path.join(self.out_dir, title)
        html = self.html if os.path.isabs(self.html or "") else os.path.join(self.out_dir, self.html or "")
        png  = self.png  if (self.png and os.path.isabs(self.png)) else (os.path.join(self.out_dir, self.png) if self.png else None)
        csv  = self.csv  if (self.csv and os.path.isabs(self.csv)) else (os.path.join(self.out_dir, self.csv) if self.csv else None)
        return html, png, csv

def ensure_outdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
