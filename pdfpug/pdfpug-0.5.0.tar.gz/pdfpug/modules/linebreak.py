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

from pdfpug.common import BasePugElement


class LineBreak(BasePugElement):
    """
    Add a line break (blank line)

    :param lines_count: No of blank lines to add

    >>> from pdfpug.modules import LineBreak
    >>> from pdfpug import PdfReport
    >>> report = PdfReport()
    >>> report.add_element(LineBreak())
    """

    __slots__ = ["lines_count"]

    def __init__(self, lines_count: int = 1) -> None:
        super().__init__()

        self.lines_count: int = lines_count

    def _calculate_pug_str(self):
        for i in range(self.lines_count):
            self._pug_str += f"{self.depth * self._tab}br\n"

        # Remove trailing new line character
        self._pug_str = self._pug_str[:-1]
