# The MIT License (MIT)
#
# Copyright (c) 2019 Henry Zhao
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pytest

from piniverse.core.pin import PinOrchestrator
from piniverse.core.module_finder import ModuleFinder
from piniverse.core.pin_finder import PinFinder
from piniverse.common.responsibilities.responsibility import ResponsibilityUtils
import tests.integration_tests.test_core.my_package as my_package
from tests.integration_tests.test_core.my_package.my_file import foo, another_foo
from tests.integration_tests.test_core.my_package.my_directory.my_file import yet_another_foo


def test_pin_orchestrator(capsys):
    pin_orchestrator = PinOrchestrator(
        pin_responsibilities=ResponsibilityUtils.build(ModuleFinder(), PinFinder()))

    pin_orchestrator.plan(my_package)

    parents = pin_orchestrator.pin_graph.parents
    assert '1' == parents['1']
    assert '1' == parents['2']
    assert '3' == parents['3']

    dag = pin_orchestrator.pin_graph.dag
    pin_nodes = dag
    tasks = list(map(lambda a: a.task, pin_nodes))
    assert '1' in tasks
    assert '2' in tasks
    assert '3' in tasks
    assert '1' == tasks[0]
    assert '2' == tasks[1]
    assert '3' == tasks[2]

    functions = list(map(lambda a: a.function, pin_nodes))
    assert foo in functions
    assert another_foo in functions
    assert yet_another_foo in functions

    pin_orchestrator.apply()
    captured = capsys.readouterr()
    assert 'foo, foo done, another foo\nNone\n' == captured.out
    assert '' == captured.err
