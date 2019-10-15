"""LPTrack is a library for encoding and decoding LavaPlayer's base 64 track
representation.

The library provides the two simple methods `decode` and `encode` which convert
from `Track` instances to their encoded representation and vice versa.

If you want to go deeper you can use the `TrackDecoder` and `TrackEncoder` classes
directly.
"""

import base64
import io
from typing import Union

from . import codec, strcodec
from .sources import *
from .track import *
from .versions import LATEST_VERSION

# needs to come after track import
from .format import *

__author__ = "Giesela Inc."
__version__ = "1.0.0"


def decode(data: Union[str, bytes], *, string_codec: strcodec.Codec = None) -> Track:
    """Decode a base 64 string or bytes to a track.

    Args:
        data: Base 64 track data as used in LavaPlayer to decode.
        string_codec: String codec to use for decoding strings.

    Returns:
        Track information contained in the encoded data.
        The version attribute of the returned `Track` will reflect
        the version of the data format.
    """
    decoded = base64.b64decode(data)
    stream = codec.MessageInput(io.BytesIO(decoded), string_codec=string_codec)
    return TrackDecoder().decode(stream)


def encode(track: Track, *, string_codec: strcodec.Codec = None) -> bytes:
    """Encode a track to its LavaPlayer representation.

    Args:
        track: Track information to be encoded.
            Note that the version of the track will be used as the format
            version.
        string_codec: String codec to use for encoding strings.

    Returns:
        Base 64 encoded track data as `bytes`.
    """
    buf = io.BytesIO()
    stream = codec.MessageOutput(buf, string_codec=string_codec)
    TrackEncoder().encode(stream, track)
    return base64.b64encode(buf.getvalue())
