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

from typing import Optional, List

from pdfpug.common import BasePugElement


class MetaInformation(BasePugElement):
    """
    Helper class to allow embedding metadata into the PDF file

    :param version: Library version
    :param title: Document title
    :param description: Document description
    :param authors: Document authors
    :param keywords: Document keywords
    """

    __slots__ = ["title", "description", "authors", "keywords", "version"]

    def __init__(
        self,
        version: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        authors: Optional[List] = None,
        keywords: Optional[List] = None,
    ):
        super().__init__()

        self.title = title
        self.description = description
        self.authors = authors
        self.keywords = keywords
        self.version = version

    def _calculate_pug_str(self):
        # The meta information supported by weasyprint is documented at
        # https://weasyprint.readthedocs.io/en/stable/api.html#weasyprint.document.DocumentMetadata

        self._pug_str += (
            f"\n{self.depth * self._tab}title {self.title}" if self.title else ""
        )

        meta = {
            "author": ",".join(self.authors if self.authors else []),
            "keywords": ",".join(self.keywords if self.keywords else []),
            "description": self.description,
            "generator": f"PdfPug {self.version}",
        }

        for key, value in meta.items():
            if value:
                self._pug_str += (
                    f'\n{self.depth * self._tab}meta(name="{key}" content="{value}")'
                )
