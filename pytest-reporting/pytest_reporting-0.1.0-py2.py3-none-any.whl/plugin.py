# -*- coding: utf-8 -*-

import pickle

import pytest

from .session import ReportingSession

# Make fixtures available
from .fixtures import reporting  # noqa


def pytest_terminal_summary(terminalreporter):
    terminalreporter.config._reportingsession.display(terminalreporter)


def pytest_configure(config):
    config._reportingsession = ReportingSession()


@pytest.mark.optionalhook
def pytest_testnodedown(node):
    if hasattr(node, "slaveoutput") and "_reportingsession" in node.slaveoutput:
        global_rs = node.config._reportingsession
        node_rs = pickle.loads(node.slaveoutput["_reportingsession"])
        global_rs.xdist_update(node_rs)
