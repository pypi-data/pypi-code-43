#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from functools import partial


class Infix(object):
    def __init__(self, func):
        self._func = func

    def __ror__(self, o):
        return Infix(partial(self._func, o))

    def __or__(self, o):
        return self._func(o)

    def __call__(self, o1, o2):
        return self._func(o1, o2)


@Infix
def isin(o1, o2):
    return o1.__isin__(o2)
