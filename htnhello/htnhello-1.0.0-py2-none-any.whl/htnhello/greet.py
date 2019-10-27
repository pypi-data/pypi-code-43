r"""
Test module uploading to PyPI.
"""


class Category(object):
    r"""
    Holds a message represented by a single string.
    """

    def __init__(self, message):
        r"""
        Create an instance to hold the message.
        :param  message:    Single string message.
        """
        self.message = message

    def show(self):
        r"""
        Displays holding messages on stdout.
        """
        print(self.message)


def hello():
    r"""
    Display [Hello, World.].
    """
    print('Hello, World.')
