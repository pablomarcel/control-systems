
from __future__ import annotations
"""Minimal sanity runner to print poles for both plants."""
from . import __package__ as _pkg  # noqa
from ..core import MIMOPlantBuilder, MIMOAnalyzer

def main():
    for name, fn in {"two_tank": MIMOPlantBuilder.two_tank, "two_zone_thermal": MIMOPlantBuilder.two_zone_thermal}.items():
        sys = fn()
        print(name, "poles:", MIMOAnalyzer.poles(sys))

if __name__ == "__main__":
    main()
