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

from pdfpug.modules.segment import Segment
from pdfpug.common import BasePugElement, SegmentType, Orientation


class Segments(BasePugElement):
    """
    A group of :py:class:`~pdfpug.modules.Segment` can be formatted to appear
    together using :py:class:`~pdfpug.modules.Segments`.

    :param segments: Group of segments
    :param Optional[SegmentType] segments_type: Visual style
    :param Optional[Orientation] orientation: Orientation of elements
    """

    __slots__ = ["segments", "segments_type", "orientation"]

    def __init__(self, segments: List[Union[Segment, "Segments"]], **kwargs):
        super().__init__()

        # Data Variables
        self.segments: List[Union[Segment, "Segments"]] = segments

        # Attributes
        self.segments_type: Optional[SegmentType] = kwargs.get("segments_type", None)
        self.orientation: Optional[Orientation] = kwargs.get("orientation", None)

    def _calculate_pug_str(self):
        self._pug_str = f"{self.depth * self._tab}{self._get_segment_class()}"

        for segment in self.segments:
            segment.depth = self.depth + 1
            self._pug_str += "\n" + segment.pug

    def _get_segment_class(self) -> str:
        # Gather attributes
        attributes = []
        for attribute in [self.segments_type]:
            if attribute:
                attributes.append(attribute.value)
        attributes.insert(0, ".ui")
        attributes.append("segments")

        # Construct attribute string e.g .ui.piled.segments
        segments_attributes = ".".join(attributes)

        return segments_attributes
