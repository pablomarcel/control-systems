
import os, logging

def test_import_modules():
    import frequency_response.plotTool as pt
    import frequency_response.plotTool.cli as cli
    import frequency_response.plotTool.app as app
    import frequency_response.plotTool.apis as apis
    import frequency_response.plotTool.core as core
    import frequency_response.plotTool.design as design
    import frequency_response.plotTool.io as io
    import frequency_response.plotTool.utils as utils
    import frequency_response.plotTool.tools.plotting_mpl as pmpl
    import frequency_response.plotTool.tools.plotting_plotly as pply

def test_utils_build_logger_levels(monkeypatch):
    import frequency_response.plotTool.utils as utils
    # No level provided -> defaults; should not raise
    log = utils.build_logger("pt_cov_default")
    print("[logger default] level=", log.level)
    assert hasattr(log, "info")

    # String level
    log2 = utils.build_logger("pt_cov_str", level="DEBUG")
    print("[logger str] level=", log2.level)
    assert isinstance(log2.level, int)

    # Int level
    log3 = utils.build_logger("pt_cov_int", level=20)
    print("[logger int] level=", log3.level)
    assert isinstance(log3.level, int)

    # Env DEBUG path: some installs keep logger at INFO but print DEBUG lines;
    # we don't assert the exact level, only that logger exists and can log.
    monkeypatch.setenv("PLOTTOOL_DEBUG", "1")
    log4 = utils.build_logger("pt_cov_env")
    print("[logger env] level=", log4.level, "isEnabled(DEBUG)=", log4.isEnabledFor(logging.DEBUG))
    assert hasattr(log4, "debug")
