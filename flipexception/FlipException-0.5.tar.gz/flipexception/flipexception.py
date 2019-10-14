#!/usr/bin/env python
# -*- coding: utf-8 -*-

import upsidedown

__version__ = 0.5

class FlipException(Exception):

    @staticmethod
    def flip_text(message=None):
        if not message:
            message = "┻━┻"
        else:
            message = upsidedown.transform(message)

        return str("(╯°□°）╯︵ " + message)


    def __init__(self, message=None):
        message = self.flip_text(message)
        super(Exception, self).__init__(message)
