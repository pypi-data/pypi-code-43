# -*- coding: utf-8 -*-
"""Test the rules module of cenv."""
from cenv_tool.rules import RULES


def test_rules():
    """Test if RULES contain attributes as expected."""
    assert RULES.git_folder
    assert RULES.conda_cmds
    assert RULES.conda_cmds.remove
    assert RULES.conda_cmds.export
    assert RULES.conda_cmds.create
    assert RULES.conda_cmds.clone
    assert RULES.conda_cmds.restore
    assert RULES.conda_cmds.clean
