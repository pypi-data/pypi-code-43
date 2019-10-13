# -*- coding: utf-8 -*-
"""Person class file."""


class Person(object):
    """Person class."""

    def __init__(self, record):
        """Initialize a class instance."""
        self.record = record

    def __str__(self):
        """Output readable string."""
        return '%s, %s [%s]' % (
            self.record['last_name'],
            self.record['first_name'],
            self.record['emplid'],
        )
