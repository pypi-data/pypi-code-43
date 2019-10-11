# -*- coding: utf-8 -*-
__author__ = 'bars'

import sys


class ParseFilterfile():

    """Docstring for ParseFilterfile. """

    def __init__(self, filterfile):
        """TODO: to be defined1. """
        self.filterfile = filterfile

    def parsefilfil(self):
        fargs = {}
        with open(self.filterfile) as filfil:
            readfil = filfil.read()
            readfil = readfil.split('\n')
            for fil in readfil:
                if not fil.startswith('#'):
                    fargs[fil.split(' ')[0]] = fil.split(' ')[1:]

        if not 'filterfile' in fargs.keys():
            sys.exit('Check filter file.')
        return fargs
