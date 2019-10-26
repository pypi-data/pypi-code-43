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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pytest
import inspect

from piniverse.core.pin_node import PinNode, PinGraph
from piniverse.common.exceptions.pin_exception import PinException
from tests.unit_tests.test_core.my_package.my_file import foo, another_foo


def test_pin_node():
    pin_node_1 = PinNode('1', '2', arguments={'args': ['3'], 'kwargs': {'4': '5'}}, function=foo)
    assert '1' == pin_node_1.task
    assert '2' == pin_node_1.toward
    assert '3' == pin_node_1.arguments['args'][0]
    assert '5' == pin_node_1.arguments['kwargs']['4']
    assert foo == pin_node_1.function

    argspecs_1 = pin_node_1.argspecs()
    assert [] == argspecs_1['args']
    assert not argspecs_1['varargs']
    assert not argspecs_1['varkw']
    assert not argspecs_1['defaults']
    assert [] == argspecs_1['kwonlyargs']
    assert not argspecs_1['kwonlydefaults']
    assert '{}' == argspecs_1['annotations']

    pin_node_2 = PinNode('2', '2', arguments={'args': ['3'], 'kwargs': {'4': '5'}}, function=another_foo)
    assert '2' == pin_node_2.task
    assert '2' == pin_node_2.toward
    assert '3' == pin_node_2.arguments['args'][0]
    assert '5' == pin_node_2.arguments['kwargs']['4']
    assert another_foo == pin_node_2.function

    argspecs = PinNode.parse(inspect.getfullargspec(foo))
    assert [] == argspecs['args']
    assert not argspecs['varargs']
    assert not argspecs['varkw']
    assert not argspecs['defaults']
    assert [] == argspecs['kwonlyargs']
    assert not argspecs['kwonlydefaults']
    assert '{}' == argspecs['annotations']

    argspecs_2 = pin_node_2.argspecs()
    assert [] == argspecs_2['args']
    assert not argspecs_2['varargs']
    assert not argspecs_2['varkw']
    assert not argspecs_2['defaults']
    assert [] == argspecs_2['kwonlyargs']
    assert not argspecs_2['kwonlydefaults']
    assert '{}' == argspecs_2['annotations']


def test_pin_graph():
    parents = {'1': '1', '2': '1', '3': '2', '4': '4', '5': '4'}
    assert '1' == PinGraph.find(parents, '1')
    assert '1' == PinGraph.find(parents, '2')
    assert '1' == PinGraph.find(parents, '3')
    assert '4' == PinGraph.find(parents, '4')
    assert '4' == PinGraph.find(parents, '5')

    pin_node_1 = PinNode('1', '2', arguments={'args': ['3'], 'kwargs': {'4': '5'}}, function=foo)
    pin_node_2 = PinNode('2', '1', arguments={'args': ['3'], 'kwargs': {'4': '5'}}, function=another_foo)
    pin_nodes = [pin_node_1, pin_node_2]
    with pytest.raises(PinException) as e:
        PinGraph.union(pin_nodes)
    assert 'Found a cyclic dependency: 1, 2' == str(e.value) or 'Found a cyclic dependency: 2, 1' == str(e.value)

    pin_node_1 = PinNode('1', '2', arguments={'args': ['3'], 'kwargs': {'4': '5'}}, function=foo)
    pin_node_2 = PinNode('2', None, arguments={'args': ['3'], 'kwargs': {'4': '5'}}, function=another_foo)
    pin_nodes = [pin_node_1, pin_node_2]
    parents = PinGraph.union(pin_nodes)
    assert '1' == parents['1']
    assert '1' == parents['2']

    dag = PinGraph.topological_sort(pin_nodes)
    assert foo == next(
        filter(lambda pin_node: pin_node.task == '1', dag)).function
    assert another_foo == next(
        filter(lambda pin_node: pin_node.task == '2', dag)).function

    dag = PinGraph(pin_nodes).dag
    assert foo == next(
        filter(lambda pin_node: pin_node.task == '1', dag)).function
    assert another_foo == next(
        filter(lambda pin_node: pin_node.task == '2', dag)).function
