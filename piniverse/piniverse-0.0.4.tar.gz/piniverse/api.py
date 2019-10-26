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

from piniverse.core.pin import PinOrchestrator
from piniverse.core.module_finder import ModuleFinder
from piniverse.core.pin_finder import PinFinder
from piniverse.core.pin_drawer import PinDrawer
from piniverse.common.responsibilities.responsibility import ResponsibilityUtils
from piniverse.common.exceptions.pin_exception import PinException

# Pin Orchestrator
pin_orchestrator = None


def apply():
    global pin_orchestrator

    if pin_orchestrator:
        pin_orchestrator.apply()
    else:
        raise PinException('Plan before applying')


def plan(package, plan_view: bool = False):
    global pin_orchestrator
    pin_orchestrator = PinOrchestrator(
        pin_responsibilities=ResponsibilityUtils.build(
            ModuleFinder(), PinFinder()
        ))

    pin_orchestrator.plan(package)

    if plan_view:
        PinDrawer(pin_orchestrator.pin_graph.dag).illustrate()


def orchestrate():
    pass
