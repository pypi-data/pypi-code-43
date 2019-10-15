from __future__ import annotations

import dataclasses
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .sources import AudioSource

__all__ = ["TrackInfo", "Track"]


@dataclasses.dataclass(unsafe_hash=True)
class TrackInfo:
    """
    Implements a hash method, but isn't immutable. Be careful when hashing
    instances while still mutating them!

    Attributes:
        title (str): Title of the track
        author (str): Author of the track.
        duration (float): Duration of the track in seconds.
        identifier (str): Identifier of the track.
        is_stream (bool): Whether the track is a stream.

        uri (Optional[str]): URI of the track. Definitely `None`
            before `version` 2, optional for version 2 and up.
            The uri is ignored for equality tests.
    """
    title: str
    author: str
    duration: float
    identifier: str
    is_stream: bool
    uri: Optional[str] = dataclasses.field(default=None, compare=False)


@dataclasses.dataclass(unsafe_hash=True)
class Track:
    """Information contained in a track data message body.

    Implements a hash method, but isn't immutable. Be careful when hashing
    instances while still mutating them!

    Attributes:
        version (Optional[int]): Track version. If this isn't set, the
            latest version (supported by the library) is assumed.
    """

    version: Optional[int]
    info: TrackInfo

    source: AudioSource
    position: float = dataclasses.field(default=0.)
