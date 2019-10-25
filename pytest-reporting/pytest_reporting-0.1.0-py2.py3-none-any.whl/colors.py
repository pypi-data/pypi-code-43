# -*- coding: utf-8 -*-

from functools import partial

from colorama import Fore, Style


# TODO: ability to chain modifiers
class _Modifier(object):
    def __init__(self, msg, modifier):
        self.modifier = modifier
        self.chain = msg

    def __str__(self):
        return self.modifier + self.chain + Style.RESET_ALL


red = partial(_Modifier, modifier=Fore.RED)
green = partial(_Modifier, modifier=Fore.GREEN)
yellow = partial(_Modifier, modifier=Fore.YELLOW)

bold = partial(_Modifier, modifier=Style.BRIGHT)
dim = partial(_Modifier, modifier=Style.DIM)
