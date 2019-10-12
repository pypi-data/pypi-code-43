# Copyright (C) 2019 Michał Góral.
#
# This file is part of TWC
#
# TWC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TWC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TWC. If not, see <http://www.gnu.org/licenses/>.

'''Task wrapper'''

import weakref
import attr


class _EmptyStrWithAnyFormat:
    def __format__(self, spec):
        return ''

    def __str__(self):
        return ''


@attr.s(hash=False)
class Task:
    t = attr.ib()  # pylint: disable=invalid-name
    _parent = attr.ib(None, init=False, cmp=False, repr=False)
    _children = attr.ib(factory=list, init=False, cmp=False, repr=False)

    @property
    def children(self):
        return self._children

    @property
    def parent(self):
        if self._parent:
            return self._parent()
        return None

    @parent.setter
    def parent(self, val):
        if self.parent:
            self.parent.children.remove(self)
        if val:
            self._parent = weakref.ref(val)
            self.parent.children.append(self)
        else:
            self._parent = val

    @property
    def depth(self):
        i = 0
        w = self
        while w.parent:
            i += 1
            w = w.parent
        return i

    def add_child(self, child):
        child.parent = self

    def remove_child(self, child):
        child.parent = None

    def __getitem__(self, key):
        # This is in fact a hack for str.format_map.
        ret = self.t[key]
        if not ret:
            return _EmptyStrWithAnyFormat()

        if isinstance(ret, set):
            ret = sorted(ret)
        if isinstance(ret, list):
            if isinstance(ret[0], str):
                return ':'.join(ret)
            return ':'.join(str(elem) for elem in ret)

        return ret

    def __hash__(self):
        return hash(self.t)
