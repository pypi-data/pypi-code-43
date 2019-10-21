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

from pdfpug.common import BasePugElement, Color, Size


class ProgressBar(BasePugElement):
    """
    Progress bar is a slightly unconventional element, but is surprisingly
    useful in some scenarios. For instance, consider a resume where one
    would like showcase the amount of experience in a language or technology.
    This can be expressed visually using a progress bar as seen nowadays in
    many modern resume styles.

    :param percent: Amount of progress in percentage
    :param Optional[str] title: Describes the progress bar
    :param Optional[str] subtitle: Describes the maximum range value
    :param Optional[Color] color: Color of progress bar
    :param Optional[Size] size: Size of progress bar

    >>> from pdfpug.modules import ProgressBar
    >>> from pdfpug.common import Color
    >>> python_skill = ProgressBar(
    ...     75, title="Python", subtitle="Expert", color=Color.blue
    ... )

    .. figure:: ../_images/progressbar.png
        :height: 75
    """

    __slots__ = ["percent", "title", "subtitle", "color", "size"]

    def __init__(self, percent: Union[int, float], **kwargs):
        super().__init__()

        # Data variables
        self.percent: Union[int, float] = percent
        self.title: Optional[str] = kwargs.get("title", None)
        self.subtitle: Optional[str] = kwargs.get("subtitle", None)

        # Attributes
        self.color: Optional[Color] = kwargs.get("color", None)
        self.size: Optional[Size] = kwargs.get("size", None)

    def _calculate_pug_str(self):
        self._construct_title()
        self._construct_body()
        self._construct_footer()

    def _construct_title(self):
        if self.title is not None:
            self._pug_str += (
                f'{self.depth * self._tab}p(style="text-align:left;margin-bottom:3px") '
                f"<b>{self.title}</b>\n"
            )

    def _construct_body(self):
        # Gather attributes
        attributes = []
        for attribute in [self.color, self.size]:
            if attribute:
                attributes.append(attribute.value)
        attributes.insert(0, ".ui")
        attributes.append("progress")

        progress_bar_attributes = ".".join(attributes)

        top_margin = '(style="margin-top:0px")' if self.title else ""

        self._pug_str += (
            f"{self.depth * self._tab}{progress_bar_attributes}{top_margin}"
            f'\n{(self.depth + 1) * self._tab}.bar(style="width: {self.percent}%")'
        )

    def _construct_footer(self):
        if self.subtitle is not None:
            self._pug_str += (
                f"\n{(self.depth + 1) * self._tab}.label"
                f'(style="text-align:right;font-size:14px") '
                f"{self.subtitle}"
            )
