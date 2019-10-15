import abc
from typing import Dict, Type

from . import codec
from .track import Track, TrackInfo

__all__ = ["AudioSource",
           "audio_source",
           "get_source",
           "BandCamp",
           "Beam",
           "Nico",
           "SoundCloud",
           "Twitch",
           "Vimeo",
           "Youtube"]


class AudioSource(abc.ABC):
    """Audio source."""

    def __str__(self) -> str:
        return self.get_name()

    @classmethod
    @abc.abstractmethod
    def get_name(cls) -> str:
        """Get the name of the audio source."""
        ...

    @abc.abstractmethod
    def encode(self, track: Track, writer: codec.Writer) -> None:
        """Encode the extra details of the source."""
        ...

    @classmethod
    @abc.abstractmethod
    def decode(cls, info: TrackInfo, reader: codec.Reader):
        """Decode the extra details of the source."""
        ...


def create_unknown_source(name: str) -> Type[AudioSource]:
    class UnknownSource(AudioSource):
        def __repr__(self) -> str:
            return f"Unknown({name!r})"

        @classmethod
        def get_name(cls) -> str:
            return name

        def encode(self, track: Track, writer: codec.Writer) -> None:
            pass

        @classmethod
        def decode(cls, info: TrackInfo, reader: codec.Reader):
            return cls()

    return UnknownSource


_SOURCES: Dict[str, Type[AudioSource]] = {}


def audio_source(cls=None):
    """Decorator to mark a source."""

    def decorator(cls: Type[AudioSource]):
        _SOURCES[cls.get_name()] = cls
        return cls

    if cls is None:
        return decorator
    else:
        return decorator(cls)


def get_source(name: str) -> Type[AudioSource]:
    """Get the audio source for the name.

    Returns:
        A subclass of `AudioSource` and an unknown source when
        no registered source type (audio sources decorated with `audio_source`)
        was found.
    """
    try:
        return _SOURCES[name]
    except KeyError:
        return create_unknown_source(name)


class _BuiltinAudioSource(AudioSource):
    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    @classmethod
    def get_name(cls) -> str:
        try:
            name = cls.__source_name__
        except AttributeError:
            name = cls.__source_name__ = cls.__name__.lower()

        return name

    def __eq__(self, other) -> bool:
        if isinstance(other, _BuiltinAudioSource):
            return self.get_name() == other.get_name()
        else:
            return NotImplemented

    def encode(self, track: Track, writer: codec.Writer) -> None:
        pass

    @classmethod
    def decode(cls, info: TrackInfo, reader: codec.Reader) -> "AudioSource":
        return cls()


@audio_source
class BandCamp(_BuiltinAudioSource):
    ...


@audio_source
class Beam(_BuiltinAudioSource):
    __source_name__ = "beam.pro"


@audio_source
class Nico(_BuiltinAudioSource):
    __source_name__ = "niconico"


@audio_source
class SoundCloud(_BuiltinAudioSource):
    ...


@audio_source
class Twitch(_BuiltinAudioSource):
    ...


@audio_source
class Vimeo(_BuiltinAudioSource):
    ...


@audio_source
class Youtube(_BuiltinAudioSource):
    ...
