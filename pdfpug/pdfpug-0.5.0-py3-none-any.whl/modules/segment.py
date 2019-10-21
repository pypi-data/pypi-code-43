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

from typing import Optional, List, Union

from pdfpug.common import (
    BasePugElement,
    Color,
    SegmentType,
    SegmentEmphasis,
    Alignment,
    SegmentSpacing,
)
from pdfpug.modules import Paragraph


class Segment(BasePugElement):
    """
    A segment is used to create a grouping of related content.

    :param data: Content to be grouped
    :param Optional[SegmentType] segment_type: Visual style
    :param Optional[Alignment] aligment: Horizontal alignment of all content
    :param Optional[SegmentSpacing] spacing: Padding around the content
    :param Optional[SegmentEmphasis] emphasis: Emphasis strength of segment

    >>> from pdfpug.modules import Segment, Header, Paragraph, UnorderedList
    >>> from pdfpug.common import HeaderTier
    >>> segment = Segment(
    ...     [
    ...         Header('Segment', tier=HeaderTier.h3),
    ...         Paragraph(
    ...             'Segments are <b>collection views</b> that can be used to group '
    ...             'content together. They can contain images, headers, and any '
    ...             'other elements that is supported by PdfPug. Segments come in '
    ...             'different styles that can be used to modify it to different use '
    ...             'cases.'
    ...         ),
    ...         Paragraph('Some segment types are listed below,'),
    ...         UnorderedList(['Stacked', 'Piled', 'Vertical', 'Basic'])
    ...     ],
    ... )

    .. figure:: ../_images/segment.png
        :height: 250

    The appearance of segments can be styled for different use cases and preferences,

    >>> from pdfpug.common import SegmentType
    >>> segment.segment_type = SegmentType.stacked
    """

    __slots__ = ["data", "segment_type", "color", "emphasis", "alignment", "spacing"]

    def __init__(self, data, **kwargs):
        super().__init__()

        # Data Variable
        self.data: Union[str, List[Union[str, BasePugElement]]] = data

        # Attributes
        self.segment_type: Optional[SegmentType] = kwargs.get("segment_type", None)
        self.color: Optional[Color] = kwargs.get("color", None)
        self.emphasis: Optional[SegmentEmphasis] = kwargs.get("emphasis", None)
        self.alignment: Optional[Alignment] = kwargs.get("alignment", None)
        self.spacing: Optional[SegmentSpacing] = kwargs.get("spacing", None)

    def _calculate_pug_str(self):
        self._pug_str = f"{self.depth * self._tab}{self._get_segment_class()}"

        if not isinstance(self.data, list):
            self.data = [self.data]

        for data_element in self.data:
            if isinstance(data_element, (str, int, float)):
                data_element = Paragraph(data_element)

            data_element.depth = self.depth + 1

            # Overwrite alignment of child elements
            if (
                self.alignment
                and hasattr(data_element, "alignment")
                and not isinstance(data_element, Paragraph)
            ):
                data_element.alignment = self.alignment
                # TODO: Fix Paragraph alignment that uses another enum

            self._pug_str += "\n" + data_element.pug

    def _get_segment_class(self) -> str:
        # Gather attributes
        attributes = []
        for attribute in [
            self.segment_type,
            self.color,
            self.emphasis,
            self.alignment,
            self.spacing,
        ]:
            if attribute:
                attributes.append(attribute.value)
        attributes.insert(0, ".ui")
        attributes.append("segment")

        # Construct attribute string e.g .ui.piled.red.segment
        segment_attributes = ".".join(attributes)
        segment_attributes = segment_attributes.replace(" ", ".")

        return segment_attributes
