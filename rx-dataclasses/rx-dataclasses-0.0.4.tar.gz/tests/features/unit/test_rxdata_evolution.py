import pytest
from dataclasses import asdict, FrozenInstanceError
from rxdata import dataclass, field, operators as rxdataop
from rx import operators as rxo
from collections import defaultdict

@pytest.fixture
def base(history):
    return history[-1]


@pytest.fixture
def record_evolutions():
    def create_evolution_state():
        state = defaultdict(list)
        def recorder(name):
            return rxo.map(lambda v: state[name].append(v) or v)

        return state, recorder

    return create_evolution_state


@pytest.mark.evolves
@pytest.mark.init
@pytest.mark.default
def test_invocation_with_defaults_on_init(base, record_evolutions):
    recorded, recorder = record_evolutions()

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=recorder('field'), default=4)
    tested = Test()

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}
    assert recorded['field'] == [4]


@pytest.mark.subclassed
@pytest.mark.evolves
@pytest.mark.init
@pytest.mark.default
def test_invocation_with_defaults_on_init_of_subclassed(base, record_evolutions):
    recorded, recorder = record_evolutions()

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=recorder('field'), default=4)

    class Subclassed(Test):
        pass

    tested = Subclassed()

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}
    assert recorded['field'] == [4]


@pytest.mark.evolves
@pytest.mark.override
@pytest.mark.init
@pytest.mark.default
def test_invocation_with_defaults_and_override_on_init(base, record_evolutions):
    recorded, recorder = record_evolutions()

    @dataclass(frozen=base.frozen)
    class Test(base):
        a2: int = field(evolves=recorder('a2'), default=2)
        field: int = field(evolves=recorder('field'), default=4)
    tested = Test()

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}
    assert recorded['a2'] == [2]
    assert recorded['field'] == [4]


@pytest.mark.subclassed
@pytest.mark.evolves
@pytest.mark.override
@pytest.mark.init
@pytest.mark.default
def test_invocation_with_defaults_and_override_on_init_of_subclassed(base, record_evolutions):
    recorded, recorder = record_evolutions()

    @dataclass(frozen=base.frozen)
    class Test(base):
        a2: int = field(evolves=recorder('a2'), default=2)
        field: int = field(evolves=recorder('field'), default=4)

    class Subclassed(Test):
        pass

    tested = Subclassed()

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}
    assert recorded['a2'] == [2]
    assert recorded['field'] == [4]


@pytest.mark.evolves
@pytest.mark.init
@pytest.mark.kwargs
def test_invocation_with_initargs_on_init(base, record_evolutions):
    recorded, recorder = record_evolutions()

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=recorder('field'), default=4)
    tested = Test(a1=11, a2=22, a3=33, field=44)

    assert asdict(tested) == {'a1': 11, 'a2': 22, 'a3': 33, 'field': 44}
    assert recorded['field'] == [44]


@pytest.mark.subclassed
@pytest.mark.evolves
@pytest.mark.init
@pytest.mark.kwargs
def test_invocation_with_initargs_on_init_of_subclassed(base, record_evolutions):
    recorded, recorder = record_evolutions()

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=recorder('field'), default=4)

    class Subclassed(Test):
        pass

    tested = Subclassed(a1=11, a2=22, a3=33, field=44)

    assert asdict(tested) == {'a1': 11, 'a2': 22, 'a3': 33, 'field': 44}
    assert recorded['field'] == [44]



@pytest.mark.evolves
@pytest.mark.override
@pytest.mark.init
@pytest.mark.kwargs
def test_invocation_with_initargs_on_init(base, record_evolutions):
    recorded, recorder = record_evolutions()

    @dataclass(frozen=base.frozen)
    class Test(base):
        a2: int = field(evolves=recorder('a2'), default=2)
        field: int = field(evolves=recorder('field'), default=4)

    tested = Test(a1=11, a2=22, a3=33, field=44)

    assert asdict(tested) == {'a1': 11, 'a2': 22, 'a3': 33, 'field': 44}
    assert recorded['a2'] == [22]
    assert recorded['field'] == [44]


@pytest.mark.subclassed
@pytest.mark.evolves
@pytest.mark.override
@pytest.mark.init
@pytest.mark.kwargs
def test_invocation_with_initargs_on_init_of_subclassed(base, record_evolutions):
    recorded, recorder = record_evolutions()

    @dataclass(frozen=base.frozen)
    class Test(base):
        a2: int = field(evolves=recorder('a2'), default=2)
        field: int = field(evolves=recorder('field'), default=4)

    class Subclassed(Test):
        pass

    tested = Subclassed(a1=11, a2=22, a3=33, field=44)

    assert asdict(tested) == {'a1': 11, 'a2': 22, 'a3': 33, 'field': 44}
    assert recorded['a2'] == [22]
    assert recorded['field'] == [44]



