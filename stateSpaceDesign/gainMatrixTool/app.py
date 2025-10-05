from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import logging, sys, os
from .apis import GainMatrixAPI

@dataclass
class GainMatrixApp:
    api: GainMatrixAPI

    @classmethod
    def default(cls):
        return cls(api=GainMatrixAPI.default())

    def configure_logging(self, log_path: str|None, verbose: bool):
        handlers = [logging.StreamHandler(sys.stdout)]
        if log_path:
            handlers.append(logging.FileHandler(log_path))
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            handlers=handlers
        )

    def run_single(self, **kwargs):
        return self.api.single(**kwargs)

    def run_batch(self, csv: str|None, yaml: str|None, export_dir: str, verify: bool, pretty: bool):
        assert csv or yaml
        if csv:
            cases = self.api.io_reader.from_csv(csv)
        else:
            cases = self.api.io_reader.from_yaml(yaml)
        self.api.batch(cases, export_dir, verify, pretty)
