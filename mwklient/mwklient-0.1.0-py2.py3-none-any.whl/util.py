"""The util module provides some common helper functions and wrappers,
to parse timestamps, read streams in chunks, etc.
"""

from io import BytesIO
from time import strptime, struct_time
import mwklient.errors as errors


def version_tuple_from_generator(string, prefix='MediaWiki '):
    """Return a version tuple from a MediaWiki Generator string.

    Example:
        "MediaWiki 1.5.1" → (1, 5, 1)

    Args:
        prefix (str): The expected prefix of the string
    """
    if not string.startswith(prefix):
        raise errors.MediaWikiVersionError(
            'Unknown generator {}'.format(string))

    version = string[len(prefix):].split('.')

    def split_num(s):
        """Split the string on the first non-digit character.

        Returns:
            A tuple of the digit part as int and, if available,
            the rest of the string.
        """
        i = 0
        while i < len(s):
            if s[i] < '0' or s[i] > '9':
                break
            i += 1
        if s[i:]:
            return (int(s[:i]), s[i:], )
        return (int(s[:i]), )

    version_tuple = sum((split_num(s) for s in version), ())

    if len(version_tuple) < 2:
        raise errors.MediaWikiVersionError('Unknown MediaWiki {}'
                                           .format('.'.join(version)))

    return version_tuple


def strip_namespace(title):
    if title[0] == ':':
        title = title[1:]
    return title[title.find(':') + 1:]


def normalize_title(title):
    # TODO: Make site dependent
    title = title.strip()
    if title[0] == ':':
        title = title[1:]
    title = title[0].upper() + title[1:]
    title = title.replace(' ', '_')
    return title


def parse_timestamp(timestamp):
    """Parses a string to a time tuple.

    Args:
        timestamp: A string fomrttaed as formatted as '%Y-%m-%dT%H:%M:%SZ'; if
        None, it is considered as '0000-00-00T00:00:00Z'.

    Returns:
        a time tuple (struct_time)

    Raises:
    """
    if not timestamp or timestamp == '0000-00-00T00:00:00Z':
        return struct_time((0, 0, 0, 0, 0, 0, 0, 0, 0))
    return strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')


def read_in_chunks(stream, chunk_size):
    """Reads from a buffer in chunks.

    Args:
        stream: The underlying buffer to read.
        chunk_size: number of characters to read each time; if it is negative,
        the full buffer is read, untile EOF.

    Returns:
        bytes

    Raises:
    """
    while True:
        data = stream.read(chunk_size)
        if not data:
            break
        yield BytesIO(data)