@pytest.mark.evolves
@pytest.mark.setattr
def test_invocation_with_setattr(base, record_evolutions):
    recorded, recorder = record_evolutions()

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=recorder('field'), default=4)
    tested = Test(a1=11, a2=22, a3=33, field=44)

    if base.frozen:
        with pytest.raises(FrozenInstanceError):
            tested.field = 444
        assert recorded['field'] == [44]
        return

    tested.field = 444
    assert asdict(tested) == {'a1': 11, 'a2': 22, 'a3': 33, 'field': 444}
    assert recorded['field'] == [44, 444]


@pytest.mark.subclassed
@pytest.mark.evolves
@pytest.mark.setattr
def test_invocation_with_setattr_of_subclassed(base, record_evolutions):
    recorded, recorder = record_evolutions()

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=recorder('field'), default=4)

    class Subclassed(Test):
        pass

    tested = Subclassed(a1=11, a2=22, a3=33, field=44)

    if base.frozen:
        with pytest.raises(FrozenInstanceError):
            tested.field = 444
        assert recorded['field'] == [44]
        return

    tested.field = 444
    assert asdict(tested) == {'a1': 11, 'a2': 22, 'a3': 33, 'field': 444}
    assert recorded['field'] == [44, 444]



@pytest.mark.evolves
@pytest.mark.override
@pytest.mark.setattr
def test_overriden_invocation_with_setattr(base, record_evolutions):
    recorded, recorder = record_evolutions()

    @dataclass(frozen=base.frozen)
    class Test(base):
        a2: int = field(evolves=recorder('a2'), default=2)
        field: int = field(evolves=recorder('field'), default=4)

    tested = Test(a1=11, a2=22, a3=33, field=44)

    if base.frozen:
        with pytest.raises(FrozenInstanceError):
            tested.field = 444
        assert recorded['field'] == [44]

        with pytest.raises(FrozenInstanceError):
            tested.a2 = 222
        assert recorded['a2'] == [22]
        return


    tested.field = 444
    assert asdict(tested) == {'a1': 11, 'a2': 22, 'a3': 33, 'field': 444}
    assert recorded['field'] == [44, 444]

    tested.a2 = 222
    assert asdict(tested) == {'a1': 11, 'a2': 222, 'a3': 33, 'field': 444}
    assert recorded['a2'] == [22, 222]
    assert recorded['field'] == [44, 444]


@pytest.mark.subclassed
@pytest.mark.evolves
@pytest.mark.override
@pytest.mark.setattr
def test_overriden_invocation_with_setattr_of_subclassed(base, record_evolutions):
    recorded, recorder = record_evolutions()

    @dataclass(frozen=base.frozen)
    class Test(base):
        a2: int = field(evolves=recorder('a2'), default=2)
        field: int = field(evolves=recorder('field'), default=4)

    class Subclassed(Test):
        pass

    tested = Subclassed(a1=11, a2=22, a3=33, field=44)

    if base.frozen:
        with pytest.raises(FrozenInstanceError):
            tested.field = 444
        assert recorded['field'] == [44]

        with pytest.raises(FrozenInstanceError):
            tested.a2 = 222
        assert recorded['a2'] == [22]
        return



    tested.field = 444
    assert asdict(tested) == {'a1': 11, 'a2': 22, 'a3': 33, 'field': 444}
    assert recorded['field'] == [44, 444]

    tested.a2 = 222
    assert asdict(tested) == {'a1': 11, 'a2': 222, 'a3': 33, 'field': 444}
    assert recorded['a2'] == [22, 222]
    assert recorded['field'] == [44, 444]



@pytest.mark.typeguard
@pytest.mark.init
@pytest.mark.default
def test_invocation_typeguard_with_defaults_on_init(base):

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=rxdataop.typeguard(), default=4)
    tested = Test()

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}


    @dataclass(frozen=base.frozen)
    class Test(base):
        field: str = field(evolves=rxdataop.typeguard(int), default=4)
    tested = Test()

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: 'builtins.int' = field(evolves=rxdataop.typeguard(), default=4)
    tested = Test()

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: str = field(evolves=rxdataop.typeguard('builtins:int'), default=4)
    tested = Test()

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: str = field(evolves=rxdataop.typeguard('builtins.int'), default=4)
    tested = Test()

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}



    @dataclass(frozen=base.frozen)
    class Test(base):
        field: str = field(evolves=rxdataop.typeguard(), default=4)
    
    with pytest.raises(TypeError):
        tested = Test()

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=rxdataop.typeguard(str), default=4)
    
    with pytest.raises(TypeError):
        tested = Test()


    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=rxdataop.typeguard('builtins:str'), default=4)
    
    with pytest.raises(TypeError):
        tested = Test()

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=rxdataop.typeguard('builtins.str'), default=4)
    
    with pytest.raises(TypeError):
        tested = Test()


