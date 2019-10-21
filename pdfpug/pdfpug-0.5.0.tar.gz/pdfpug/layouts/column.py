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
from pdfpug.layouts.helpers import convert_number_to_word


class Column(BasePugElement):
    """
    The grid system divides horizontal space into indivisible units called Columns.
    The :py:class:`~pdfpug.layouts.Column` layout is the one that contain the
    actual content like :py:class:`~pdfpug.modules.Paragraph` etc. Think of
    it as a container that holds content in a vertical layout.

    :param int width: Width of the column (should be in the range of 1-14)
    """

    __slots__ = ["data", "width"]

    def __init__(self, **kwargs):
        super().__init__()

        self.data: List[BasePugElement] = []

        # Attributes
        self.width: int = kwargs.get("width", 0)

    def add_element(self, element: BasePugElement) -> None:
        """
        Add element to the column

        :param BasePugElement element: Element to be added to the column
        """
        if not isinstance(element, BasePugElement):
            raise TypeError(f"{element} is not a valid element!")
        self.data.append(element)

    def _calculate_pug_str(self):
        self._pug_str = self._get_column_class()

        for data_element in self.data:
            data_element.depth = self.depth + 1
            self._pug_str += "\n" + data_element.pug

    def _get_column_class(self):
        if self.width > 14 or self.width < 0:
            raise ValueError("column width should between 0 and 14")

        width = f".{convert_number_to_word(self.width)}.wide" if self.width else ""

        return f"{self.depth * self._tab}{width}.column"
