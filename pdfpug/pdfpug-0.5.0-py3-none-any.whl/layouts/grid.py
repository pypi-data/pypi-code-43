#  MIT License
#
#  Copyright (C) 2019 Nekhelesh Ramananthan
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#  PARTICULAR PURPOSE AND  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
#  AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from typing import Union, List

from pdfpug.common import BasePugElement
from pdfpug.layouts.column import Column
from pdfpug.layouts.row import Row


class Grid(BasePugElement):
    """
    A grid is a tabular structure that is divided vertically into
    :py:class:`~pdfpug.layouts.Row` and horizontally into
    :py:class:`~pdfpug.layouts.Column`. This allows for creating complex
    layouts that would otherwise not be possible. The grid system is
    illustrated below for more clarity.

    .. figure:: ../_images/grid.png
        :height: 220

    The grid system supports a maximum horizontal size of **14** units. For
    instance, 2 columns of width 7 units can be placed in a single row.
    Or a single column of width 14 units. If the width of the columns in a row
    exceed 14 units, the extra columns will automatically flow to the next
    row.

    .. note::
        Only layouts like :py:class:`~pdfpug.layouts.Row` or
        :py:class:`~pdfpug.layouts.Column` can be added to the grid
        layout.

    >>> from pdfpug.layouts import Grid, Column
    >>> from pdfpug.modules import Paragraph, OrderedList
    >>> # Create left column and its contents
    >>> para = Paragraph('Python 3.x has several releases as listed,')
    >>> left_column = Column(width=5)
    >>> left_column.add_element(para)
    >>> # Create right column and its contents
    >>> releases = OrderedList(['3.0', '3.1', '3.2', '3.3', '3.4', '3.5', '3.6', '3.7'])
    >>> right_column = Column(width=5)
    >>> right_column.add_element(releases)
    >>> # Construct grid
    >>> grid = Grid()
    >>> grid.add_layout(left_column)
    >>> grid.add_layout(right_column)
    """

    __slots__ = ["layouts"]

    def __init__(self):
        super().__init__()

        self.layouts: List[Union[Row, Column]] = []

    def add_layout(self, layout: Union[Column, Row]) -> None:
        """
        Add a Row/Column to the grid

        :param Union[Column, Row] layout: layout to be added to the grid
        """
        if not isinstance(layout, (Column, Row)):
            raise TypeError(f"{layout} is not a layout! Only Column/Row supported")
        self.layouts.append(layout)

    def _calculate_pug_str(self) -> None:
        self._pug_str = f"{self.depth * self._tab}.ui.grid"

        for layout in self.layouts:
            layout.depth = self.depth + 1
            self._pug_str += "\n" + layout.pug
