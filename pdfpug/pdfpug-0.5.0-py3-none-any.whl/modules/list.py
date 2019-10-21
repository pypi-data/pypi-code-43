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

from typing import List, Optional, Union, Dict

from pdfpug.common import ListType, Orientation, Size, BasePugElement


class BaseList(BasePugElement):

    __slots__ = ["items", "list_type", "orientation", "size"]

    def __init__(
        self,
        items: Union[List, Dict],
        list_type: Optional[ListType] = None,
        orientation: Orientation = Orientation.vertical,
        size: Size = Size.small,
    ) -> None:
        super().__init__()

        # Attributes
        self.size = size
        self.items = items
        self.list_type = list_type
        self.orientation = orientation

    def _get_list_class(self) -> str:
        # Gather attributes
        attributes = []
        for attribute in [self.list_type, self.orientation, self.size]:
            if attribute:
                attributes.append(attribute.value)
        attributes.insert(0, "ui")
        attributes.append("list")

        # Construct attribute string e.g .ui.ordered.horizontal.list
        list_attributes = ".".join(attributes)

        return f"{self.depth * self._tab}.{list_attributes}"

    def _calculate_pug_str(self):
        self._pug_str = f"{self._get_list_class()}\n"
        self._build_list(self.items)

    def _build_list(self, items):
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    self._build_list(item)
                elif isinstance(item, (str, float, int)):
                    self._pug_str += f"{(self.depth + 1) * self._tab}.item {item}\n"
                else:
                    raise TypeError(f"{item} is of invalid nested input type!")

        elif isinstance(items, dict):
            for parent, children in items.items():
                self._pug_str += f"{(self.depth + 1) * self._tab}.item {parent}\n"
                if isinstance(children, (list, int, float, str)):
                    base_list = BaseList(children)
                    base_list.depth = self.depth + 2
                    self._pug_str += base_list.pug
                else:
                    raise TypeError(f"{children} is of invalid nested input type")

        else:
            raise TypeError("Invalid input type. Should either be a List or Dict")
