"""
This is module should not import any other runez module, it's the lowest on the import chain
"""

import os
import re
import sys

from runez.base import string_type, stringified, UNSET


DEFAULT_BASE = 1000
DEFAULT_UNITS = "kmgt"
RE_FORMAT_MARKERS = re.compile(r"{([^}]*?)}")
RE_WORDS = re.compile(r"[^\w]+")
RE_SPACES = re.compile(r"[\s\n]+", re.MULTILINE)
RE_UNDERSCORED_NUMBERS = re.compile(r"([0-9])_([0-9])")  # py2 does not parse numbers with underscores like "1_000"
SYMBOLIC_TMP = "<tmp>"
TRUE_TOKENS = {"on", "true", "y", "yes"}

SANITIZED = 1
SHELL = 2
UNIQUE = 4


def capped(value, minimum=None, maximum=None):
    """
    Args:
        value: Value to cap
        minimum: If specified, value should not be lower than this minimum
        maximum: If specified, value should not be higher than this maximum

    Returns:
        `value` capped to `minimum` and `maximum` (if it is outside of those bounds)
    """
    if value is not None:
        if minimum is not None and value < minimum:
            return minimum

        if maximum is not None and value > maximum:
            return maximum

    return value


def flattened(value, split=None):
    """
    Args:
        value: Possibly nested arguments (sequence of lists, nested lists)
        split (int | str | unicode | (str | unicode | None, int) | None): How to split values:
            - None: simply flatten, no further processing
            - one char string: split() on specified char
            - SANITIZED: discard all None items
            - UNIQUE: each value will appear only once
            - SHELL:  filter out sequences of the form ["-f", None] (handy for simplified cmd line specification)

    Returns:
        list: 'value' flattened out (leaves from all involved lists/tuples)
    """
    result = []
    separator = None
    mode = 0
    if isinstance(split, tuple):
        separator, mode = split
    elif isinstance(split, int):
        mode = split
    else:
        separator = split
    _flatten(result, value, separator, mode)
    return result


def formatted(text, *args, **kwargs):
    """
    Args:
        text (str | unicode): Text to format
        *args: Objects to extract values from (as attributes)
        **kwargs: Optional values provided as named args

    Returns:
        (str): Attributes from this class are expanded if mentioned
    """
    if not text or "{" not in text:
        return text
    strict = kwargs.pop("strict", True)
    max_depth = kwargs.pop("max_depth", 3)
    objects = list(args) + [kwargs] if kwargs else args[0] if len(args) == 1 else args
    if not objects:
        return text
    definitions = {}
    markers = RE_FORMAT_MARKERS.findall(text)
    while markers:
        key = markers.pop()
        if key in definitions:
            continue
        val = _find_value(key, objects)
        if strict and val is None:
            return None
        val = stringified(val) if val is not None else "{%s}" % key
        markers.extend(m for m in RE_FORMAT_MARKERS.findall(val) if m not in definitions)
        definitions[key] = val
    if not max_depth or not isinstance(max_depth, int) or max_depth <= 0:
        return text
    expanded = dict((k, _rformat(k, v, definitions, max_depth)) for k, v in definitions.items())
    return text.format(**expanded)


def quoted(text):
    """
    Args:
        text (str | unicode | None): Text to optionally quote

    Returns:
        (str): Quoted if 'text' contains spaces
    """
    if text and " " in text:
        sep = "'" if '"' in text else '"'
        return "%s%s%s" % (sep, text, sep)
    return text


def represented_args(args, separator=" "):
    """
    Args:
        args (list | tuple | None): Arguments to represent
        separator (str | unicode): Separator to use

    Returns:
        (str): Quoted as needed textual representation
    """
    result = []
    if args:
        for text in args:
            result.append(quoted(short(text)))
    return separator.join(result)


def resolved_path(path, base=None):
    """
    Args:
        path (str | unicode | None): Path to resolve
        base (str | unicode | None): Base path to use to resolve relative paths (default: current working dir)

    Returns:
        (str): Absolute path
    """
    if not path or path.startswith(SYMBOLIC_TMP):
        return path

    path = os.path.expanduser(path)
    if base and not os.path.isabs(path):
        return os.path.join(resolved_path(base), path)

    return os.path.abspath(path)


def short(path):
    """
    Args:
        path (str): Path to textually represent in a shortened (yet meaningful) form

    Returns:
        (str): Shorter version of `path` (relative to one of the current anchor folders)
    """
    return Anchored.short(path)


def shortened(value, size=120):
    """
    Args:
        value: Value to textually represent within `size` characters (stringified if necessary)
        size (int): Max chars

    Returns:
        (str): Leading part of 'text' with at most 'size' chars
    """
    text = stringified(value, converter=_prettified).strip()
    text = RE_SPACES.sub(" ", text)
    if len(text) > size:
        return "%s..." % text[:size - 3]
    return text


