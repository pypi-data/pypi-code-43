from ..terminal import (
    detect_terminal,
    TrueColorTerminal,
    NoColorTerminal,
    WinLegacy,
)
from .compiler import LilyStringCompiler


def get_compiler():
    global _sm
    return _sm.compiler()


def teardown():
    global _sm
    _sm.teardown()


class StateManager(object):
    def __init__(self):
        self.appstate = {}
        self.current_terminal = None
        self.current_compiler = None

    def setup(self):
        if self.current_terminal is None:
            self.setterm(detect_terminal())

    def teardown(self):
        if self.current_terminal is not None:
            self.current_terminal.teardown(self.appstate)
            self.current_terminal = None

    def setterm(self, terminal):
        if self.current_terminal is not None:
            self.current_terminal.teardown(self.appstate)
        self.appstate = {}
        self.current_compiler = None
        terminal.setup(self.appstate)
        self.current_terminal = terminal
        self.current_compiler = LilyStringCompiler(terminal)

    def compiler(self):
        if self.current_compiler is None:
            self.setup()
        return self.current_compiler


class CustomTerminal(object):
    def __init__(self, terminal):
        self.original_term = None
        self.new_term = terminal

    def __enter__(self):
        global _sm
        self.original_term = _sm.current_terminal
        _sm.setterm(self.new_term)
        return self.new_term

    def __exit__(self, t, v, tb):
        global _sm
        if self.original_term is not None:
            _sm.setterm(self.original_term)


_sm = StateManager()


compile_all = CustomTerminal(TrueColorTerminal())
nocolor = CustomTerminal(NoColorTerminal())
colorama = CustomTerminal(WinLegacy())
