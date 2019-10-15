#!/usr/bin/env python
# -*- coding: utf-8 -*-


class AnsiCode:

    def __init__(self):
        self.warning = '\033[0;93m⚠ '
        self.error = '\033[0;91m✖ '
        self.finish = '\033[0;92m✔ '
        self.reply = '\033[0;95m→ '
        self.header = '\033[0;95m '
        self.reset = '\033[0m'

    def message(self, function, style, message, jumpline='\n'):
        if function == 'print':
            return print(f'{style}{message}{self.reset}')
        elif function == 'input':
            try:
                return input(f'{style}{message}{jumpline}>> {self.reset}')
            except KeyboardInterrupt:
                print(f'{jumpline}{self.warning}Aborted by user.{self.reset}')
