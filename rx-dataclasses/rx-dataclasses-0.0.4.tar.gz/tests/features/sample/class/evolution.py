from dataclasses import field as stdfield
from rxdata import field as rxfield, dataclass


class _unfrozen:
    frozen = False

class _frozen:
    frozen = True

class unfrozen:
    @dataclass(frozen=False)
    class plain(_unfrozen):
        a1: int = 1
        a2: int = rxfield(default=2)
        a3: int = stdfield(default=3)

    @dataclass(frozen=False)
    class base0:
        a1: int = 1

    @dataclass(frozen=False)
    class inherited(base0, _unfrozen):
        a2: int = rxfield(default=2)
        a3: int = stdfield(default=3)

    @dataclass(frozen=False)
    class base1:
        a2: int = rxfield(default=2)

    @dataclass(frozen=False)
    class composed(base0, base1, _unfrozen):
        a3: int = stdfield(default=3)

class frozen:
    value = False
    @dataclass(frozen=True)
    class plain(_frozen):
        a1: int = 1
        a2: int = rxfield(default=2)
        a3: int = stdfield(default=3)

    @dataclass(frozen=True)
    class base0:
        a1: int = 1

    @dataclass(frozen=True)
    class inherited(base0, _frozen):
        a2: int = rxfield(default=2)
        a3: int = stdfield(default=3)

    @dataclass(frozen=True)
    class base1:
        a2: int = rxfield(default=2)

    @dataclass(frozen=True)
    class composed(base0, base1, _frozen):
        a3: int = stdfield(default=3)