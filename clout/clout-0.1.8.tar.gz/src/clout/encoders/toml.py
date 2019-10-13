import typing as t

import attr
import toml


@attr.dataclass
class TOML:
    encoder: "toml.TomlEncoder" = toml.encoder
    decoder: "toml.TomlDecoder" = toml.decoder
    cls: t.Type = dict

    def dumps(self, data, encoder=None) -> str:
        encoder = encoder or self.encoder
        return encoder.dumps(data, encoder=encoder)

    def loads(self, text: str, decoder=None, cls=None):
        decoder = decoder or self.decoder
        return decoder.loads(text, _dict=cls or self.cls)
