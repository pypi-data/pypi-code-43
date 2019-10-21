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

from pdfpug.common import (
    HeaderTier,
    Alignment,
    Size,
    BasePugElement,
    Color,
    HeaderStyle,
)


class Header(BasePugElement):
    """
    A *header* element provides a short summary of the body text

    It is separated from the body element and has a strong distinct style to stand
    above all other elements. Headers give a sense of orientation to the reader.

    This class supports a wide variety of customisation that can be applied to a header
    from changing the header weight to the horizontal placement, color or style.

    Instantiating a header is as simple as the following,

    >>> from pdfpug.modules import Header
    >>> intro_header = Header('Introduction')

    Want to customise the header weight and color?

    >>> from pdfpug.common import HeaderTier, Color
    >>> intro_header.tier = HeaderTier.h2
    >>> intro_header.color = Color.red

    .. note::
        The header size can be set using either the ``tier`` or ``size`` parameter.
        **Do not set both!** Doing so will result in a ``ValueError`` being raised!
        By default, header tier is set to ``HeaderTier.h1``. When setting ``size``,
        be sure to set ``tier`` to None.

    :param text: Header text
    :param Optional[str] sub_header: Caption (sub header) below the header
    :param HeaderTier tier: Header weight (defaults to ``HeaderTier.h1``)
    :param Alignment alignment: Horizontal placement (defaults to ``Alignment.center``)
    :param Optional[Size] size: Size of header
    :param Optional[Color] color: Color of the header text
    :param Optional[HeaderStyle] style: Visual style of header
    """

    __slots__ = ["text", "sub_header", "tier", "size", "alignment", "color", "style"]

    def __init__(self, text: str, **kwargs) -> None:
        super().__init__()

        # Data Variable
        self.text: str = text
        self.sub_header: Optional[str] = kwargs.get("sub_header", None)

        # Attributes
        self.tier = kwargs.get("tier", HeaderTier.h1)
        self.size: Optional[Size] = kwargs.get("size", None)
        self.alignment: Alignment = kwargs.get("alignment", Alignment.center)
        self.color: Optional[Color] = kwargs.get("color", None)
        self.style: Optional[HeaderStyle] = kwargs.get("style", None)

    def __repr__(self):
        return f"Header({self.text})"

    def _calculate_pug_str(self):
        if self.tier and self.size:
            raise ValueError("Header must not be supplied with both Tier and Size")

        # Gather attributes
        attributes = []
        for attribute in [self.size, self.alignment, self.color, self.style]:
            if attribute:
                attributes.append(attribute.value)
        attributes.insert(0, "ui")
        attributes.append("header")

        # String attributes together
        if self.tier:
            header_attributes = " ".join(attributes)
            header_class = (
                f'{self.tier.value}(class="{header_attributes}", '
                f'id="{self.text.replace(" ", "-")}")'
            )
        else:
            header_attributes = ".".join(attributes)
            header_class = (
                f'.{header_attributes.replace(" ", ".")}'
                f'(id="{self.text.replace(" ", "-")}")'
            )

        # Construct pug string
        self._pug_str = f"{self.depth * self._tab}{header_class} {self.text}"
        if self.sub_header:
            self._pug_str += (
                f"\n{(self.depth + 1) * self._tab}.sub.header {self.sub_header}"
            )
