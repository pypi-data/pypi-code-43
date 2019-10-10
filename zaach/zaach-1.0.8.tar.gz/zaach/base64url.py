import base64


def encode(unencoded):
    """
    Encodes the argument to be safe to use in an URL and a filename.

    See RFC 4648, Section 5 "Base 64 Encoding with URL and Filename
    Safe Alphabet" for details.
    """
    return base64.b64encode(unencoded.encode('utf-8')) \
           .decode('utf-8') \
           .rstrip('=') \
           .replace('+', '-') \
           .replace('/', '_')


def decode(encoded):
    """
    Decodes the argument.

    See RFC 4648, Section 5 "Base 64 Encoding with URL and Filename
    Safe Alphabet" for details.
    """
    return base64.b64decode(
        '{}{}'.format(
            encoded.replace('-', '+').replace('_', '/'),
            ((-1 * len(encoded)) % 4) * '='
        )
    ).decode('utf-8')
