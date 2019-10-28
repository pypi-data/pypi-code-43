#!win10_x64 python3.6
# coding: utf-8
# Date: 2019/10/27
# wbq813@foxmail.com
import logging
import re
from urllib.parse import urlencode
import html.entities as htmlentities


unicode_char = chr
long = int

DATETIME_REGEX = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})(\.\d+)?Z$"
    # NOQA: E501
)
# dict key used to add nested documents to a document
NESTED_DOC_KEY = "_childDocuments_"


def force_unicode(value):
    """
    Forces a bytestring to become a Unicode string.
    """
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    elif not isinstance(value, str):
        value = str(value)

    return value


def force_bytes(value):
    """
    Forces a Unicode string to become a bytestring.
    """
    if isinstance(value, str):
        value = value.encode("utf-8", "backslashreplace")

    return value


def unescape_html(text):
    """
    Removes HTML or XML character references and entities from a text string.

    @param text The HTML (or XML) source text.
    @return The plain text, as a Unicode string, if necessary.

    Source: http://effbot.org/zone/re-sub.htm#unescape-html
    """

    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unicode_char(int(text[3:-1], 16))
                else:
                    return unicode_char(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unicode_char(htmlentities.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is

    return re.sub(r"&#?\w+;", fixup, text)


def safe_urlencode(params, doseq=0):
    """
    UTF-8-safe version of safe_urlencode

    The stdlib safe_urlencode prior to Python 3.x chokes on UTF-8 values
    which can't fail down to ascii.
    """
    return urlencode(params, doseq)


def is_valid_xml_char_ordinal(i):
    """
    Defines whether char is valid to use in xml document

    XML standard defines a valid char as::

    Char ::= #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
    """
    # conditions ordered by presumed frequency
    return (
            0x20 <= i <= 0xD7FF
            or i in (0x9, 0xA, 0xD)
            or 0xE000 <= i <= 0xFFFD
            or 0x10000 <= i <= 0x10FFFF
    )


def clean_xml_string(s):
    """
    Cleans string from invalid xml chars

    Solution was found there::

    http://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python
    """
    return "".join(c for c in s if is_valid_xml_char_ordinal(ord(c)))


# Using two-tuples to preserve order.
REPLACEMENTS = (
    # Nuke nasty control characters.
    (b"\x00", b""),  # Start of heading
    (b"\x01", b""),  # Start of heading
    (b"\x02", b""),  # Start of text
    (b"\x03", b""),  # End of text
    (b"\x04", b""),  # End of transmission
    (b"\x05", b""),  # Enquiry
    (b"\x06", b""),  # Acknowledge
    (b"\x07", b""),  # Ring terminal bell
    (b"\x08", b""),  # Backspace
    (b"\x0b", b""),  # Vertical tab
    (b"\x0c", b""),  # Form feed
    (b"\x0e", b""),  # Shift out
    (b"\x0f", b""),  # Shift in
    (b"\x10", b""),  # Data link escape
    (b"\x11", b""),  # Device control 1
    (b"\x12", b""),  # Device control 2
    (b"\x13", b""),  # Device control 3
    (b"\x14", b""),  # Device control 4
    (b"\x15", b""),  # Negative acknowledge
    (b"\x16", b""),  # Synchronous idle
    (b"\x17", b""),  # End of transmission block
    (b"\x18", b""),  # Cancel
    (b"\x19", b""),  # End of medium
    (b"\x1a", b""),  # Substitute character
    (b"\x1b", b""),  # Escape
    (b"\x1c", b""),  # File separator
    (b"\x1d", b""),  # Group separator
    (b"\x1e", b""),  # Record separator
    (b"\x1f", b""),  # Unit separator
)


def sanitize(data):
    fixed_string = force_bytes(data)

    for bad, good in REPLACEMENTS:
        fixed_string = fixed_string.replace(bad, good)

    return force_unicode(fixed_string)

def get_logger(sub):
    logging.getLogger(sub)
