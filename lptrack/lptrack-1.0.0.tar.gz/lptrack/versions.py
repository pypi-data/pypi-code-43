"""Versioned body readers and writers for track message bodies.

Attributes:
    LATEST_VERSION (int): Latest version supported by the library.
"""

from typing import Callable, Tuple

from . import TrackInfo, codec

LATEST_VERSION = 2


def _read_body_v1_2(stream: codec.Reader, version: int) -> TrackInfo:
    return TrackInfo(
        title=stream.read_utf(),
        author=stream.read_utf(),
        duration=stream.read_long() / 1000,
        identifier=stream.read_utf(),
        is_stream=stream.read_bool(),
        uri=stream.read_optional_utf() if version >= 2 else None,
    )


def read_body_v1(stream: codec.Reader) -> TrackInfo:
    return _read_body_v1_2(stream, 1)


def read_body_v2(stream: codec.Reader) -> TrackInfo:
    return _read_body_v1_2(stream, 2)


def _write_body_v1_2(stream: codec.Writer, track: TrackInfo, version: int) -> None:
    stream.write_utf(track.title)
    stream.write_utf(track.author)
    stream.write_long(int(track.duration * 1000))
    stream.write_utf(track.identifier)
    stream.write_bool(track.is_stream)

    if version >= 2:
        stream.write_optional_utf(track.uri)


def write_body_v1(stream: codec.Writer, track: TrackInfo) -> None:
    _write_body_v1_2(stream, track, 1)


def write_body_v2(stream: codec.Writer, track: TrackInfo) -> None:
    _write_body_v1_2(stream, track, 2)


ReaderType = Callable[[codec.Reader], TrackInfo]
WriterType = Callable[[codec.Writer, TrackInfo], None]

_FORMAT_VERSIONS = {
    1: (read_body_v1, write_body_v1),
    2: (read_body_v2, write_body_v2),
}


def _get_format(version: int) -> Tuple:
    try:
        return _FORMAT_VERSIONS[version]
    except KeyError:
        raise ValueError(f"Unsupported version: {version}") from None


def get_reader(version: int) -> ReaderType:
    """Get a body reader for the given version.

    Raises:
        ValueError: If the version isn't supported.
    """
    return _get_format(version)[0]


def get_writer(version: int) -> WriterType:
    """Get a body writer for the given version.

    Raises:
        ValueError: If the version isn't supported.
    """
    return _get_format(version)[1]
