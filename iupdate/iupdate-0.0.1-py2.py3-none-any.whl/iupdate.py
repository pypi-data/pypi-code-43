#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .lib.ansi_code import AnsiCode
# from getpass import getpass
from subprocess import run, PIPE, STDOUT


class IUpdate:
    def __init__(self):
        self.name_prog = 'iUpdate'

    @staticmethod
    def system():
        print('[Run iUpdate]')
        print('Warning! Sorry, this package is under construction')
