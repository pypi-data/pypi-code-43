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

from typing import Optional

from pdfpug.common import BasePugElement, Color, Size, LabelType


class Label(BasePugElement):
    """
    Label are useful for depicting classification categories and are analogous
    to tags. A group of labels are by default displayed horizontally. They can
    be customized in various colors and types.

    >>> from pdfpug.modules.Label
    >>> from pdfpug.common import Color, LabelType
    >>> category = Label(text='Documentation', color=Color.blue)
    >>> tag = Label(text="v1.0", label_type=LabelType.tag)

    .. figure:: ../_images/labels.png
        :height: 30

    .. note::
        Do not mistake a `Label` element for UI labels that display paragraphs
        of text! That use case is covered by :py:class:`~pdfpug.modules.Paragraph`
        element.

    :param Optional[str] text: content
    :param Optional[str] subtext: content detail
    :param Optional[Color] color: background color
    :param Optional[Size] size: size of label
    :param Optional[LabelType] label_type: label type
    """

    __slots__ = ["text", "subtext", "color", "size", "label_type"]

    def __init__(self, **kwargs):
        super().__init__()

        self.text: Optional[str] = kwargs.get("text", None)
        self.subtext: Optional[str] = kwargs.get("subtext", None)
        self.color: Optional[Color] = kwargs.get("color", None)
        self.size: Optional[Size] = kwargs.get("size", None)
        self.label_type: Optional[LabelType] = kwargs.get("label_type", None)

    def _calculate_pug_str(self):
        self._pug_str = f"{self.depth * self._tab}{self._get_label_class()}"
        self._add_text()
        self._add_subtext()

    def _add_text(self):
        if self.text:
            self._pug_str += f" {self.text}"

    def _add_subtext(self):
        if self.subtext:
            self._pug_str += f"\n{(self.depth + 1) * self._tab}.detail {self.subtext}"

    def _get_label_class(self):
        # Gather attributes
        attributes = []
        for attribute in [self.color, self.size, self.label_type]:
            if attribute:
                attributes.append(attribute.value)
        attributes.insert(0, ".ui")
        attributes.append("label")

        if not self.text and self.label_type == LabelType.circular:
            attributes.insert(1, "empty")

        # Construct attribute string e.g ".ui.red.label"
        label_attributes = ".".join(attributes)

        return label_attributes