@pytest.mark.typeguard
@pytest.mark.init
@pytest.mark.kwargs
def test_invocation_typeguard_with_args_on_init(base):

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=rxdataop.typeguard(), default=False)
    tested = Test(field=4)

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}


    @dataclass(frozen=base.frozen)
    class Test(base):
        field: str = field(evolves=rxdataop.typeguard(int), default=False)
    tested = Test(field=4)

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: 'builtins.int' = field(evolves=rxdataop.typeguard(), default=False)
    tested = Test(field=4)

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: str = field(evolves=rxdataop.typeguard('builtins.int'), default=False)
    tested = Test(field=4)

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: str = field(evolves=rxdataop.typeguard('builtins:int'), default=4)
    tested = Test(field=4)

    assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 4}


    @dataclass(frozen=base.frozen)
    class Test(base):
        field: str = field(evolves=rxdataop.typeguard(), default='4')
    
    with pytest.raises(TypeError):
        tested = Test(field=5)

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=rxdataop.typeguard(str), default='4')
    
    with pytest.raises(TypeError):
        tested = Test(field=4)


    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=rxdataop.typeguard('builtins:str'), default='4')
    
    with pytest.raises(TypeError):
        tested = Test(field=4)

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=rxdataop.typeguard('builtins.str'), default='4')
    
    with pytest.raises(TypeError):
        tested = Test(field=4)


@pytest.mark.typeguard
@pytest.mark.setattr
def test_invocation_typeguard_with_setattr(base):

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=rxdataop.typeguard(), default=4)
    tested = Test()

    if not base.frozen:
        tested.field = 5
        assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 5}
    else:
        with pytest.raises(FrozenInstanceError):
            tested.field = 5


    @dataclass(frozen=base.frozen)
    class Test(base):
        field: str = field(evolves=rxdataop.typeguard(int), default=4)
    tested = Test()
    
    if not base.frozen:
        tested.field = 5    
        assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 5}
    else:
        with pytest.raises(FrozenInstanceError):
            tested.field = 5


    @dataclass(frozen=base.frozen)
    class Test(base):
        field: 'builtins.int' = field(evolves=rxdataop.typeguard(), default=4)
    tested = Test()

    if not base.frozen:
        tested.field = 5
        assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 5}
    else:
        with pytest.raises(FrozenInstanceError):
            tested.field = 5

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: str = field(evolves=rxdataop.typeguard('builtins:int'), default=4)
    tested = Test()

    if not base.frozen:
        tested.field = 5
        assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 5}
    else:
        with pytest.raises(FrozenInstanceError):
            tested.field = 5

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: str = field(evolves=rxdataop.typeguard('builtins.int'), default=4)
    tested = Test()

    if not base.frozen:
        tested.field = 5
        assert asdict(tested) == {'a1': 1, 'a2': 2, 'a3': 3, 'field': 5}
    else:
        with pytest.raises(FrozenInstanceError):
            tested.field = 5



    @dataclass(frozen=base.frozen)
    class Test(base):
        field: str = field(evolves=rxdataop.typeguard(), default='4')

    tested = Test()
    if not base.frozen:
        with pytest.raises(TypeError):
            tested.field = 5
    else:
        with pytest.raises(FrozenInstanceError):
            tested.field = 5


    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=rxdataop.typeguard(str), default='4')

    tested = Test()
    if not base.frozen:
        with pytest.raises(TypeError):
            tested.field = 5
    else:
        with pytest.raises(FrozenInstanceError):
            tested.field = 5


    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=rxdataop.typeguard('builtins:str'), default='4')

    tested = Test()
    if not base.frozen:
        with pytest.raises(TypeError):
            tested.field = 5
    else:
        with pytest.raises(FrozenInstanceError):
            tested.field = 5

    @dataclass(frozen=base.frozen)
    class Test(base):
        field: int = field(evolves=rxdataop.typeguard('builtins.str'), default='4')
    
    tested = Test()

    if not base.frozen:
        with pytest.raises(TypeError):
            tested.field = 5
    else:
        with pytest.raises(FrozenInstanceError):
            tested.field = 5
