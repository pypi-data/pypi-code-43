import itertools

import pytest

from textconv.text import to_text, to_bytes


# Format: byte representation, text representation, encoding of byte representation
VALID_STRINGS = (
    (b'abcde', u'abcde', 'ascii'),
    # u'café'
    (b'caf\xc3\xa9', u'caf\xe9', 'utf-8'),
    (b'caf\xe9', u'caf\xe9', 'latin-1'),
    # u'Россия'
    (b'\xd0\xa0\xd0\xbe\xd1\x81\xd1\x81\xd0\xb8\xd1\x8f', u'\u0420\u043e\u0441\u0441\u0438\u044f', 'utf-8'),
)


@pytest.mark.parametrize('in_string, encoding, expected',
                         itertools.chain(((d[0], d[2], d[1]) for d in VALID_STRINGS),
                                         ((d[1], d[2], d[1]) for d in VALID_STRINGS)))
def test_to_text(in_string, encoding, expected):
    """test happy path of decoding to text"""
    assert to_text(in_string, encoding) == expected


@pytest.mark.parametrize('in_string, encoding, expected',
                         itertools.chain(((d[0], d[2], d[0]) for d in VALID_STRINGS),
                                         ((d[1], d[2], d[0]) for d in VALID_STRINGS)))
def test_to_bytes(in_string, encoding, expected):
    """test happy path of encoding to bytes"""
    assert to_bytes(in_string, encoding) == expected
