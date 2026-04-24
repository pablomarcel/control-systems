
#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

DOT = """digraph G {
  rankdir=LR;
  node [shape=record];
  TFModel [label="{TFModel|+ num: ndarray\\\l+ den: ndarray\\\l}"];
  SSModel [label="{SSModel|+ A: ndarray\\\l+ B: ndarray\\\l+ C: ndarray\\\l+ D: ndarray\\\l}"];
  ConverterEngine [label="{ConverterEngine|+ tf_to_ss()\\\l+ ss_to_tf()\\\l}"];
  ConverterApp [label="{ConverterApp|+ run(cfg)\\l}"];
  ConverterConfig [label="{ConverterConfig|...}"];
  ConverterResult [label="{ConverterResult|...}"];
  TFModel -> ConverterEngine [label="input"];
  SSModel -> ConverterEngine [label="input"];
  ConverterEngine -> TFModel [label="returns"];
  ConverterEngine -> SSModel [label="returns"];
  ConverterApp -> ConverterEngine [label="uses"];
  ConverterApp -> ConverterConfig [label="reads"];
  ConverterApp -> ConverterResult [label="returns"];
}"""

def main(out: str = "out/converterTool_class_diagram.dot"):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(DOT, encoding="utf-8")
    print(out)

if __name__ == "__main__":
    main()
