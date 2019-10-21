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

from typing import List, Union, Optional

from pdfpug.common import (
    BasePugElement,
    TableSpacing,
    TableRowStyle,
    TableRowType,
    TableColumnWidth,
    TableType,
    Color,
)
from pdfpug.modules.row import Row


class Table(BasePugElement):
    """
    A Table lists data in organised manner making it easier to digest large amounts
    of data. It is made up of :py:class:`~pdfpug.modules.Row` and
    :py:class:`~pdfpug.modules.Cell` as shown in the screenshot.

    It is also worth noting that the header and body of a table are also
    comprised of the same. The header and body attributes exist primarily
    for style changes. Header contents have a stronger style by being in bold
    and allow the reader to be informed of what the categories of data are.
    The body counterpart places more emphasis on placing the content in an
    organised manner so to speak.

    .. figure:: ../_images/table.png
        :height: 150

    :param Optional[List] header: Header row
    :param List[List] data: Body rows
    :param TableSpacing spacing: Table spacing (defaults to ``TableSpacing.comfortable``)
    :param Optional[TableRowStyle] striped: Table row style
    :param TableType table_type: Table type (defaults to ``TableType.celled``)
    :param Optional[Color] color: Table color
    :param Optional[TableColumnWidth] column_width_rule: Table column width

    A simple table consisting of just strings and numbers can be created as shown
    below.

    >>> from pdfpug.modules import Table
    >>> basic_table = Table(
    ...    header=['Serial No.', 'Fruit', 'Stock Level'],
    ...    data=
    ...     [
    ...         [1, 'Apple', 'Low'],
    ...         [2, 'Orange', 'Low'],
    ...         [3, 'Grape', 'High'],
    ...         [4, 'Guava', 'Not Available']
    ...     ],
    ... )

    .. figure:: ../_images/basic_table.png
        :height: 200

    More formatting options are unlocked if the :py:class:`~pdfpug.modules.Row` and
    :py:class:`~pdfpug.modules.Cell` are used. A Cell allows for embedding of other
    elements like :py:class:`~pdfpug.modules.Header` etc thereby providing more
    control of the content layouts and style.

    A more advanced table would looks something like the following where the cell
    content alignment is modified. Also, the table has alternate row colored
    different and uses a compact style.

    >>> from pdfpug.modules import Cell, Row
    >>> from pdfpug.common import TableSpacing, TableRowStyle, State, Alignment
    >>> advanced_table = Table(
    >>>     header=['Player', 'Hero', 'Role', 'K/D/A'],
    >>>     data=
    ...     [
    ...         Row(
    ...             ['Kuro', 'Lion', Cell('Support', row_span=2), '2/10/15'],
    ...             alignment=Alignment.center,
    ...             state=State.negative
    ...         ),
    ...         Row(['Gh', 'Oracle', '3/7/6'], alignment=Alignment.center),
    ...         Row(['Miracle', 'Void', 'Carry', '9/2/4'], alignment=Alignment.center),
    ...         Row(['W33', 'Timber', 'Midlaner', '5/8/2'], alignment=Alignment.center)
    ...     ],
    ...     spacing=TableSpacing.compact,
    ...     striped=TableRowStyle.striped,
    ... )

    .. figure:: ../_images/advanced_table.png
        :height: 175
    """

    __slots__ = [
        "header",
        "data",
        "spacing",
        "striped",
        "table_type",
        "color",
        "column_width_rule",
    ]

    def __init__(self, data: List[Union[List, Row]], **kwargs) -> None:
        super().__init__()

        # Data Variables
        self.header: Optional[Union[List, Row]] = kwargs.get("header", None)
        self.data: List[Union[List, Row]] = data

        # Attributes
        self.spacing: TableSpacing = kwargs.get("spacing", TableSpacing.comfortable)
        self.striped: Optional[TableRowStyle] = kwargs.get("striped", None)
        self.table_type: TableType = kwargs.get("table_type", TableType.celled)
        self.color: Optional[Color] = kwargs.get("color", None)
        self.column_width_rule: Optional[TableColumnWidth] = kwargs.get(
            "column_width_rule", None
        )

    def _calculate_pug_str(self):
        # Gather attributes
        attributes = []
        for attribute in [
            self.spacing,
            self.striped,
            self.table_type,
            self.color,
            self.column_width_rule,
        ]:
            if attribute:
                attributes.append(attribute.value)
        attributes.insert(0, "ui")
        attributes.append("table")

        table_class = f'{self.depth * self._tab}table(class="{" ".join(attributes)}")'
        header = self._construct_header() if self.header else ""
        body = self._construct_body()

        self._pug_str = f"{table_class}\n{header}{body}"

    def _construct_header(self) -> str:
        header_pug = f"{(self.depth + 1) * self._tab}thead\n"
        if isinstance(self.header, Row):
            self.header.depth = self.depth
            self.header.row_type = TableRowType.header
            header_pug += self.header.pug
        else:
            row = Row(self.header, row_type=TableRowType.header)
            row.depth = self.depth
            header_pug += row.pug

        return header_pug

    def _construct_body(self) -> str:
        body_pug = f"{(self.depth + 1) * self._tab}tbody\n"
        for row in self.data:
            if not isinstance(row, Row):
                row = Row(row, row_type=TableRowType.body)
            row.depth = self.depth
            body_pug += row.pug

        return body_pug
