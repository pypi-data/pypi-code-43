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


class Responsibility:
    """ Abstract base class for responsibilities

        To derive this class, it is expected to ovveride the '_execute' method.

        Attributes:
            key (str): responsibility's key
            value (object): responsibility's value
            successor (Responsibility): responsibility's successor
    """

    def __init__(self, key: str = 'default', value = None, successor: 'Responsibility' = None):
        self._key = key
        self._value = value
        self._successor = successor

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> str:
        return self._value

    @property
    def successor(self) -> 'Responsibility':
        return self._successor

    def execute(self, content: dict):
        return self._execute(content)

    def _execute(self, content: dict):
        pass

    def _continue_or_return(self, content: dict) -> dict:
        if self._successor:
            return self._successor.execute(content)
        else:
            return content


class ResponsibilityUtils:
    """ Utility functions for the Responsiblity class """

    @staticmethod
    def build(*responsibilities: list) -> 'Responsibility':
        head = Responsibility()
        pre = head

        for responsibility in responsibilities:
            pre._successor = responsibility
            pre = pre._successor

        return head._successor

    @staticmethod
    def pretty_print(responsibility):
        cur = responsibility
        print('\n----- Responsibilities -----\n')

        while cur:
            print('[key: {}, value: {}] -> \n'.format(cur.key, cur.value))
            cur = cur.successor

        print('null\n')
        print('\n----------------------------\n')
