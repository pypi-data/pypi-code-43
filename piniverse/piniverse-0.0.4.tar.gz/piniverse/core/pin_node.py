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

import inspect

from piniverse.common.exceptions.pin_exception import PinException


class PinNode:
    """ Base class for pin nodes

        task (str): task
        toward (str): toward
        arguments (dict): arguments of wrapped function
        function: wrapped function
    """

    def __init__(self, task: str, toward: str, arguments: dict, function = None):
        self._task = task
        self._toward = toward
        self._arguments = arguments
        self._function = function

    @property
    def task(self):
        return self._task

    @property
    def toward(self):
        return self._toward

    @property
    def arguments(self):
        return self._arguments

    @property
    def function(self):
        return self._function

    def argspecs(self):
        return self.parse(inspect.getfullargspec(self._function))

    @staticmethod
    def parse(argspecs):
        return {
            'args': argspecs.args,
            'varargs': argspecs.varargs,
            'varkw': argspecs.varkw,
            'defaults': argspecs.defaults,
            'kwonlyargs': argspecs.kwonlyargs,
            'kwonlydefaults': argspecs.kwonlydefaults,
            'annotations': str(argspecs.annotations)
        }


class PinGraph:
    """ Base class for pin graph

        Attributes:
            parents (dict): parents to respective tasks
            dag (list): direct acyclic graph of pin nodes
    """

    def __init__(self, pin_nodes: list):
        self._parents = PinGraph.union(pin_nodes)
        self._dag = PinGraph.topological_sort(pin_nodes)

    @property
    def parents(self):
        return self._parents

    @property
    def dag(self):
        return self._dag

    @staticmethod
    def topological_sort(pin_nodes: list) -> list:
        inwards = {}
        outwards = {}

        for pin_node in pin_nodes:
            if pin_node.task not in inwards or pin_node.task not in outwards:
                inwards[pin_node.task] = 0
                outwards[pin_node.task] = 0

        for pin_node in pin_nodes:
            if pin_node.toward:
                outwards[pin_node.task] += 1
                inwards[pin_node.toward] += 1

        actives = []
        orphans = []
        for pin_node in pin_nodes:
            if inwards[pin_node.task] == 0 and outwards[pin_node.task] == 0:
                orphans.append(pin_node)
            else:
                actives.append(pin_node)

        ref = {}
        for pin_node in actives:
            if pin_node.task not in ref:
                ref[pin_node.task] = pin_node

        graph = {}
        degrees = {}
        for pin_node in actives:
            task = pin_node.task
            toward = pin_node.toward

            if not toward:
                continue

            if task not in graph:
                graph[task] = []

            if task not in degrees:
                degrees[task] = 0

            if toward not in graph:
                graph[toward] = []

            if toward not in degrees:
                degrees[toward] = 0

            graph[task].append(toward)
            degrees[toward] += 1

        q = []
        for k, v in degrees.items():
            if v == 0:
                q.append(k)

        order = []
        while q:
            size = len(q)
            for i in range(size):
                cur = q.pop(0)
                order.append(ref[cur])

                for _next in graph[cur]:
                    degrees[_next] -= 1
                    if degrees[_next] == 0:
                        q.append(_next)

        return order + orphans

    @staticmethod
    def union(pin_nodes: list) -> list:
        parents = {}

        for pin_node in pin_nodes:
            parents[pin_node.task] = pin_node.task
            if pin_node.toward is not None:
                parents[pin_node.toward] = pin_node.toward

        ranks = {}
        for pin_node in pin_nodes:
            ranks[pin_node.task] = 1

        for pin_node in pin_nodes:
            if pin_node.toward:
                left = PinGraph.find(parents, pin_node.task)
                right = PinGraph.find(parents, pin_node.toward)

                if left != right:
                    parents[right] = left
                else:
                    raise PinException(
                        'Found a cyclic dependency: {}, {}'
                        .format(pin_node.task, pin_node.toward))

        return parents

    @staticmethod
    def find(parents: dict, cur: int) -> int:
        if parents[cur] != cur:
            parents[cur] = PinGraph.find(parents, parents[cur])
        return parents[cur]
