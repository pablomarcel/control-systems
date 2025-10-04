"""
Extra plotting helpers (placeholder for future scale).
"""
from __future__ import annotations
import matplotlib.pyplot as plt

def figure(title: str | None = None):
    fig = plt.figure()
    if title:
        fig.suptitle(title)
    return fig
