from typing import List

class Part:
    def __init__(self, keys: List[str], val: str):
        self._ks = keys
        self._v = val

    def encode(self) -> str:
        if len(self._ks) == 0:
            raise ValueError('Key is required')

        data: str = self._ks[0]
        for k in self._ks[1:]:
            data += f'[{k}]'

        return f'{data}={self._v}'

class Encoder:
    def __init__(self, obj, keys: List[str] = []):
        self.obj = obj
        self.keys = keys

    def encode(self) -> List[Part]:
        pass

class DictEncoder(Encoder):
    def encode(self) -> List[Part]:

        pairs: List[Part] = []

        for k, v in sorted(self.obj.items()):
            keys = self.keys.copy()
            keys.append(k)

            pairs.extend(
                EncoderFactory().get_encoder(v, keys).encode()
            )

        return pairs

class ListEncoder(Encoder):
    def encode(self) -> List[Part]:

        parts: List[Part] = []
        for i, v in enumerate(self.obj):
            keys = self.keys.copy()
            keys.append(str(i))

            parts.extend(
                EncoderFactory().get_encoder(v, keys).encode()
            )

        return parts

class StrEncoder(Encoder):
    def encode(self) -> List[Part]:
        return [Part(self.keys, self.obj)]

class IntEncoder(Encoder):
    def encode(self) -> List[Part]:
        return [Part(self.keys, str(self.obj))]

class FloatEncoder(Encoder):
    def encode(self) -> List[Part]:
        return [Part(self.keys, str(self.obj))]

class NoneEncoder(Encoder):
    def encode(self) -> List[Part]:
        if len(self.keys) != 0:
            raise ValueError('None is not value')

        return []

class EncoderFactory:
    def get_encoder(self, obj, keys: List[str] = []) -> Encoder:
        if isinstance(obj, dict):
            return DictEncoder(obj, keys)
        elif isinstance(obj, list):
            return ListEncoder(obj, keys)
        elif isinstance(obj, str):
            return StrEncoder(obj, keys)
        elif isinstance(obj, int):
            return IntEncoder(obj, keys)
        elif isinstance(obj, float):
            return FloatEncoder(obj, keys)
        elif obj is None:
            return NoneEncoder(obj, keys)

        raise Exception(f"type {type(obj)} have not been supported yet")

class Preparer:
    def __init__(self, obj: object):
        self._obj = obj

    def encode(self) -> str:
        pairs: List[Part] = EncoderFactory().get_encoder(self._obj).encode()

        return '&'.join([p.encode() for p in pairs])