def to_float(value, lenient=False, default=None):
    """
    Args:
        value: Value to convert to float
        lenient (bool): If True, returned number is returned as an `int` if possible first, float otherwise
        default: Default to return when value can't be converted

    Returns:
        (float | int | None): Extracted float if possible, otherwise `None`
    """
    if isinstance(value, string_type):
        return _float_from_text(value, lenient=lenient, default=default)

    if lenient:
        try:
            return int(value)

        except (TypeError, ValueError):
            pass

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def to_int(value, default=None):
    """
    Args:
        value: Value to convert to int
        default: Default to return when value can't be converted

    Returns:
        (int | None): Extracted int if possible, otherwise `None`
    """
    if isinstance(value, string_type):
        return _int_from_text(value, default=default)

    try:
        return int(value)

    except (TypeError, ValueError):
        return default


def to_number(value, default=None):
    """
    Args:
        value: Value to convert to number
        default: Default to return when value can't be converted

    Returns:
        (int | float | None): Extracted number if possible, otherwise `None`
    """
    return to_float(value, lenient=True, default=default)


class Anchored(object):
    """
    An "anchor" is a known path that we don't wish to show in full when printing/logging
    This allows to conveniently shorten paths, and show more readable relative paths
    """

    paths = []  # Folder paths that can be used to shorten paths, via short()
    home = os.path.expanduser("~")

    def __init__(self, folder):
        self.folder = resolved_path(folder)

    def __enter__(self):
        Anchored.add(self.folder)

    def __exit__(self, *_):
        Anchored.pop(self.folder)

    @classmethod
    def set(cls, *anchors):
        """
        Args:
            *anchors (str | unicode | list): Optional paths to use as anchors for short()
        """
        cls.paths = sorted(flattened(anchors, split=SANITIZED | UNIQUE), reverse=True)

    @classmethod
    def add(cls, anchors):
        """
        Args:
            anchors (str | unicode | list): Optional paths to use as anchors for short()
        """
        cls.set(cls.paths, anchors)

    @classmethod
    def pop(cls, anchors):
        """
        Args:
            anchors (str | unicode | list): Optional paths to use as anchors for short()
        """
        for anchor in flattened(anchors, split=SANITIZED | UNIQUE):
            if anchor in cls.paths:
                cls.paths.remove(anchor)

    @classmethod
    def short(cls, path):
        """
        Example:
            short("examined /Users/joe/foo") => "examined ~/foo"

        Args:
            path: Path to represent in its short form

        Returns:
            (str): Short form, using '~' if applicable
        """
        if path is None:
            return path

        path = stringified(path)
        if cls.paths:
            for p in cls.paths:
                if p:
                    path = path.replace(p + "/", "")

        path = path.replace(cls.home, "~")
        return path


def affixed(text, prefix=None, suffix=None, normalize=None):
    """
    Args:
        text (str | None): Text to ensure prefixed
        prefix (str | None): Prefix to add (if not already there)
        suffix (str | None): Suffix to add (if not already there)
        normalize (callable | None): Optional function to apply to `text`

    Returns:
        (str | None): `text' guaranteed starting with `prefix` and ending with `suffix`
    """
    if text is not None:
        if normalize:
            text = normalize(text)

        if prefix and not text.startswith(prefix):
            text = prefix + text

        if suffix and not text.endswith(suffix):
            text = text + suffix

    return text


def camel_cased(text, separator=""):
    """
    Args:
        text (str): Text to camel case
        separator (str): Separator to use

    Returns:
        (str): Camel-cased text
    """
    return wordified(text, separator=separator, normalize=str.title)


def entitled(text, separator=" "):
    """
    Args:
        text (str): Text to turn into title
        separator (str): Separator to use

    Returns:
        (str): First letter (of 1st word only) upper-cased
    """
    words = get_words(text)
    if words:
        words[0] = words[0].title()
    return separator.join(words)


def get_words(text, normalize=None):
    """
    Args:
        text (str | None): Text to extract words from
        normalize (callable | None): Optional function to apply on each word

    Returns:
        (list | None): Words, if any
    """
    if not text:
        return []

    words = [s.strip().split("_") for s in RE_WORDS.split(text)]
    words = [s for s in flattened(words) if s]
    if normalize:
        words = [normalize(s) for s in words]
    return words


def snakified(text, normalize=str.upper):
    """
    Args:
        text (str): Text to transform
        normalize (callable | None): Optional function to apply on each word

    Returns:
        (str | None): Upper-cased and snake-ified
    """
    return wordified(text, normalize=normalize)


def wordified(text, separator="_", normalize=None):
    """
    Args:
        text (str | None): Text to process as words
        separator (str): Separator to use to join words back
        normalize (callable | None): Optional function to apply on each word

    Returns:
        (str): Dashes replaced by underscore
    """
    if text is None:
        return None

    return separator.join(get_words(text, normalize=normalize))


