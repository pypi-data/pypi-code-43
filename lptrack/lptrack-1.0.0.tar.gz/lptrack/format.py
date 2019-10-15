"""TrackEncoder and TrackDecoder for LavaPlayer's message format specific to track bodies."""

import enum
from typing import Optional

from . import Track, codec, sources, versions

__all__ = ["TrackFlags", "TrackDecoder", "TrackEncoder"]


class TrackFlags(enum.IntFlag):
    """Message TrackFlags for the track data."""
    TRACK_INFO_VERSIONED = enum.auto()

    @property
    def is_versioned(self) -> bool:
        return (self & TrackFlags.TRACK_INFO_VERSIONED) > 0


class TrackDecoder:
    """TrackDecoder for track messages."""

    _version: Optional[int]
    _reader: Optional[versions.ReaderType]

    def __init__(self, *, version: int = None) -> None:
        self._version = version

        if version is None:
            self._reader = None
        else:
            self._reader = versions.get_reader(version)

    @property
    def version(self) -> Optional[int]:
        return self._version

    def decode(self, stream: codec.MessageInput) -> Track:
        """Decode an entire message and return the `Track`."""
        body_reader = stream.next()
        if not body_reader:
            raise ValueError("empty stream")

        version = self._version
        if version is None:
            flags = TrackFlags(stream.flags)

            if flags.is_versioned:
                version = body_reader.read_byte()
            else:
                version = 1

        reader = self._reader
        if reader is None:
            reader = versions.get_reader(version)

        info = reader(body_reader)
        source_name = body_reader.read_utf()
        source = sources.get_source(source_name).decode(info, body_reader)

        position = body_reader.read_long() / 1000

        return Track(version, info, source, position)


class TrackEncoder:
    _version: Optional[int]
    _writer: Optional[versions.WriterType]

    def __init__(self, *, version: int = None) -> None:
        self._version = version

        if version is None:
            self._writer = None
        else:
            self._writer = versions.get_writer(version)

    @property
    def version(self) -> Optional[int]:
        return self._version

    def encode(self, stream: codec.MessageOutput, track: Track) -> None:
        body_writer = stream.start()

        version = self._version
        if version is None:
            version = track.version
            if version is None:
                version = versions.LATEST_VERSION

        writer = self._writer
        if writer is None:
            writer = versions.get_writer(version)

        flags = TrackFlags(0)

        if version > 1:
            flags |= TrackFlags.TRACK_INFO_VERSIONED
            body_writer.write_byte(version)

        writer(body_writer, track.info)

        body_writer.write_utf(track.source.get_name())
        track.source.encode(track, body_writer)
        body_writer.write_long(round(track.position * 1000))

        stream.commit(flags)
