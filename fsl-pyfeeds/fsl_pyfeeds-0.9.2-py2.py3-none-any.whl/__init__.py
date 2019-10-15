#!/usr/bin/env python
#
# __init__.py - The pyfeeds package.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

__version__ = '0.9.2'
"""The pyfeeds version number. """


from .common import (
    fslbin,
    readfsf,
    writefsf,
)


from .evaluate import (
    evalImage,
    evalNumericalText,
    evalVectorImage,
    evalMD5
)
