from dataclasses import field as stdfield
from rxdata import field as rxfield


class Dataclass:
    class Annotated:
        a1: int
        a2: int = 2

    class Mixed:
        keywords = {'a1': 11, 'a2': 22}
        a1: int = 1
        a2: int = stdfield(default=2)

    class Fielded:
        keywords = {'a1': 11, 'a2': 22, 'a3': 33, 'a4': 44, 'a5': 55, 'a6': 66, 'a7': 77, 'a8': 88}
        a1: int = stdfield(default=1)
        a2: int = stdfield(default=2)
        a3: int = stdfield(default_factory=lambda: 3)
        a4: int = stdfield(default=4, repr=False)
        a5: int = stdfield(default=5, hash=False)
        a6: int = stdfield(default=6, init=True)
        a7: int = stdfield(default=7, compare=False)
        a8: int = stdfield(default=8, metadata={'is_set': True})

class MixedFieldTypes:
    class RXDataclass:
        a1: int = 1
        a2: int = rxfield(default=2)
        a3: int = stdfield(default_factory=lambda: 3)

    class DataclassEquivalent:
        a1: int = 1
        a2: int = stdfield(default=2)
        a3: int = stdfield(default_factory=lambda: 3)

