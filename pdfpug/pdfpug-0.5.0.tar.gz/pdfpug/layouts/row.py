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

from typing import List

from pdfpug.common import BasePugElement
from pdfpug.layouts.column import Column
from pdfpug.layouts.helpers import convert_number_to_word


class Row(BasePugElement):
    """
    Rows are groups of columns which are aligned horizontally. When a group of
    columns exceed the grid width (14 units), the content automatically flows
    to the next row which is to say that rows are created automatically
    as required.

    However, if explicit control is required for achieving a particular layout
    it can be declared with columns added to it. For instance, in the illustration
    below, the first row has 2 columns A, B which occupy a total of 10 units.
    If the row was not explicitly declared, then column C would be placed
    in the first row due to available space.

    .. figure:: ../_images/rowlayout.png
        :height: 140
    """

    __slots__ = ["data", "column_count"]

    def __init__(self, **kwargs):
        super().__init__()

        self.data: List[Column] = []

        # Attributes
        self.column_count: int = kwargs.get("column_count", 0)

    def add_column(self, column: Column) -> None:
        """
        Add column to the row

        :param Column column: Column to be added to the row
        """
        if not isinstance(column, Column):
            raise TypeError(f"{column} is not a valid Column!")
        self.data.append(column)

    def _calculate_pug_str(self):
        self._pug_str = self._get_row_class()

        for column in self.data:
            column.depth = self.depth + 1
            self._pug_str += "\n" + column.pug

    def _get_row_class(self):
        if self.column_count > 14 or self.column_count < 0:
            raise ValueError("column_count should between 0 and 14")

        column_count = (
            f".{convert_number_to_word(self.column_count)}.column"
            if self.column_count
            else ""
        )

        return f"{self.depth * self._tab}{column_count}.row"
