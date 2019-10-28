import functools
import string

HEXLIFY_CHARS = "0123456789abcdefABCDEF"
URLSAFEB64_CHARS = "-0123456789=ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz\r\n"
BASE64_CHARS = "+/0123456789=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz\r\n"


def wholestrip(text):
    """Remove all white spaces in text. White spaces are ' \t\n\r\x0b\x0c\u3000'.
    """
    for space in string.whitespace + '\u3000':
        text = text.replace(space, "")
    return text


def split(text, seps, strip=False):
    """seps is a list of string, all sep in the seps are treated as delimiter.
    """
    if not isinstance(seps, (list, set, tuple)):
        seps = [seps]
    results = [text]
    for sep in seps:
        row = []
        for value in results:
            row += value.split(sep)
        results = row
    if strip:
        row = []
        for value in results:
            row.append(value.strip())
        results = row
    return results


def str_composed_by(text, choices):
    """Test if text is composed by chars in the choices.
    """
    for char in text:
        if not char in choices:
            return False
    return True

is_str_composed_by_the_choices = str_composed_by


def is_hex_digits(text):
    """Test if all chars in text is hex digits.
    """
    if not text:
        return False
    return str_composed_by(text, HEXLIFY_CHARS)

def join_lines(text):
    """Join multi-lines into single line.
    """
    return "".join(text.splitlines())


def is_urlsafeb64_decodable(text):
    """Test if the text can be decoded by urlsafeb64 method.
    """
    text = wholestrip(text)
    if not text:
        return False
    if len(text) % 4 != 0:
        return False
    return str_composed_by(join_lines(text), URLSAFEB64_CHARS)


def is_base64_decodable(text):
    """Test  if the text can be decoded by base64 method.
    """
    text = wholestrip(text)
    if not text:
        return False
    if len(text) % 4 != 0:
        return False
    return str_composed_by(join_lines(text), BASE64_CHARS)


def is_unhexlifiable(text):
    """Test if the text can be decoded by unhexlify method.
    """
    text = wholestrip(text)
    if not text:
        return False
    if len(text) % 2 != 0:
        return False
    return str_composed_by(text, HEXLIFY_CHARS)


def text_display_length(text, unicode_display_length=2):
    """Get text display length.
    """
    length = 0
    for c in text:
        if ord(c) <= 128:
            length += 1
        else:
            length += unicode_display_length
    return length

def text_display_shorten(text, max_length, unicode_display_length=2, suffix="..."):
    """Shorten text to fix the max display length.
    """
    if max_length < len(suffix):
        max_length = len(suffix)
    tlen = text_display_length(text, unicode_display_length=unicode_display_length)
    if tlen <= max_length:
        return text
    result = ""
    tlen = 0
    max_length -= len(suffix)
    for c in text:
        if ord(c) <= 128:
            tlen += 1
        else:
            tlen += unicode_display_length
        if tlen < max_length:
            result += c
        elif tlen == max_length:
            result += c
            break
        else:
            break
    result += suffix
    return result
