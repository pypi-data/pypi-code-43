# Copyright (C) 2019 Michał Góral.
#
# This file is part of TWC
#
# TWC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TWC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TWC. If not, see <http://www.gnu.org/licenses/>.

from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window


class MessageBox:
    def __init__(self):
        self.box = FormattedTextControl(
            '',
            focusable=False,
            show_cursor=False)
        self.window = Window(self.box, dont_extend_height=True)

    def print(self, text):
        self.box.text = text

    def clear(self):
        self.box.text = ''

    def empty(self):
        return bool(self.box.text)

    def __pt_container__(self):
        return self.window
