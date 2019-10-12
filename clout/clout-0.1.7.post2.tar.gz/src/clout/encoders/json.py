import json
import typing as t

import attr


@attr.dataclass
class JSON:
    encoder: "json.JSONEncoder" = json.JSONEncoder
    cls: t.Type = dict

    def dumps(self, data, encoder=None) -> str:
        encoder = encoder or self.encoder
        return encoder.dumps(data)

    def loads(self, text: str, encoder=None, **kwargs):
        encoder = encoder or self.encoder
        return encoder.loads(text, **kwargs)
