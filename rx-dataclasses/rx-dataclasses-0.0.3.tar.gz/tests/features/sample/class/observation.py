from dataclasses import field as stdfield
from rxdata import field as rxfield, dataclass
from functools import partial
import builtins

builtins.__dict__['a9'] = lambda: 9
builtins.__dict__['a10'] = lambda: 10
builtins.__dict__['a11'] = lambda: 11


class _unfrozen:
    frozen = False

class _frozen:
    frozen = True

class unfrozen:
    @dataclass(frozen=False)
    class plain(_unfrozen):
        a1: int = 1
        a1_ = 'a1'

        a2: int = 2
        a2_ = 'a2'

        a3: int = stdfield(default=3)


        a4: int = stdfield(default=4)
        a4_ = 'a4'

        c5 = 3
        def a5(self=None):
            return 5

        c6 = 4
        def a6(self=None):
            return 6

        a6_ = 'a6'

        a7 = partial(int, 7)
        
        a8 = partial(int, 8)
        a8_ = 'a8'

        a9 = builtins.a9

        a10_ = 'builtins.a10'

        a11_ = 'builtins:a11'

        a12 = (i for i in range(100))

        for i in range(11):
            next(a12)

        a12_ = partial(next, a12)

        _static = []

        for i in range(1, 13):
            _static.append(locals()[f'a{i}_'] if f'a{i}_' in locals() else locals()[f'a{i}'])


    @dataclass(frozen=False)
    class base(_unfrozen):
        a1: int = 1


        a2: int = 2


        a3: int = stdfield(default=3)


        a4: int = stdfield(default=4)


    @dataclass(frozen=False)
    class inherited(base):

        a1_ = 'a1'
        a2_ = 'a2'
        a3_ = 'a3'
        a4_ = 'a4'

        c5 = 3
        def a5(self=None):
            return 5

        c6 = 4
        def a6(self=None):
            return 6

        a6_ = 'a6'

        a7 = partial(int, 7)
        
        a8 = partial(int, 8)
        a8_ = 'a8'

        a9 = builtins.a9

        a10_ = 'builtins.a10'

        a11_ = 'builtins:a11'

        a12 = (i for i in range(100))

        for i in range(11):
            next(a12)

        a12_ = partial(next, a12)

        _static = []

        for i in range(1, 13):
            _static.append(locals()[f'a{i}_'] if f'a{i}_' in locals() else locals()[f'a{i}'])


    @dataclass(frozen=False)
    class base0():
        a1: int = 1
        a2: int = 2

    @dataclass(frozen=False)
    class base1():
        a3: int = stdfield(default=3)
        a4: int = stdfield(default=4)

    @dataclass(frozen=False)
    class composed(base0, base1, _unfrozen):
        a1_ = 'a1'
        a2_ = 'a2'
        a3_ = 'a3'
        a4_ = 'a4'

        c5 = 3
        def a5(self=None):
            return 5

        c6 = 4
        def a6(self=None):
            return 6

        a6_ = 'a6'

        a7 = partial(int, 7)
        
        a8 = partial(int, 8)
        a8_ = 'a8'

        a9 = builtins.a9

        a10_ = 'builtins.a10'

        a11_ = 'builtins:a11'

        a12 = (i for i in range(100))

        for i in range(11):
            next(a12)

        a12_ = partial(next, a12)

        _static = []

        for i in range(1, 13):
            _static.append(locals()[f'a{i}_'] if f'a{i}_' in locals() else locals()[f'a{i}'])



class frozen:
    @dataclass(frozen=True)
    class plain(_frozen):
        a1: int = 1
        a1_ = 'a1'

        a2: int = 2
        a2_ = 'a2'

        a3: int = stdfield(default=3)


        a4: int = stdfield(default=4)
        a4_ = 'a4'

        c5 = 3
        def a5(self=None):
            return 5

        c6 = 4
        def a6(self=None):
            return 6

        a6_ = 'a6'

        a7 = partial(int, 7)
        
        a8 = partial(int, 8)
        a8_ = 'a8'

        a9 = builtins.a9

        a10_ = 'builtins.a10'

        a11_ = 'builtins:a11'

        a12 = (i for i in range(100))

        for i in range(11):
            next(a12)

        a12_ = partial(next, a12)

        _static = []

        for i in range(1, 13):
            _static.append(locals()[f'a{i}_'] if f'a{i}_' in locals() else locals()[f'a{i}'])

    @dataclass(frozen=True)
    class base(_frozen):
        a1: int = 1


        a2: int = 2


        a3: int = stdfield(default=3)


        a4: int = stdfield(default=4)


    @dataclass(frozen=True)
    class inherited(base):


        a1_ = 'a1'
        a2_ = 'a2'
        a3_ = 'a3'
        a4_ = 'a4'

        c5 = 3
        def a5(self=None):
            return 5

        c6 = 4
        def a6(self=None):
            return 6

        a6_ = 'a6'

        a7 = partial(int, 7)
        
        a8 = partial(int, 8)
        a8_ = 'a8'

        a9 = builtins.a9

        a10_ = 'builtins.a10'

        a11_ = 'builtins:a11'

        a12 = (i for i in range(100))

        for i in range(11):
            next(a12)

        a12_ = partial(next, a12)

        _static = []

        for i in range(1, 13):
            _static.append(locals()[f'a{i}_'] if f'a{i}_' in locals() else locals()[f'a{i}'])


    @dataclass(frozen=True)
    class base0():
        a1: int = 1
        a2: int = 2

    @dataclass(frozen=True)
    class base1():
        a3: int = stdfield(default=3)
        a4: int = stdfield(default=4)

    @dataclass(frozen=True)
    class composed(base0, base1, _frozen):
        a1_ = 'a1'
        a2_ = 'a2'
        a3_ = 'a3'
        a4_ = 'a4'

        c5 = 3
        def a5(self=None):
            return 5

        c6 = 4
        def a6(self=None):
            return 6

        a6_ = 'a6'

        a7 = partial(int, 7)
        
        a8 = partial(int, 8)
        a8_ = 'a8'

        a9 = builtins.a9

        a10_ = 'builtins.a10'

        a11_ = 'builtins:a11'

        a12 = (i for i in range(100))

        for i in range(11):
            next(a12)

        a12_ = partial(next, a12)

        _static = []

        for i in range(1, 13):
            _static.append(locals()[f'a{i}_'] if f'a{i}_' in locals() else locals()[f'a{i}'])