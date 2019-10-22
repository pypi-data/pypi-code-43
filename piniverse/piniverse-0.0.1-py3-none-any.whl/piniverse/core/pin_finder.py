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

import importlib
import inspect

from piniverse.core.pin_node import PinNode
from piniverse.core.tags import PinKeys, PinValues
from piniverse.common.responsibilities.responsibility import Responsibility
from piniverse.common.visitors.visitor import Visitor


class PinFinder(Responsibility, Visitor):
    """ Pin Finder

        Attributes:
            pin_nodes (list): list of pin nodes
            successor (Responsibility): succeeding responsibility
    """

    def __init__(self, successor: 'Responsibility' = None):
        super(PinFinder, self).__init__(successor=successor)
        self._pin_nodes = []

    @property
    def pin_nodes(self):
        return self._pin_nodes

    def _execute(self, content):
        modules = content['modules']

        for module in modules:
            imported = importlib.import_module(module)
            members = inspect.getmembers(imported, predicate=inspect.isfunction)

            for member in members:
                function = member[1]
                self.visit(function)

        return self._continue_or_return({
            'pin_nodes': self._pin_nodes
        })

    def visit(self, visitable):
        if getattr(visitable, PinKeys.TAG, '') == PinValues.PINNED:
            pin_node = PinNode(
                getattr(visitable, PinKeys.TASK),
                getattr(visitable, PinKeys.TOWARD),
                getattr(visitable, PinKeys.ARGUMENTS),
                visitable)

            self._pin_nodes.append(pin_node)
