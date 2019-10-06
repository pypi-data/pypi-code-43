"""Non-Blocking Stream Reader

This package is to address the issue described in Stack Overflow article
`Non-blocking read on a subprocess.PIPE in python`_. I.e. this package provides
a sort-of stream class with the following attributes:

- where reading functions can have timeouts,
- it works on Windows too,
- it works on Python 2.7, as well as Python 3.7

Additionally, it supports interactions, e.g. it can identify remote output
patterns (like a prompt) so that whey can be reacted on (like sending a command)
in optimized time.

.. _Non-blocking read on a subprocess.PIPE in python:
    https://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
"""
#import the main module with the class and all exceptions and 'returnby' values
from .nonblocking_reader import NonBlockingStreamReader
from .exceptions import *
from .returnbys import *
