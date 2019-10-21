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

from pdfpug.common import BasePugElement, ParagraphAlignment


class Paragraph(BasePugElement):
    """
    Paragraphs are considered as one of the core elements of any report with each
    paragraph being a self-contained unit around a central idea.

    :param text: Paragraph text
    :param ParagraphAlignment alignment: Horizontal paragraph alignment (defaults to
        ``ParagraphAlignment.left``)

    Instantiating a paragraph is as simple as the following,

    >>> from pdfpug.modules import Paragraph
    >>> para = Paragraph("Lorem Ipsum is simply dummy text of the printing industry")

    This component supports rich HTML formatting options like <b>, <i>, <u> tags.

    >>> para = Paragraph("Lorem Ipsum is <b>simply</b> <u>dummy</u> text!")
    """

    __slots__ = ["text", "alignment"]

    def __init__(self, text: str, **kwargs) -> None:
        super().__init__()

        # Data Variable
        self.text: str = text

        # Attributes
        self.alignment: ParagraphAlignment = kwargs.get(
            "alignment", ParagraphAlignment.left
        )

    def _calculate_pug_str(self):
        self._pug_str = (
            f'{self.depth * self._tab}p(style="text-align:{self.alignment.value}") '
            f"{self.text}"
        )
