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

import twc.signals as signals


class Tabline:
    def __init__(self, tabs):
        self.tabs = tabs
        self._idx = 0

        self.tab_changed = signals.signal('tab_changed')

        visible = len(tabs) > 1
        height = 1 if visible else 0

        self.control = FormattedTextControl(
            self._get_tabline,
            focusable=False,
            show_cursor=False)

        self.window = Window(
            content=self.control,
            height=height,
            wrap_lines=False,
            style='class:tabline')

    @property
    def current(self):
        return self.tabs[self._idx]

    def change_idx(self, idx):
        self._idx = idx
        self.tab_changed.emit(self.current)

    def change(self, name):
        self._idx = self.tabs.index(name)
        self.tab_changed.emit(self.current)

    def _get_tabline(self):
        ft = []

        for i, tab in enumerate(self.tabs):
            if i == self._idx:
                style = 'class:tabsel'
            else:
                style = 'class:tab'
            ft.append((style, ' [{}] '.format(tab)))

        return ft

    def __pt_container__(self):
        return self.window
