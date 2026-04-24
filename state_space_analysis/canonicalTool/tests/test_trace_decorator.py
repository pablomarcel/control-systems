
from __future__ import annotations
from state_space_analysis.canonicalTool.tools.trace_uml import track, export_trace_metadata

class Foo:
    @track("Foo.a", "Foo.b")
    def a(self): return 1
    def b(self): return 2

def test_export_trace_metadata():
    edges = export_trace_metadata(Foo())
    assert ("Foo.a","Foo.b") in edges
