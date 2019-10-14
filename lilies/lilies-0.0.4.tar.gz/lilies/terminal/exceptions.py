class UnsupportedStyleException(Exception):
    """
    Base exception when an unsupported style
    is encountered
    """

    pass


class UnsupportedColorException(UnsupportedStyleException):
    """
    Raised when a color has not been properly translated
    for the terminal before attempting rendering
    """

    pass


class UnsupportedAttributeException(UnsupportedStyleException):
    """
    Raised when an attribute is not supported by
    the current terminal but rendering was attempted
    """

    pass
