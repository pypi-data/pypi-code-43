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

from pdfpug.modules import Image
from pdfpug.common import BasePugElement, Size


class Images(BasePugElement):
    """
    Embed a row of images together using the ``Images`` class.

    :param images: Group of images
    :param Optional[Size] size: Common size of group images

    >>> from pdfpug.modules import Image, Images
    >>> images = Images(
    ...     [
    ...         Image('/home/johndoe/image1.png'),
    ...         Image('/home/johndoe/image2.png'),
    ...         Image('/home/johndoe/image3.png')
    ...     ],
    ...     size=Size.small
    ... )

    .. figure:: ../_images/images.png
        :height: 150
    """

    __slots__ = ["images", "size"]

    def __init__(self, images: List[Image], **kwargs):
        super().__init__()

        # Data Variable
        self.images: List[Image] = images

        # Attributes
        self.size: Optional[Size] = kwargs.get("size", None)

    def _calculate_pug_str(self):
        self._pug_str = f"{self.depth * self._tab}{self._get_images_class()}\n"
        for image in self.images:
            image.depth = self.depth + 1
            self._pug_str += image.pug + "\n"

    def _get_images_class(self) -> str:
        # Gather attributes
        attributes = []
        for attribute in [self.size]:
            if attribute:
                attributes.append(attribute.value)
        attributes.insert(0, ".ui")
        attributes.append("images")

        # Construct attribute string e.g ui mini images
        images_attributes = ".".join(attributes)

        return images_attributes
