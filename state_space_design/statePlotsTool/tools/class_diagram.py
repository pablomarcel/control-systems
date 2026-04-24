# SPDX-License-Identifier: MIT
"""Generate a simple class diagram using graphviz (if available)."""
from __future__ import annotations
from pathlib import Path

def generate_class_diagram(out_path: str | Path) -> Path:
    try:
        from graphviz import Digraph
    except Exception as e:
        raise RuntimeError(f'graphviz not available: {e}')
    dot = Digraph('statePlotsTool', format='png')
    # nodes
    dot.node('RunRequest')
    dot.node('StatePlotsAPI')
    dot.node('StatePlotsApp')
    dot.node('Simulator')
    dot.node('ClosedLoopBuilder')
    dot.node('CSVExporter')
    dot.node('PlotBackend')
    # edges
    dot.edge('StatePlotsApp', 'StatePlotsAPI')
    dot.edge('StatePlotsAPI', 'RunRequest')
    dot.edge('StatePlotsAPI', 'Simulator')
    dot.edge('Simulator', 'ClosedLoopBuilder')
    dot.edge('StatePlotsAPI', 'CSVExporter')
    dot.edge('StatePlotsAPI', 'PlotBackend')
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    dot.render(out_path.with_suffix(''), cleanup=True)
    return out_path.with_suffix('.png')
