"""Provides support for various codecs."""
import dataclasses
import importlib

__all__ = ["Codec",
           "DEFAULT", "UTF8", "MUTF8"]


@dataclasses.dataclass(frozen=True)
class Codec:
    encoding: str
    error_handler: str

    def encode(self, data: str) -> bytes:
        return data.encode(self.encoding, self.error_handler)

    def decode(self, data: bytes) -> str:
        return data.decode(self.encoding, self.error_handler)


DEFAULT: Codec
UTF8 = Codec("utf-8", "surrogatepass")
UTF8STRICT = Codec("utf-8", "strict")
MUTF8 = Codec("utf-8-var", "strict")

try:
    importlib.import_module("ftfy.bad_codecs")
    import ftfy.bad_codecs.utf8_variants
except ImportError:
    DEFAULT = UTF8
else:
    DEFAULT = MUTF8
