#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Colorful:

    def __init__(self):
        # Colors common
        self.n_black = '\033[0;30m'
        self.b_magenta = '\033[0;95m'
        self.b_blue = '\033[0;94m'
        self.b_green = '\033[0;92m'
        self.b_red = '\033[0;91m'
        self.b_yellow = '\033[0;93m'
        self.b_cyan = '\033[0;96m'
        self.b_white = '\033[0;97m'

        # For messagens
        self.warning = f'{self.b_yellow}⚠ '
        self.error = f'{self.b_red}✖ '
        self.finish = f'{self.b_green}✔ '
        self.reply = f'{self.b_magenta}➜ '
        self.starting = f'{self.b_blue}→ '
        self.reset = '\033[0m'

    def printc(self, function, text, *args, jump_line='\n'):
        if function == 'p' or function == 'P':
            return print(f'{args[0]}{text}{self.reset}')
        elif function == 't' or function == 'T':
            return f'{args}{text}{self.reset}'
        elif function == 'i' or function == 'I':
            # noinspection PyBroadException
            try:
                return input(f'{self.reply}{text}{jump_line}> {self.reset}')
            except Exception:
                msg = 'There was a return error in the input of function "printc".'
                print(f'{jump_line}{self.error}{msg}{self.reset}')
        else:
            raise Exception('Colorful error parameter "function printc".')
