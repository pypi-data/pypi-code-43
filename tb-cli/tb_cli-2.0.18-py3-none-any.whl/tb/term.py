import re
import sys
from io import UnsupportedOperation
from os.path import dirname, isdir, abspath, expanduser
from typing import Dict, List, Union

from prompt_toolkit import print_formatted_text, HTML, PromptSession, ANSI
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator, ValidationError
from tabulate import tabulate


class Objectview(object):
    def __init__(self, d):
        self.__dict__ = d


class ColoredTerminal:

    def __init__(self, theme=None, history_path='~/.tb/history.txt'):
        if theme is None:
            theme = {}
        self._history_path = history_path
        self._reset_prompt_session(history_path)

        self._styles = Style.from_dict(theme)

    def _reset_prompt_session(self, history_path):
        try:
            self._prompt = PromptSession()
            if history_path:
                history_path = expanduser(history_path)
                if isdir(dirname(history_path)):
                    self._prompt = PromptSession(
                        history=FileHistory(history_path),
                        auto_suggest=AutoSuggestFromHistory())
        except UnsupportedOperation:
            print("No terminal detected, prompts disabled")

    def h1(self, text):
        self.print("\n<h1>{}</h1>".format("=" * len(text)))
        self.print(f"<h2>{text}</h2>")
        self.print("<h1>{}</h1>\n".format("=" * len(text)))

    def h2(self, text):
        self.print(f"\n<h2>{text}</h2>")
        self.print("<h2>{}</h2>\n".format("-" * len(text)))

    def info(self, text):
        self.print(f"<info>{text}</info>")

    def warn(self, text):
        self.print(f"<warn>{text}</warn>")

    def error(self, text):
        self.print(f"<error>{text}</error>")

    def success(self, text):
        self.print(f"<success>{text}</success>")

    def columns(self, names, outputs, columns, report_format="{:24}{:^7}"):
        """Takes sorted names and corresponding output values"""
        self.print("<h3>{data}</h3>".format(data=report_format.format(*columns)))
        for name, output in sorted(zip(names, outputs)):
            color = "info" if not output else "error"
            self.print("<{c}>{text}</{c}>".format(text=report_format.format(name, output), c=color))

    def action(self, name, value):
        self.print(f"{name}: <h3>{value}</h3>")

    def print(self, orig_text, **kwargs):
        orig_text = orig_text.replace("&", "&amp;")
        print_formatted_text(HTML(orig_text), style=self._styles, **kwargs)

    def print_ansi(self, orig_text, **kwargs):
        if 'end' not in kwargs:
            kwargs['end'] = "\r\n"
        print(orig_text, **kwargs)

    def command(self, context, command_line):
        self.print(f"{context}: <cmd>{command_line}</cmd>")

    def yesno(self, text, default=False, *args, **kwargs):
        value = self.prompt(f"{text} [y/n]", *args,
                            **kwargs)
        return value.lower() == 'y'

    def prompt_int(self, text, *args, **kwargs):
        if 'default' in kwargs:
            kwargs['default'] = str(kwargs['default'])

        if 'validator' not in kwargs:
            kwargs['validator'] = NumberValidator()

        return int(self.prompt(text, *args, **kwargs))

    def prompt_float(self, text, *args, **kwargs):
        if 'default' in kwargs:
            kwargs['default'] = str(kwargs['default'])

        if 'validator' not in kwargs:
            kwargs['validator'] = NumberValidator()

        return float(self.prompt(text, *args, **kwargs))

    def prompt_menu(self, text, options: Union[List[str], Dict[str, str]], *args, **kwargs):
        self.h2(text)

        if isinstance(options, List):
            print(tabulate([[x, y] for x, y in enumerate(options, start=1)], tablefmt="github"))
            opts = [str(x) for x in range(1, len(options)+1)]
            result = int(self.prompt("> ", *args, options=opts, **kwargs))
            return options[result-1]
        else:
            print(tabulate([[x, y] for x, y in options.items()], tablefmt="github"))
            return self.prompt("> ", *args, options=options.keys(), **kwargs)

    def prompt(self, text, *args, **kwargs):
        text = f"<prompt>{text}</prompt> "
        if 'options' in kwargs and 'validator' not in kwargs and 'completer' not in kwargs:
            opts = kwargs['options']
            kwargs['validator'] = Validator.from_callable(
                lambda t: t in opts,
                error_message='Invalid option: must be one of {}'.format(opts),
                move_cursor_to_end=True)
            kwargs['completer'] = WordCompleter(opts)
            del kwargs['options']
        elif 'pattern' in kwargs and 'validator' not in kwargs:
            ptn = kwargs['pattern']
            kwargs['validator'] = Validator.from_callable(
                lambda t: re.fullmatch(ptn, t),
                error_message='Invalid pattern: must match {}'.format(ptn),
                move_cursor_to_end=True)
            del kwargs['pattern']

        val = self._prompt.prompt(HTML(text), *args, style=self._styles, **kwargs)

        # For some reason, passing in overrides modifies the session, so we need to reset
        if kwargs:
            self._reset_prompt_session(self._history_path)
        return val


class NumberValidator(Validator):
    def validate(self, document):
        text = document.text

        if text and not text.isdigit():
            i = 0

            # Get index of fist non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if not c.isdigit():
                    break

            raise ValidationError(message='This input contains non-numeric characters',
                                  cursor_position=i)
