"""
Common exception classes
"""


class GenericException(Exception):
    message = None

    def __init__(self):
        super(GenericException, self).__init__(self.message)
