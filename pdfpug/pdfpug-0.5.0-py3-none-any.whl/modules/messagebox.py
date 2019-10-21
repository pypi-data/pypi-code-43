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

from typing import Optional, Union, List

from pdfpug.modules.paragraph import Paragraph
from pdfpug.common import BasePugElement, Color, Size, MessageState


class MessageBox(BasePugElement):
    """
    A MessageBox can be used to display information in a distinct style that
    captures the attention of the reader.

    :param Optional[str] header: title
    :param Union[str, List] body: message
    :param Optional[Color] color: color
    :param Optional[Size] size: size
    :param Optional[MessageState] state: state

    >>> from pdfpug.modules import MessageBox
    >>> from pdfpug.common import MessageState
    >>> message = MessageBox(
    ...     header="Important Announcement",
    ...     body="MessageBox is really good at capturing the attention of the reader!",
    ...     state=MessageState.info
    ... )

    .. figure:: ../_images/negative_messagebox.png
        :height: 75
    """

    __slots__ = ["header", "body", "color", "size", "state"]

    def __init__(self, body: Union[str, List], header: Optional[str] = None, **kwargs):
        super().__init__()

        self.header: Optional[str] = header
        self.body: Union[str, List] = body

        # Attributes
        self.color: Optional[Color] = kwargs.get("color", None)
        self.size: Optional[Size] = kwargs.get("size", None)
        self.state: Optional[MessageState] = kwargs.get("state", None)

    def _calculate_pug_str(self):
        self._pug_str = f"{self.depth * self._tab}{self._get_message_class()}"
        self._construct_header()
        self._construct_body()

    def _construct_header(self):
        if self.header:
            self._pug_str += f"\n{(self.depth + 1) * self._tab}.header {self.header}"

    def _construct_body(self):
        if isinstance(self.body, str):
            para = Paragraph(self.body)
            para.depth = self.depth + 1
            self._pug_str += "\n" + para.pug
        elif isinstance(self.body, list):
            self._pug_str += f'\n{(self.depth + 1) * self._tab}ul(class="list")'
            for item in self.body:
                self._pug_str += f"\n{(self.depth + 2) * self._tab}li {item}"
        else:
            raise TypeError

    def _get_message_class(self) -> str:
        # Gather attributes
        attributes = []
        for attribute in [self.color, self.size, self.state]:
            if attribute:
                attributes.append(attribute.value)
        attributes.insert(0, ".ui")
        attributes.append("message")

        # Construct attribute string e.g ui red message
        message_attributes = ".".join(attributes)

        return message_attributes
