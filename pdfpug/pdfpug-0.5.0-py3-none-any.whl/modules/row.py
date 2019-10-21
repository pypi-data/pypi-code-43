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

from typing import List, Optional

from pdfpug.common import BasePugElement, TableRowType, State, Alignment
from pdfpug.modules.cell import Cell


class Row(BasePugElement):
    """
    A Row is the next higher order element above :py:class:`~pdfpug.modules.Cell`.
    Multiple Rows make up a :py:class:`~pdfpug.modules.Table` similar to how multiple
    :py:class:`~pdfpug.modules.Cell` make a Row.

    :param List data: Row contents
    :param TableRowType row_type: Row type (defaults to ``TableRowType.body``)
    :param Optional[State] state: Row state
    :param Optional[Alignment] alignment: Horizontal alignment of row contents

    >>> from pdfpug.modules import Row, Cell, Header
    >>> row = Row(
    ...     ['Cell 1', 'Cell 2', Cell(Header('Inception'))], alignment=Alignment.left
    ... )
    """

    __slots__ = ["data", "row_type", "state", "alignment"]

    def __init__(self, data: List, **kwargs):
        super().__init__()

        # Data Variable
        self.data: List = data

        # Attributes
        self.row_type: TableRowType = kwargs.get("row_type", TableRowType.body)
        self.state: Optional[State] = kwargs.get("state", None)
        self.alignment: Optional[Alignment] = kwargs.get("alignment", None)

    def _calculate_pug_str(self):
        self._pug_str = f"{self._construct_row()}{self._calculate_row_content()}"

    def _construct_row(self) -> str:
        # Gather attributes
        attributes = []
        for attribute in [self.state, self.alignment]:
            if attribute:
                attributes.append(attribute.value)

        row_class = f'(class="{" ".join(attributes)}")' if attributes else ""

        return f"{(self.depth + 2) * self._tab}tr{row_class}\n"

    def _calculate_row_content(self) -> str:
        row_content = ""
        for cell in self.data:
            if not isinstance(cell, Cell):
                cell = Cell(cell)
            cell.cell_type = self.row_type
            cell.depth = self.depth
            row_content += cell.pug

        return row_content
