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

from piniverse.core.pin import Pin, Pinned
from piniverse.core.tags import PinKeys, PinValues
from piniverse.common.exceptions.pin_exception import PinException


def test_pin():
    pin = Pin('1', '2', {'args': ['3'], 'kwargs': {'4': '5'}})
    assert '1' == pin.task
    assert '2' == pin.toward
    assert '3' == pin.arguments['args'][0]
    assert '5' == pin.arguments['kwargs']['4']


def test_pinned():
    with pytest.raises(PinException) as e:
        Pinned()
    assert 'Task is undefined' == str(e.value)

    with pytest.raises(PinException) as e:
        Pinned(toward='1')
    assert 'Task is undefined' == str(e.value)

    pinned = Pinned(task='1', toward='2')
    assert '1' == pinned.task
    assert '2' == pinned.toward
    assert 0 == len(pinned.arguments['args'])
    assert 0 == len(pinned.arguments['kwargs'])

    @Pinned(
        task='1',
        toward='2',
        arguments={'args': ['3'], 'kwargs': {'4': '5'}}
    )
    def foo(a, b=''):
        pass

    assert '1' == getattr(foo, PinKeys.TASK, '')
    assert '2' == getattr(foo, PinKeys.TOWARD, '')
    assert PinValues.PINNED == getattr(foo, PinKeys.TAG, '')
    assert '3' == getattr(foo, PinKeys.ARGUMENTS, None)['args'][0]
    assert '5' == getattr(foo, PinKeys.ARGUMENTS, None)['kwargs']['4']


def tes_pin_orchestrator():
    pass
