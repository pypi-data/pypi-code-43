from threading import Thread

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.completion import WordCompleter

from coderadio.exchange import display_now
from coderadio.help_messages import HELP_TEXT
from coderadio.player import radio


help_buffer = Buffer(
    document=Document(HELP_TEXT, 0), read_only=True, name="help_buffer"
)


list_buffer = Buffer(
    document=Document(radio.list(), 0),
    multiline=True,
    read_only=True,
    name="list_buffer",
)

command_buffer = Buffer(
    completer=WordCompleter(
        ["play", "stop", "rec", "info", "help", "list", "bytag", "byid", "exit"],
        ignore_case=True,
    ),
    complete_while_typing=True,
    name="command_buffer",
)


class DisplayBuffer:
    def __init__(self):
        self._buffer = Buffer(document=Document("", 0), read_only=True)
        self.forever()

    @property
    def buffer(self):
        return self._buffer

    @buffer.setter
    def buffer(self, value):
        self._buffer.set_document(Document(value, 0), bypass_readonly=True)

    def forever(self):
        def func():
            while True:
                info = display_now.get()
                self.buffer = info

        Thread(target=func, daemon=True).start()
