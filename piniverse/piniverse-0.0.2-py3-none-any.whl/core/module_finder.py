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

import os
import importlib

from piniverse.common.responsibilities.responsibility import Responsibility
from piniverse.common.exceptions.pin_exception import PinException


class ModuleFinder(Responsibility):
    """ Module Finder

       Attributes:
            key (str): package identifier
            value (object): package or package name
            successor (Responsibility): responsibility's successor
    """

    def __init__(self, successor: 'Responsibility' = None):
        super(ModuleFinder, self).__init__(successor=successor)

    def _execute(self, content):
        if 'package' not in content:
            raise PinException('Package is undefined.\
                Expected input format { \'package\': [package name] }')

        package = ModuleFinder.parse(content['package'])
        path = importlib.import_module(package).__file__.replace('__init__.py', '')

        targets = []
        for root, dirs, files in os.walk(path):
            for _file in files:
                prefix = root.replace(os.sep, '.')
                index = prefix.find(package)

                if prefix.endswith('.'):
                    prefix = prefix[index:][:-1]
                else:
                    prefix = prefix[index:]

                if _file.endswith('.py'):
                    targets.append('{}.{}'.format(prefix, _file.replace('.py', '')))

        return self._continue_or_return({
            'modules': targets
        })

    @staticmethod
    def parse(package):
        if isinstance(package, str):
            return package
        else:
            return package.__name__
