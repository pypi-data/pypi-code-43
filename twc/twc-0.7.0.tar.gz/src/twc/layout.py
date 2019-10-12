# Copyright (C) 2019 Michał Góral.
#
# This file is part of TWC
#
# TWC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.  TWC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TWC. If not, see <http://www.gnu.org/licenses/>.

'''prompt-toolkit layout definition'''

import weakref
from contextlib import contextmanager
import attr

from prompt_toolkit import Application
from prompt_toolkit.filters import buffer_has_focus
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import (
    DynamicContainer, HSplit, FloatContainer, Float
)
from prompt_toolkit.layout.menus import CompletionsMenu

from twc.widgets import AgendaView, Tabline, CommandLine, StatusLine, MessageBox
from twc.window_stack import WindowStack


@attr.s(cmp=False)
class LayoutController:
    tw = attr.ib()
    cfg = attr.ib()
    app = attr.ib(None, init=False)

    # layout, widgets
    stack = attr.ib(None, init=False, repr=False)
    layout = attr.ib(None, init=False, repr=False)
    tabline = attr.ib(None, init=False, repr=False)
    agendaview = attr.ib(None, init=False, repr=False)
    commandline = attr.ib(None, init=False, repr=False)
    statusline = attr.ib(None, init=False, repr=False)
    messages = attr.ib(None, init=False, repr=False)

    def make_app(self, *a, **kw):
        assert self.app is None, "prompt_toolkit Application already exists"

        self.layout = self._make_layout()
        kw['layout'] = self.layout

        self.app = Application(*a, **kw)
        self.app.controller = weakref.ref(self)
        return self.app

    def push(self, container):
        self.stack.append(container)
        self.focus(container)

    def pop(self):
        if self.stack:
            self.stack.pop()
        if self.stack:
            self.layout.focus(self.stack[-1])
        else:
            self.app.exit()

    def focus(self, container):
        with self.act_on_state_change():
            self.layout.focus(container)

    @contextmanager
    def focused(self, container):
        prev = self.layout.current_window
        try:
            self.focus(container)
            yield
        finally:
            self.focus(prev)

    def is_normal_state(self):
        return not buffer_has_focus()

    def is_insert_state(self):
        return buffer_has_focus()

    @contextmanager
    def act_on_state_change(self):
        def _states():
            is_insert = buffer_has_focus()
            return (is_insert, not is_insert)

        try:
            was_insert, was_normal = _states()
            yield
        finally:
            if was_normal and self.is_insert_state():
                self._on_enter_insert_state()
            elif was_insert and self.is_normal_state():
                self._on_enter_normal_state()

    def _on_enter_insert_state(self):
        # Buffer is closed by escape key, which should be immediate action.
        # However, for some reason it waits timeoutlen, because probably
        # it has some default key sequence with escape. We don't want that -
        # our Buffer (commandline) is a simple input, which doesn't support key
        # sequences.
        self.app.timeoutlen = 0

    def _on_enter_normal_state(self):
        self.app.timeoutlen = self.cfg.settings.timeoutlen

    def _bottom_container(self):
        if self.commandline.active():
            return self.commandline
        return self.messages

    def _make_layout(self):
        '''Agenda view, i.e. a single string which contains many blocks (lists) of
        differently filtered and presented tasks.'''
        self.tabline = Tabline(list(self.cfg.agendas.keys()))
        self.agendaview = AgendaView(self.tw, self.cfg)
        self.commandline = CommandLine(self.tw, self.cfg)
        self.statusline = StatusLine(self.tw, self.cfg)
        self.messages = MessageBox()

        # signals
        self.agendaview.agenda_changed.connect(self.tabline.change)
        self.statusline.connect_to_signals(self)

        split = HSplit([
            self.tabline,
            self.agendaview,
            self.statusline,
            DynamicContainer(self._bottom_container)])

        compl_menu = Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=16, scroll_offset=1))
        float_cont = FloatContainer(content=split, floats=[compl_menu])

        self.stack = WindowStack([float_cont])

        return Layout(DynamicContainer(self.stack))
