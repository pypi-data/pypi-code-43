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

from pdfpug.common import ListType, url, BasePugElement, HeaderTier, Alignment
from pdfpug.modules import BaseList, Header


class TableOfContents(BasePugElement):
    """
    The TableOfContents element automatically searches the entire document for
    tier `h1` and `h2` headers and compiles the overall structure of the
    document. One needs to only add the table of contents element to the
    :py:class:`~pdfpug.PdfReport` class using the
    :py:func:`~pdfpug.PdfReport.add_element` function.

    >>> from pdfpug.modules import TableOfContents, Header
    >>> from pdfpug import PdfReport
    >>> toc = TableOfContents()
    >>> report = PdfReport()
    >>> report.add_element(toc)
    >>> report.add_element(Header('PdfPug'))
    >>> report.generate_pdf('pdfpug.pdf')
    """

    def __init__(self, **kwargs):
        super().__init__()

        self._elements: List[BasePugElement] = kwargs.get("elements", [])

    def _calculate_pug_str(self):
        data = self._prepare_data()
        contents = BaseList(data, ListType.ordered)
        header = Header(
            "Table of Contents", tier=HeaderTier.h1, alignment=Alignment.left
        )

        self._pug_str = f"{header.pug}\n{contents.pug}"
        self._pug_str = self._pug_str.replace(
            ".ui.ordered.vertical.small.list",
            '.ui.ordered.vertical.small.list(id="Table-of-Contents-List")',
        )

    def _prepare_data(self):
        data = []
        h1_headers = {}
        current_header = None

        for element in self._elements:
            # Ignore non header elements
            if not isinstance(element, Header):
                continue

            # Only consider h1 and h2 tier headers
            if element.tier not in [HeaderTier.h1, HeaderTier.h2]:
                continue

            header = url(f'#{element.text.replace(" ", "-")}', element.text)

            if element.tier == HeaderTier.h1:
                h1_headers[header] = {"contents": []}
                current_header = header
            else:
                if current_header is None:
                    current_header = "H1 Header"
                    h1_headers[current_header] = {"contents": []}
                h1_headers[current_header]["contents"].append(header)

        for h1_header, value in h1_headers.items():
            if value["contents"]:
                item = {h1_header: []}
                for h2_header in value["contents"]:
                    item[h1_header].append(h2_header)
                data.append(item)
            else:
                data.append(h1_header)

        return data
