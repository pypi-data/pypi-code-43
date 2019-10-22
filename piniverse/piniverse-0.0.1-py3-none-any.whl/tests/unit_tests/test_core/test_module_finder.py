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

from piniverse.core.module_finder import ModuleFinder
# from piniverse.common.responsibilities.responsibility
# import ResponsibilityUtils
import tests.unit_tests.test_core.my_package as my_package


def test_module_finder():
    module_finder = ModuleFinder()
    assert 'default' == module_finder.key
    assert not module_finder.value
    assert not module_finder.successor
    assert 'tests.unit_tests.test_core.my_package' == ModuleFinder.parse(my_package)
    assert 'tests.unit_tests.test_core.my_package' == ModuleFinder.parse(my_package.__name__)

    modules = ModuleFinder().execute({'package': my_package})['modules']
    assert 'tests.unit_tests.test_core.my_package.__init__' in modules
    assert 'tests.unit_tests.test_core.my_package.my_file' in modules
    assert 'tests.unit_tests.test_core.my_package.my_directory.my_file' in modules
