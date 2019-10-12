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

'''Custom markup processor.
Each tag receives a list of formatted text tuples and modifies this list
in-place. That list is committed to processor's output markup when
appropriate.'''

import functools
from collections import deque
from html.parser import HTMLParser
import attr

from twc.utils import eprint
from twc.locale import tr


@attr.s
class _Any:
    '''Generic handling of any markup element'''
    tag = attr.ib()  # used tag name

    fg = attr.ib(None)
    bg = attr.ib(None)
    color = attr.ib(None)  # alias for fg

    def process(self, data):
        for i, elem in enumerate(data):
            fmt, text = elem
            new = self._process(fmt, text)
            data[i] = new

    # this tries to mimick behaviour of prompt-toolkit's HTML() class
    def _process(self, fmt, text):
        style = []
        if fmt:
            style.append(fmt)

        if self.fg or self.color or self.bg:
            if self.fg:
                style.append('fg:{}'.format(self.fg))
            elif self.color:
                style.append('fg:{}'.format(self.color))
            if self.bg:
                style.append('bg:{}'.format(self.bg))
        else:
            style.append('class:{}'.format(self.tag))

        return (' '.join(style), text)


@attr.s
class _Sr:
    '''Elements surround: <sr left=[ right=]>'''
    left = attr.ib('')
    right = attr.ib('')

    __tagname__ = 'sr'

    def process(self, data):
        if len(data) == 1 and not data[0][0]:
            # single element, with no previous formatting:
            # <sr>text</sr>
            text = '{0}{1}{2}'.format(self.left, data[0][1], self.right)
            data[0] = ('', text)
        elif data:
            data.appendleft(('', self.left))
            data.append(('', self.right))


@attr.s
class _Ind:
    '''Replaces inner text with an indicator: <ind value=A>{annotation}</ind>'''
    value = attr.ib()

    __tagname__ = 'ind'

    def process(self, data):
        data_empty = all(not elem[1] for elem in data)
        data.clear()
        if not data_empty:
            data.append(('', self.value))


_tag_types = (_Sr, _Ind,)
_tag_handlers = {cls.__tagname__: cls for cls in _tag_types}


# TODO: Handle incorrect HTML (mgoral, 2019-04-24)
# pylint: disable=abstract-method
@attr.s
class Parser(HTMLParser):
    '''Parser of task format markup'''
    _tags = attr.ib(factory=deque)
    _markup = attr.ib(factory=list)

    def __attrs_post_init__(self):
        super().__init__()

    @property
    def markup(self):
        return self._markup

    def handle_starttag(self, tag, attrs):
        any_ctor = functools.partial(_Any, tag)
        ctor = _tag_handlers.get(tag, any_ctor)

        kwds = {}
        kwds.update(attrs)
        self._tags.append(ctor(**kwds))

    def handle_endtag(self, tag):
        if not self._tags:
            eprint(tr('Unexpected end tag: </{}>'.format(tag)))
            return

        ctor = _tag_handlers.get(tag, _Any)
        last = self._tags[-1]
        if isinstance(last, _Any) and last.tag == tag:
            self._tags.pop()
        elif isinstance(last, ctor):
            self._tags.pop()

    def handle_data(self, data):
        formatted = ('', data)
        if not self._tags:
            self.markup.append(formatted)
        else:
            current = deque([formatted])
            for t in reversed(self._tags):
                t.process(current)
            self._markup.extend(current)


def parse_html(text):
    parser = Parser()
    parser.feed(text)
    return parser.markup
