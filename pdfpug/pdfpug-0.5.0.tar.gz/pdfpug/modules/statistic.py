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

from typing import Optional, Union

from pdfpug.common import BasePugElement, Color, Size, Orientation


class Statistic(BasePugElement):
    """
    A statistic element can be used to show metrics. It adds emphasis with its
    visual appearance.

    Using it is very simple as shown below!

    >>> from pdfpug.modules.Statistic
    >>> no_of_flights = Statistic(label="Flights", value=14567)

    .. figure:: ../_images/statistic.png
        :height: 60

    :param label: Text to provide context of the metric
    :param value: Metric
    :param Optional[Color] color: Display color
    :param Optional[Size] size: Display size
    :param Optional[Orientation] orientation: Layout of the label and value
    """

    __slots__ = ["label", "value", "color", "size", "orientation"]

    def __init__(self, label: str, value: Union[str, int, float], **kwargs):
        super().__init__()

        # Data variables
        self.label = label
        self.value = value

        # Attributes
        self.color: Optional[Color] = kwargs.get("color", None)
        self.size: Optional[Size] = kwargs.get("size", None)
        self.orientation: Optional[Orientation] = kwargs.get("orientation", None)

    def _calculate_pug_str(self) -> None:
        self._pug_str = f"{self.depth * self._tab}{self._get_statistic_class()}"
        self._build_value()
        self._build_label()

    def _build_label(self) -> None:
        self._pug_str += f"\n{(self.depth + 1) * self._tab}.label {self.label}"

    def _build_value(self) -> None:
        value_type = "value" if isinstance(self.value, (int, float)) else "text value"
        self._pug_str += (
            f"\n{(self.depth + 1) * self._tab}.{'.'.join(value_type.split())} "
            f"{self.value}"
        )

    def _get_statistic_class(self) -> str:
        # Gather attributes
        attributes = []
        for attribute in [self.color, self.size, self.orientation]:
            if attribute:
                attributes.append(attribute.value)
        attributes.insert(0, ".ui")
        attributes.append("statistic")

        # Construct attribute string e.g ".ui.red.statistics"
        statistic_attributes = ".".join(attributes)

        return statistic_attributes
