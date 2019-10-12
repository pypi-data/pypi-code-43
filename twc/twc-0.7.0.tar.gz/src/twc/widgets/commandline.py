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

import asyncio
from contextlib import contextmanager

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.containers import Window, VSplit
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings

import twc.signals as signals
from twc.commands import event_to_controller


class CommandLine:
    def __init__(self, tw, cfg):
        self.tw = tw
        self.cfg = cfg
        self._lock = asyncio.Lock()
        self._command = None
        self._help_text = ''
        self._command_name = ''

        self.command_name_changed = signals.signal('command_name_changed')
        self.text_changed = signals.signal('text_changed')

        self.completer = WordCompleter(words=[], WORD=True)
        self.buffer = Buffer(
            completer=self.completer,
            complete_while_typing=self.cfg.settings.autocomplete,
            on_text_changed=self._text_changed)
        self.control = BufferControl(
            self.buffer,
            input_processors=[BeforeInput(self.show_help, 'class:tooltip')],
            key_bindings=self.keys(),
            focusable=True)

        self.prompt = FormattedTextControl(
            '',
            focusable=False,
            show_cursor=False)

        self.window = VSplit([
            Window(self.prompt, dont_extend_width=True),
            Window(content=self.control, height=1),
        ])

    def keys(self):
        kb = KeyBindings()

        @self.cfg.command_handler('activate', kb)
        @event_to_controller
        def _(controller):
            if self._command:
                self._command.set_result(self.buffer.text)

        @kb.add('c-c')
        @self.cfg.command_handler('cancel', kb)
        @event_to_controller
        def _(controller):
            if self._command:
                self._command.set_result(None)

        return kb

    def active(self):
        return self._lock.locked()

    def set_prompt(self, text):
        self.prompt.text = text

    def set_help(self, text):
        self._help_text = text

    @contextmanager
    def ensure_clear(self, **kw):
        try:
            yield
        finally:
            self.clear(**kw)

    def clear(self):
        self.set_help('')
        self.completer.words = []
        self.command = ''
        self.buffer.reset()
        self.prompt.text = ''
        self._command = None

    def show_help(self):
        autohelp = self.cfg.settings.autohelp
        if autohelp and self._help_text and not self.buffer.text:
            return self._help_text
        return ''

    async def read_command(self, compl=None, prompt='> '):
        async with self._lock:
            self.set_prompt(prompt)
            if compl:
                self.completer.words = compl

            self._command = asyncio.get_event_loop().create_future()
            await self._command
            with self.ensure_clear():
                return self._command.result()

    @property
    def command(self):
        return self._command_name

    @command.setter
    def command(self, name):
        self.command_name_changed.emit(name)
        self._command_name = name

    def _text_changed(self, buffer):
        self.text_changed.emit(buffer.text)

    def __pt_container__(self):
        return self.window