def unitized(value, unit, base=DEFAULT_BASE, unitseq=DEFAULT_UNITS):
    """
    Args:
        value (int | float): Value to expand
        unit (str | unicode): Given unit
        base (int): Base to use (usually 1024)
        unitseq (str): Sequence of 1-letter representation for each exponent level

    Returns:
        Deduced value (example: "1k" becomes 1000)
    """
    exponent = _get_unit_exponent(unit, unitseq)
    if exponent is not None:
        return int(value * (base ** exponent))


def _get_unit_exponent(unit, unitseq, default=None):
    try:
        return 0 if not unit else unitseq.index(unit) + 1

    except ValueError:
        return default


def _rformat(key, value, definitions, max_depth):
    if max_depth > 1 and value and "{" in value:
        value = value.format(**definitions)
        return _rformat(key, value, definitions, max_depth=max_depth - 1)
    return value


def _flatten(result, value, separator, mode):
    """
    Args:
        result (list): Will hold all flattened values
        value: Possibly nested arguments (sequence of lists, nested lists)
        separator (str | unicode | None): Split values with `separator` if specified
        mode (int): Describes how keep flattenened values

    Returns:
        list: 'value' flattened out (leaves from all involved lists/tuples)
    """
    if value is None or value is UNSET:
        if mode & SHELL:
            # Convenience: allow to filter out ["--switch", None] easily
            if result and result[-1].startswith("-"):
                result.pop(-1)
            return

        if mode & SANITIZED:
            return

    if value is not None:
        if isinstance(value, (list, tuple, set)):
            for item in value:
                _flatten(result, item, separator, mode)
            return

        if separator and hasattr(value, "split") and separator in value:
            _flatten(result, value.split(separator), separator, mode)
            return

        if mode & SHELL:
            value = "%s" % value

    if (mode & UNIQUE == 0) or value not in result:
        result.append(value)


def _get_value(obj, key):
    """Get a value for 'key' from 'obj', if possible"""
    if obj is not None:
        if isinstance(obj, (list, tuple)):
            for item in obj:
                v = _find_value(key, item)
                if v is not None:
                    return v
            return None
        if hasattr(obj, "get"):
            return obj.get(key)
        return getattr(obj, key, None)


def _find_value(key, *args):
    """Find a value for 'key' in any of the objects given as 'args'"""
    for arg in args:
        v = _get_value(arg, key)
        if v is not None:
            return v


def _int_from_text(text, base=None, default=None):
    """
    Args:
        text (str): Text to convert to int
        base (int | None): Base to use (managed internally, no need to specify)
        default: Default to return when value can't be converted

    Returns:
        (int | None): Extracted int if possible, otherwise `None`
    """
    try:
        if base is None:
            return int(text)

        return int(text, base=base)

    except ValueError:
        if base is None:
            if sys.version_info[:2] <= (3, 5):
                # 3.5 has the same quirk as 2.7
                text = RE_UNDERSCORED_NUMBERS.sub(r"\1\2", text)
                try:
                    return int(text)

                except ValueError:
                    pass

            if len(text) >= 3 and text[0] == "0":
                if text[1] == "o":
                    return _int_from_text(text, base=8, default=default)

                if text[1] == "x":
                    return _int_from_text(text, base=16, default=default)

    return default


def _float_from_text(text, lenient=True, default=None):
    """
    Args:
        text (str): Text to convert to float (yaml-like form ".inf" also accepted)
        lenient (bool): If True, returned number is returned as an `int` if possible first, float otherwise
        default: Default to return when value can't be converted

    Returns:
        (float | None): Extracted float if possible, otherwise `None`
    """
    value = _int_from_text(text, default=default)  # Allows to also support hex/octal numbers
    if value is not None:
        return value if lenient else float(value)

    try:
        return float(text)

    except ValueError:
        if len(text) >= 3 and text[-1] in "fF" and (text[0] == "." or text[1] == "."):
            try:
                return float(text.replace(".", "", 1))  # Edge case: "[+-]?.inf"

            except ValueError:
                pass

    return default


def _prettified(value):
    if isinstance(value, list):
        return "[%s]" % ", ".join(stringified(s, converter=_prettified) for s in value)

    if isinstance(value, tuple):
        return "(%s)" % ", ".join(stringified(s, converter=_prettified) for s in value)

    if isinstance(value, dict):
        keys = sorted(value, key=lambda x: "%s" % x)
        pairs = ("%s: %s" % (stringified(k, converter=_prettified), stringified(value[k], converter=_prettified)) for k in keys)
        return "{%s}" % ", ".join(pairs)

    if isinstance(value, set):
        return "{%s}" % ", ".join(stringified(s, converter=_prettified) for s in sorted(value, key=lambda x: "%s" % x))

    if isinstance(value, type):
        return "class %s.%s" % (value.__module__, value.__name__)

    if callable(value):
        return "function '%s'" % value.__name__
