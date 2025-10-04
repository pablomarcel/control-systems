
def test_generate_class_diagram_no_graphviz():
    from stateSpaceAnalysis.stateSolnTool.tools.diagram import generate_class_diagram
    # Should not raise even if graphviz or dot is unavailable
    generate_class_diagram("stateSpaceAnalysis/stateSolnTool/out/test_classes.png")
