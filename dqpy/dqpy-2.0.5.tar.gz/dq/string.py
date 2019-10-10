import random
import re

NAMESPACE = 'abcdefghijklmnopqrstuvwxyz1234567890'
PUNCS = '!"#$%&\'()*+,.:;<=>?@[\\]^_`{|}~'
TBL = dict.fromkeys(ord(i) for i in PUNCS)
SAFE_PATH = re.compile(r'^(?!(/|\.{2}))(?!.*/(\.*)(?:/.*|$)).*$')


def lower_no_punc(text):
    """Convert string to lowercase, stripping spaces and punctuations.

    :param string text: The text to clean up.
    :returns string: The cleaned up text.
    """
    # Strip whitespaces and convert to lowercase.
    return text.translate(TBL).strip().lower()


def random_string(length):
    """Get a random string of lowercase letters + numbers of the given length.

    :param int length: The desired length of the string.
    :returns string: A random string of the given length.
    """
    return ''.join(random.choice(NAMESPACE) for i in range(length))


def valid_filename(text):
    """Turn a string into a valid filename.

    :param string text: The string to convert.
    :returns string: A valid filename derived from the string.
    """
    text = text.strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', text)


def safe_relative_path(path):
    """Check whether a relative path is "safe".

    A path is safe if it is a relative path and doesn't contain . or ..'s.
    This prevents us from directory traversal attacks.

    Note that for simplicity, certain safe paths aren't allowed either, notably
    ... (e.g. .../path). Normal user should not really use such paths.

    :param string path: The path to check.
    :returns boolean: True if the path is safe, and False otherwise.
    """
    if not path or not isinstance(path, str):
        return False
    return bool(re.match(SAFE_PATH, path))
