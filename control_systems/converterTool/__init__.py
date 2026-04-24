
# modernControl.control_systems.converterTool
"""System Converter Tool — TF <-> SS conversions, pretty-print, and plotting.

Package layout:
  - app.py     : Application orchestration (logging, run pipeline, rendering)
  - apis.py    : Public dataclasses and programmatic API surface
  - core.py    : Domain objects (TFModel, SSModel) and ConverterEngine
  - design.py  : Pretty-print helpers, plotting helpers
  - io.py      : Parsers, normalizers, JSON/CSV I/O conveniences
  - utils.py   : Misc utilities
  - cli.py     : End-user CLI (argparse) + Sphinx skeleton helper (sphinx-skel)
  - tools/     : Extra utilities (class diagram, sample generators)
  - tests/     : Pytest-based TDD scaffolding (no heavy deps)
"""
from .apis import ConverterConfig, ConverterResult, convert_tf_to_ss, convert_ss_to_tf
