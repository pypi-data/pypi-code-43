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

from pdfpug.common import BasePugElement, ImageStyle, ImageLayout, Size


class Image(BasePugElement):
    """
    Embed picturesque visuals using the ``Image`` class with different styles

    :param path: Absolute path of image
    :param Optional[Size] size: Size of image
    :param Optional[ImageStyle] style: Render style
    :param Optional[ImageLayout] layout: Layout options

    Instantiating an image is as simple as the following,

    >>> from pdfpug.modules import Image
    >>> img = Image('/home/johndoe/image.png', size=Size.small, style=ImageStyle.rounded)

    .. figure:: ../_images/rounded_image.png
        :height: 150
    """

    __slots__ = ["path", "size", "style", "layout"]

    def __init__(self, path: str, **kwargs) -> None:
        super().__init__()

        # Data Variable
        self.path = path

        # Attributes
        self.size: Optional[Size] = kwargs.get("size", None)
        self.style: Optional[ImageStyle] = kwargs.get("style", None)
        self.layout: Optional[ImageLayout] = kwargs.get("layout", None)

    def _calculate_pug_str(self):
        self._pug_str = (
            f"{self.depth * self._tab}img({self._get_image_class()} "
            f'src="file://{self.path}")'
        )

    def _get_image_class(self) -> str:
        # Gather attributes
        attributes = []
        for attribute in [self.size, self.style, self.layout]:
            if attribute:
                attributes.append(attribute.value)
        attributes.insert(0, "ui")
        attributes.append("image")

        # Construct attribute string e.g ui circular image
        image_attributes = " ".join(attributes)

        return f'class="{image_attributes}"'
