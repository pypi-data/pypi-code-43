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

from piniverse.core.pin_node import PinGraph
from piniverse.core.pin_store import PinStore
from piniverse.core.tags import PinKeys, PinValues
from piniverse.common.exceptions.pin_exception import PinException


class Pin:
    """ Pin

        Attributes:
            task (int): task number
            toward (int): toward next task number
            arguments (dict): arguments for wrapped function
    """

    def __init__(self, task: str, toward: str, arguments: dict):
        self._task = task
        self._toward = toward
        self._arguments = arguments

    @property
    def task(self):
        return self._task

    @property
    def toward(self):
        return self._toward

    @property
    def arguments(self):
        return self._arguments


class PinDecorator(Pin):
    """ Pin Decorator """

    def __init__(self, task: str = None, toward: str = None, arguments: dict = {'args': [], 'kwargs': {}}):
        if not task:
            raise PinException('Task is undefined')

        if 'args' not in arguments:
            arguments['args'] = []

        if 'kwargs' not in arguments:
            arguments['kwargs'] = {}

        super(PinDecorator, self).__init__(
            task,
            toward if task != toward else None,
            arguments)

    def __call__(self, child):
        setattr(child, PinKeys.TASK, self._task)
        setattr(child, PinKeys.TOWARD, self._toward)
        setattr(child, PinKeys.ARGUMENTS, self._arguments)
        setattr(child, PinKeys.TAG, PinValues.PINNED)
        return child


Pinned = PinDecorator


class PinOrchestrator():
    """ Pin Orchestrator

        Attributes:
            title (str): title of the orchestrator
            responsibilities (Responsibility): list of responsibilities
            pin_graph (PinGraph): graph of pin nodes
    """

    def __init__(self, title: str = 'master', pin_responsibilities=None):
        self._title = title
        self._pin_responsibilities = pin_responsibilities
        self._pin_graph = None

    @property
    def pin_graph(self):
        return self._pin_graph

    def apply(self):
        if not self._pin_graph:
            raise PinException('Pin Graph is undefined. Plan before apply')

        stores = {}
        for k, v in self._pin_graph.parents.items():
            if k == v:
                stores[k] = PinStore()

        for pin_node in self._pin_graph.dag:
            task = pin_node.task
            args = pin_node.arguments
            _callable = pin_node.function

            try:
                parent = PinGraph.find(self._pin_graph.parents, task)
                store = stores[parent]

                kwargs = {
                    **args['kwargs'],
                    'store': store
                }

                result = _callable(*args['args'], **kwargs)
                store.rpush(task=task, content=result)
            except Exception as e:
                raise PinException(
                    'Failed to execute callable {} due to {}'.format(
                        _callable.__name__,
                        str(e)))

    def plan(self, package):
        pin_nodes = self._pin_responsibilities.execute(
            {'package': package}
        )['pin_nodes']

        self._pin_graph = PinGraph(pin_nodes)

    def orchestrate(self):
        pass
