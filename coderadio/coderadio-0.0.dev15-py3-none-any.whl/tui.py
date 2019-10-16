from prompt_toolkit.application import Application
from prompt_toolkit.application import get_app

from prompt_toolkit.filters import has_focus

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next
from prompt_toolkit.key_binding.bindings.focus import focus_previous

from prompt_toolkit.layout import BufferControl
from prompt_toolkit.layout import ConditionalContainer
from prompt_toolkit.layout import Float
from prompt_toolkit.layout import FloatContainer
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout import HSplit
from prompt_toolkit.layout import CompletionsMenu

from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.containers import ScrollOffsets

from prompt_toolkit.layout.margins import ScrollbarMargin
from prompt_toolkit.layout.processors import BeforeInput

from prompt_toolkit.lexers import PygmentsLexer

from prompt_toolkit.widgets import Box
from prompt_toolkit.widgets import Label
from prompt_toolkit.widgets import Frame

from pygments.lexers import MarkdownLexer

from coderadio.buffers import command_buffer

from coderadio.buffers import DisplayBuffer

from coderadio.buffers import help_buffer
from coderadio.buffers import list_buffer

from coderadio.commands import handle_command

from coderadio.help_messages import TOP_MESSAGE


class TopMessage:
    def __init__(self):
        self.window = Box(Label(text=TOP_MESSAGE), padding_left=2, height=1)

    def __pt_container__(self):
        return self.window


class Display:
    def __init__(self, buffer):
        self.buffer_control = BufferControl(
            buffer=buffer, focusable=False, focus_on_click=False
        )
        self.window = Window(content=self.buffer_control)
        self.window = Frame(
            body=Box(self.window, padding_left=2, padding_right=0), height=7
        )

    def __pt_container__(self):
        return self.window


class ListView:
    def __init__(self, buffer):

        self._buffer = buffer
        self.buffer_control = BufferControl(
            buffer=self._buffer,
            focusable=True,
            key_bindings=self._get_key_bindings(),
            focus_on_click=True,
        )

        self.window = Window(
            content=self.buffer_control,
            right_margins=[ScrollbarMargin(display_arrows=True)],
        )
        self.window = Frame(
            body=Box(self.window, padding_left=2, padding_right=0)
        )

    def handler(self, event):
        # index is -> (int) line number
        index = self._buffer.document.cursor_position_row
        # text is -> (str) line content
        text = self._buffer.document.current_line
        return handle_command(event, index=index, text=text)

    def _get_key_bindings(self):
        " Key bindings for the List. "
        kb = KeyBindings()

        @kb.add("p")
        @kb.add("enter")
        def _(event):
            if self.handler is not None:
                self.handler(event)

        return kb

    def __pt_container__(self):
        return self.window


class CommandPrompt:
    def __init__(self, buffer, **kwargs):
        self.buffer = buffer
        self.before_input_text = kwargs.get("before_input_text", "➜ ")
        self.title = kwargs.get("title", "COMMAND SHELL")
        self._buffer = buffer
        self._buffer_control = BufferControl(
            buffer=self.buffer,
            input_processors=[BeforeInput(text=self.before_input_text)],
            focus_on_click=True,
        )
        self.window = Frame(
            title=self.title,
            key_bindings=self.kbindings(),
            body=FloatContainer(
                content=Window(self._buffer_control),
                key_bindings=None,
                floats=[
                    Float(
                        xcursor=True,
                        ycursor=True,
                        content=CompletionsMenu(max_height=5, scroll_offset=1),
                    )
                ],
            ),
            height=3,
        )

    def kbindings(self):

        kb = KeyBindings()

        @kb.add("enter")
        def _(event):
            handle_command(event)
            command_buffer.text = ""

        return kb

    def __pt_container__(self):
        return self.window


class PopUpWindow:
    def __init__(self, buffer, title):
        self._title = title
        self._buffer = buffer

        self.buffer_control = BufferControl(
            buffer=self._buffer, lexer=PygmentsLexer(MarkdownLexer)
        )

        self.window = Frame(
            body=Window(
                content=self.buffer_control,
                right_margins=[ScrollbarMargin(display_arrows=True)],
                scroll_offsets=ScrollOffsets(top=2, bottom=2),
            ),
            title=self._title,
        )

    def __pt_container__(self):
        return self.window


# Fix: window width on small screens
# from prompt_toolkit.layout.dimension import D
# D(preferred=80)


class AppLayout:
    def __init__(self, *args, **kwargs):
        self.layout = Layout(
            FloatContainer(
                content=HSplit(
                    [
                        self._help_message(),
                        self._top(),
                        self._center(),
                        self._botton(),
                    ]
                ),
                modal=True,
                floats=[
                    # Help text as a float.
                    Float(
                        width=60,
                        top=3,
                        bottom=2,
                        content=ConditionalContainer(
                            content=self._pop_up_window(),
                            filter=has_focus(help_buffer),
                        ),
                    )
                ],
            )
        )
        self.set_focus(command_buffer)

    def _help_message(self):
        return TopMessage()

    def _top(self):
        display_buffer = DisplayBuffer()
        buffer = display_buffer.buffer
        return Display(buffer)

    def _center(self):
        return ListView(list_buffer)

    def _botton(self):
        return CommandPrompt(command_buffer)

    def _pop_up_window(self):
        return PopUpWindow(help_buffer, title="Help")

    def set_focus(self, buffer_to_focus):
        self.layout.focus(buffer_to_focus)


class App:
    def __init__(self, *args, **kwargs):
        self.layout = AppLayout().layout
        self.app = self.create_app()

    def create_app(self):
        app = Application(
            layout=self.layout,
            key_bindings=self.kbindings(),
            full_screen=True,
            mouse_support=True,
            enable_page_navigation_bindings=True,
        )
        return app

    def kbindings(self):
        # Key bindings.
        # https://python-prompt-toolkit.readthedocs.io/en/stable/pages/advanced_topics/key_bindings.html?highlight=vim%20#list-of-special-keys
        # https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/key_bindings.html
        # https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/prompt_toolkit/keys.py
        kb = KeyBindings()
        # kb.add("tab")(focus_next)  # down
        # kb.add("s-tab")(focus_previous)  # up
        @kb.add("c-down")  # down
        def _(event):
            focus_next(event)

        @kb.add("c-up")  # up
        def _(event):
            focus_previous(event)

        @kb.add("f1")
        def _(event):
            """Launch Help Pop Up."""
            get_app().layout.focus(help_buffer)

        # kb.add('escape')(lambda event: layout.focus(command_prompt))
        kb.add("c-q")(lambda event: get_app().exit())
        return kb

    def run(self):
        self.app.run()
