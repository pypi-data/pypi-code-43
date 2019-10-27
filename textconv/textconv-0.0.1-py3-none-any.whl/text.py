"""converting a string to a byte string or a text string
"""
from typing import Union

_COMPOSED_ERROR_HANDLERS = frozenset((None, 'surrogate_then_replace'))


def to_bytes(obj, encoding: str='utf-8', errors: Union[None, str]=None, nonstring: str='simplerepr'):
    """Convert a string to a byte string

    :arg obj: An object to make sure is a byte string.  In most cases this
        will be either a text string or a byte string.
    :kwarg encoding: The encoding to use to convert a text string to
        a byte string.  Defaults to 'utf-8'.
    :kwarg errors: The error handler to use if the text string can not be
        encoded using the specified encoding.  Any valid `codecs error
        handler <https://docs.python.org/3/library/codecs.html#error-handlers>`
        may be specified. There is an additional error strategy
        specifically aimed at raise-free encoding:

            :surrogate_then_replace: If encoding with ``surrogateescape`` would raise,
                surrogates are first replaced with a replacement characters
                and then the string is encoded using ``replace`` (which replaces
                the rest of the bytes that won't encode).  This strategy is designed
                to never raise when it attempts to encode a string.

    :kwarg nonstring: The strategy to use if a nonstring is specified in
        ``obj``.  Default is 'simplerepr'.  Valid values are:

            :simplerepr: Take the ``str`` representation of the object and
                then returns the bytes version of that string.
            :empty: Return an empty byte string
            :passthru: Return the obj passed in as-is
            :strict: Raise `TypeError`

    :returns: Returns a byte string.  If a nonstring object is
        passed in this may be a different type depending on the strategy
        specified by `nonstring`.

    .. note:: If passed a byte string, this function does not check that the
        string is valid in the specified encoding.  If it's important that the
        byte string is in the specified encoding do::

            encoded_string = to_bytes(to_text(input_string, 'latin-1'), 'utf-8')
    """
    if isinstance(obj, bytes):
        return obj

    original_errors = errors
    if errors in _COMPOSED_ERROR_HANDLERS:
        errors = 'surrogateescape'

    if isinstance(obj, str):
        try:
            # Try this first as it's the fastest
            return obj.encode(encoding, errors)
        except UnicodeEncodeError:
            if original_errors in _COMPOSED_ERROR_HANDLERS:
                # Slow but works
                return_string = obj.encode('utf-8', 'surrogateescape')
                # Replace surrogates with u'\uFFFD'('?' when encoding)
                return_string = return_string.decode('utf-8', 'replace')
                return return_string.encode(encoding, 'replace')
            raise

    if nonstring == 'simplerepr':
        try:
            value = str(obj)
        except UnicodeError:
            try:
                value = repr(obj)
            except UnicodeError:
                # Give up
                return b''
    elif nonstring == 'passthru':
        return obj
    elif nonstring == 'empty':
        return b''
    elif nonstring == 'strict':
        raise TypeError('obj must be a string type')
    else:
        raise TypeError('Invalid value %s for to_bytes\' nonstring parameter' % nonstring)

    return to_bytes(value, encoding, errors)


def to_text(obj, encoding :str='utf-8', errors: Union[None, str]=None, nonstring :str='simplerepr'):
    """Convert a string to a text string

    :arg obj: An object to make sure is a text string.  In most cases this
        will be either a text string or a byte string.  However, with
        ``nonstring='simplerepr'``, this can be used as a raise-free
        version of ``str(obj)``.
    :kwarg encoding: The encoding to use to transform from a byte string to
        a text string.  Defaults to using 'utf-8'.
    :kwarg errors: The error handler to use if the byte string can not be
        decoded using the specified encoding.  Any valid `codecs error
        handler <https://docs.python.org/3/library/codecs.html#error-handlers>`
        may be specified.

    :kwarg nonstring: The strategy to use if a nonstring is specified in
        ``obj``.  Default is 'simplerepr'.  Valid values are:

            :simplerepr: Take the ``str`` representation of the object and
                then return the text version of that string.
            :empty: Return an empty text string
            :passthru: Return the object passed in
            :strict: Raise a `TypeError`

    :returns: Typically this returns a text string.  If a nonstring object is
        passed in this may be a different type depending on the strategy
        specified by `nonstring`.
    """
    if isinstance(obj, str):
        return obj

    if errors in _COMPOSED_ERROR_HANDLERS:
        errors = 'surrogateescape'

    if isinstance(obj, bytes):
        # Note: Don't need special handling for 'surrogate_then_replace'
        # because all bytes will either be made into surrogates or are valid
        # to decode.
        return obj.decode(encoding, errors)

    if nonstring == 'simplerepr':
        try:
            value = str(obj)
        except UnicodeError:
            try:
                value = repr(obj)
            except UnicodeError:
                # Give up
                return ''
    elif nonstring == 'passthru':
        return obj
    elif nonstring == 'empty':
        return ''
    elif nonstring == 'strict':
        raise TypeError('obj must be a string type')
    else:
        raise TypeError('Invalid value %s for to_text\'s nonstring parameter' % nonstring)

    return to_text(value, encoding, errors)
