import os
from copy import deepcopy
from builtins import map
from builtins import str
from future.utils import python_2_unicode_compatible
from future.moves.itertools import zip_longest

from .style import Style
from .base import LilyBase
from .base_utils import isstringish, islilyblock
from .lilystring import lstr
from .compiler import compile_all


def block(obj, *args, **kwargs):
    if islilyblock(obj):
        return obj
    return LilyBlock(obj, *args, **kwargs)


@python_2_unicode_compatible
class LilyBlock(LilyBase):
    def __init__(self, rows=[], style=Style(), newline_char=os.linesep):
        if isstringish(rows):
            rows = rows.split(newline_char)
        if islilyblock(rows):
            rows = rows._copy_rows()
        if not hasattr(rows, "__iter__"):
            rows = [rows]

        self._endl = newline_char
        grower = lstr if style.is_default() else lambda s: lstr(s, style)
        rows = list(map(grower, rows))

        split_rows = []
        for row in rows:
            split_rows += row.split(self._endl)
        self._rows = split_rows

    def __str__(self):
        return self._endl.join(map(str, self._rows))

    def __repr__(self):
        return "c'''" + self.__str__() + "'''"

    def __getitem__(self, key):
        if not (isinstance(key, slice) or isinstance(key, int)):
            raise TypeError("Invalid argument type, looking for int or slice")

        sliced = self._copy_rows().__getitem__(key)
        return LilyBlock(sliced)

    def __iter__(self):
        for row in self._rows:
            yield row

    def __add__(self, other):
        return self.concat(other)

    def __radd__(self, other):
        try:
            return other.__add__(self)
        except TypeError:
            return LilyBlock(other).__add__(self)

    def __mul__(self, other):
        if not isinstance(other, int):
            raise TypeError("can't multiply sequence by non-int")
        if other < 1:
            return LilyBlock()
        new = LilyBlock(self._copy_rows())
        for _ in range(other - 1):
            new = new.concat(self)
        return new

    def __rmul__(self, other):
        return self.__mul__(other)

    def __iadd__(self, other):
        return self.__add__(other)

    def __imul__(self, other):
        return self.__mul__(other)

    def __gt__(self, other):
        return self.wilt() > other

    def __lt__(self, other):
        return self.wilt() < other

    def __ge__(self, other):
        return self.wilt() >= other

    def __le__(self, other):
        return self.wilt() <= other

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return sum(map(len, self._rows))

    def __hash__(self):
        with compile_all:
            return hash(self.__str__())

    def _copy_rows(self):
        return deepcopy(self._rows)

    def _isstringish(self):
        return False

    def _isblockish(self):
        return True

    def wilt(self):
        rows = map(lambda r: r.wilt(), self._rows)
        return self._endl.join(rows)

    def append(self, row, justify="left"):
        other = block(row)
        if justify != "left":
            if other.width() > self.width():
                top = self.resize_x(other.width(), justify=justify)
                top_rows = top._copy_rows()
                bottom_rows = other._copy_rows()
            else:
                top_rows = self._copy_rows()
                bottom = other.resize_x(self.width(), justify=justify)
                bottom_rows = bottom._copy_rows()
        else:
            top_rows = self._copy_rows()
            bottom_rows = other._copy_rows()

        rows = top_rows + bottom_rows
        return LilyBlock(map(lstr, rows))

    def concat(self, lilyblock, squash=False):
        rows = self._copy_rows()
        if not squash:
            width = self.width()
            rows = [s.resize(width) for s in rows]
        other_rows = lilyblock._copy_rows()
        zipped = zip_longest(rows, other_rows, fillvalue=lstr(""))
        new_rows = [r[0] + r[1] for r in zipped]
        return LilyBlock(new_rows)

    def width(self):
        return max(list(map(len, self._rows)))

    def height(self):
        return len(self._rows)

    def resize_x(self, amount, *args, **kwargs):
        rows = self._copy_rows()

        def str_resize(s):
            return s.resize(amount, *args, **kwargs)

        rows = map(str_resize, rows)
        return LilyBlock(rows)

    def resize_y(self, amount, justify="top"):
        if justify == "center":
            cur_size = len(self._rows)
            delta = amount - cur_size

            # We want the top half to always have equal or less change,
            # Expanding or contracting by an odd number will cause the
            # Lower rows to be affected more than the top rows.
            # Python will always round remainders toward negative infinity.
            # Since we want it rounded towards 0, the positive remainder 1,
            # if it exists, should get added with the quotient.
            top_delta = delta // 2 if delta > 0 else sum(divmod(delta, 2))

            # top_delta means change to the top, justify to the _bottom_.
            resize_step1 = self.resize_y(cur_size + top_delta, "bottom")
            return resize_step1.resize_y(amount, "top")
        elif justify == "bottom":
            rows = self._copy_rows()
            delta = amount - len(rows)
            if delta < 0:
                rows = rows[abs(delta) :]
                return LilyBlock(rows)
            style = rows[0].style_at(0) or Style()
            fill = lstr(" ", style)
            rows = ([fill] * delta) + rows
            return LilyBlock(rows)
        else:  # assume top 'cause whatever
            trimmed_rows = self._copy_rows()[:amount]
            if len(trimmed_rows) < amount:
                delta = amount - len(trimmed_rows)
                style = trimmed_rows[-1].style_at(0) or Style()
                fill = lstr(" ", style)
                trimmed_rows += [fill] * delta
            return LilyBlock(trimmed_rows)

    def resize(self, x=-1, y=-1, justify_x="left", justify_y="top", **kwargs):
        if y == -1:
            y_resized = LilyBlock(self._copy_rows())
        else:
            y_resized = self.resize_y(y, justify=justify_y)
        if x == -1:
            return y_resized
        else:
            return y_resized.resize_x(x, justify=justify_x, **kwargs)

    def normalize(self, justify="left"):
        return self.resize_x(self.width(), justify=justify)

    def to_lilystring(self):
        lily = lstr(self._endl)
        return lily.join(self._copy_rows())

    def style_regex(self, pattern, style_str=None, flags=0, num=0):
        lily = self.to_lilystring()
        styled = lily.style_regex(pattern, style_str, flags, num)
        return LilyBlock(styled)

    def _map_rebuild(self, func):
        rows = self._copy_rows()
        mapped = map(func, rows)
        return LilyBlock(mapped)

    def _vstrip_by_iter(self, iter, chars):
        strip_complete = False
        for row in iter:
            if strip_complete:
                yield row
                continue
            stripped = row.strip(chars)
            if len(stripped) != 0:
                strip_complete = True
                yield row

    def tstrip(self, chars=None):
        rows = self._vstrip_by_iter(self._copy_rows(), chars)
        return LilyBlock(rows)

    def bstrip(self, chars=None):
        rows = self._vstrip_by_iter(self._copy_rows()[::-1], chars)
        return LilyBlock(list(rows)[::-1])

    def lstrip(self, chars=None):
        def func(s):
            return s.lstrip(chars)

        return self._map_rebuild(func)

    def rstrip(self, chars=None):
        def func(s):
            return s.rstrip(chars)

        return self._map_rebuild(func)

    def strip_x(self, chars=None):
        def func(s):
            return s.strip(chars)

        return self._map_rebuild(func)

    def strip_y(self, chars=None):
        return self.tstrip(chars).bstrip(chars)

    def strip(self, chars=None, x=True, y=True):
        stripped = self.strip_x(chars) if x else self
        return stripped.strip_y(chars) if y else LilyBlock(self._copy_rows())
