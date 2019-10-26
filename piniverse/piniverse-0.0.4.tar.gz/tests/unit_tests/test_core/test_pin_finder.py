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

from piniverse.core.pin_finder import PinFinder
from tests.unit_tests.test_core import my_package


def test_pin_finder():
    pin_finder = PinFinder()
    assert 'default' == pin_finder.key
    assert not pin_finder.value
    assert not pin_finder.successor
    assert 0 == len(pin_finder.pin_nodes)

    pin_nodes = pin_finder.execute(
        {'modules': ['tests.unit_tests.test_core.my_package.my_file']}
    )['pin_nodes']
    assert 2 == len(pin_nodes)
    assert my_package.my_file.foo == next(
        filter(lambda pin_node: pin_node.task == '1', pin_nodes)).function
    assert my_package.my_file.another_foo == next(
        filter(lambda pin_node: pin_node.task == '2', pin_nodes)).function
