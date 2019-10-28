import pytest
from dataclasses import asdict, FrozenInstanceError
from rxdata import dataclass, field, operators as instance
from rx import operators as rxo

@pytest.fixture
def base(history):
    return history[-1]


@pytest.mark.observes
@pytest.mark.init
@pytest.mark.default
def test_field_observes_with_defaults_on_init(base):

    _observes = base._static + [field(default=13), 'rxfield2']

    @dataclass(frozen=base.frozen)
    class Test(base):
        rxfield1: int = _observes[-2]
        rxfield2: int = field(default=14)

        rx1: int = field(default=None, observes=rxfield1)
        rx2: int = field(default=None, observes='rxfield2')

        field: tuple = field(default=tuple([0]) * (len(_observes)),
                             observes=_observes,
                             merges=rxo.map(tuple),
                             evolves=instance.typeguard()
                             )

    test = Test()

    assert asdict(test) == {'a1': 1, 'a2': 2, 'a3': 3, 'a4': 4, 'rxfield1': 13, 'rxfield2': 14, 'rx1': 13, 'rx2':14, 'field': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)}

@pytest.mark.observes
@pytest.mark.init
@pytest.mark.default
@pytest.mark.setattr
def test_field_observes_setattr_with_defaults_on_init(base):

    _observes = base._static + [field(default=13), 'rxfield2']

    @dataclass(frozen=base.frozen)
    class Test(base):
        rxfield1: int = _observes[-2]
        rxfield2: int = field(default=14)


        rx1: int = field(default=None, observes=rxfield1)
        rx2: int = field(default=None, observes='rxfield2')

        field: tuple = field(default=tuple([0]) * (len(_observes)),
                             observes=_observes,
                             merges=rxo.map(tuple),
                             evolves=instance.typeguard()
                             )

    test = Test()

    if not base.frozen:
        # no no linked fields changes until reactive field of their observations is changed
        test.a1 = 11

        assert asdict(test) == {'a3': 3, 'a4': 4, 'a1': 11, 'a2': 2, 'rxfield1': 13, 'rxfield2': 14, 'rx1': 13, 'rx2': 14, 'field': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 13, 14)}
                               
        test.a2 = 22

        assert asdict(test) == {'a3': 3, 'a4': 4, 'a1': 11, 'a2': 22, 'rxfield1': 13, 'rxfield2': 14, 'rx1': 13, 'rx2': 14, 'field': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 13, 14)}

        test.a3 = 33

        assert asdict(test) == {'a3': 33, 'a4': 4, 'a1': 11, 'a2': 22, 'rxfield1': 13, 'rxfield2': 14, 'rx1': 13, 'rx2': 14, 'field': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 13, 14)}

        test.a4 = 44

        assert asdict(test) == {'a3': 33, 'a4': 44, 'a1': 11, 'a2': 22, 'rxfield1': 13, 'rxfield2': 14, 'rx1': 13, 'rx2': 14, 'field': (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 13, 14)}

        test.rxfield1 = 131

        assert asdict(test) == {'a3': 33, 'a4': 44, 'a1': 11, 'a2': 22, 'rxfield1': 131, 'rxfield2': 14, 'rx1': 131, 'rx2': 14, 'field': (11, 22, 33, 44, 5, 6, 7, 8, 9, 10, 11, 15, 131, 14)}

        test.rxfield2 = 141

        assert asdict(test) == {'a3': 33, 'a4': 44, 'a1': 11, 'a2': 22, 'rxfield1': 131, 'rxfield2': 141, 'rx1': 131, 'rx2': 141, 'field': (11, 22, 33, 44, 5, 6, 7, 8, 9, 10, 11, 16, 131, 141)}

    else:
        with pytest.raises(FrozenInstanceError):
            test.a1 = 11
        with pytest.raises(FrozenInstanceError):
            test.a2 = 22

        with pytest.raises(FrozenInstanceError):
            test.rxfield1 = 131

        with pytest.raises(FrozenInstanceError):
            test.rxfield1 = 141

@pytest.mark.observes
@pytest.mark.init
@pytest.mark.kwargs
def test_field_observes_with_kwargs_on_init(base):

    _observes = base._static + [field(default=13), 'rxfield2']

    @dataclass(frozen=base.frozen)
    class Test(base):
        rxfield1: int = _observes[-2]
        rxfield2: int = field(default=14)

        rx1: int = field(default=None, observes=rxfield1)
        rx2: int = field(default=None, observes='rxfield2')

        field: tuple = field(default=tuple([0]) * (len(_observes)),
                             observes=_observes,
                             merges=rxo.map(tuple),
                             evolves=instance.typeguard()
                             )


    test = Test(a1=11, a2=22, a3=33, a4=44, rxfield1=131, rxfield2=141)

    assert asdict(test) == {'a1': 11, 'a2': 22, 'a3': 33, 'a4': 44, 'rxfield1': 131, 'rxfield2': 141, 'rx1': 131, 'rx2': 141, 'field': (11, 22, 33, 44, 5, 6, 7, 8, 9, 10, 11, 12, 131, 141)}


@pytest.mark.observes
@pytest.mark.init
@pytest.mark.kwargs
@pytest.mark.setattr
def test_field_observes_setattr_with_kwargs_on_init(base):

    _observes = base._static + [field(default=13), 'rxfield2']

    @dataclass(frozen=base.frozen)
    class Test(base):
        rxfield1: int = _observes[-2]
        rxfield2: int = field(default=14)

        rx1: int = field(default=None, observes=rxfield1)
        rx2: int = field(default=None, observes='rxfield2')

        field: tuple = field(default=tuple([0]) * (len(_observes)),
                             observes=_observes,
                             merges=rxo.map(tuple),
                             evolves=instance.typeguard()
                             )


    test = Test(a1=11, a2=22, a3=33, a4=44, rxfield1=131, rxfield2=141)

    if not base.frozen:
        # no no linked fields changes until reactive field of their observations is changed
        test.a1 = 111

        assert asdict(test) == {'a1': 111, 'a2': 22, 'a3': 33, 'a4': 44, 'rxfield1': 131, 'rxfield2': 141, 'rx1': 131, 'rx2':141, 'field': (11, 22, 33, 44, 5, 6, 7, 8, 9, 10, 11, 14, 131, 141)}

        test.a2 = 222
        assert asdict(test) == {'a1': 111, 'a2': 222, 'a3': 33, 'a4': 44, 'rxfield1': 131, 'rxfield2': 141, 'rx1': 131, 'rx2':141, 'field': (11, 22, 33, 44, 5, 6, 7, 8, 9, 10, 11, 14, 131, 141)}

        test.a3 = 333
        assert asdict(test) == {'a1': 111, 'a2': 222, 'a3': 333, 'a4': 44, 'rxfield1': 131, 'rxfield2': 141, 'rx1': 131, 'rx2':141, 'field': (11, 22, 33, 44, 5, 6, 7, 8, 9, 10, 11, 14, 131, 141)}

        test.a4 = 444
        assert asdict(test) == {'a1': 111, 'a2': 222, 'a3': 333, 'a4': 444, 'rxfield1': 131, 'rxfield2': 141, 'rx1': 131, 'rx2':141, 'field': (11, 22, 33, 44, 5, 6, 7, 8, 9, 10, 11, 14, 131, 141)}

        test.rxfield1 = 1311

        assert asdict(test) == {'a1': 111, 'a2': 222, 'a3': 333, 'a4': 444, 'rxfield1': 1311, 'rxfield2': 141, 'rx1': 1311, 'rx2': 141, 'field': (111, 222, 333, 444, 5, 6, 7, 8, 9, 10, 11, 15, 1311, 141)}

        test.rxfield2 = 1411
        assert asdict(test) == {'a3': 333, 'a4': 444, 'a1': 111, 'a2': 222, 'rxfield1': 1311, 'rxfield2': 1411, 'rx1': 1311, 'rx2': 1411, 'field': (111, 222, 333, 444, 5, 6, 7, 8, 9, 10, 11, 16, 1311, 1411)}


    else:
        with pytest.raises(FrozenInstanceError):
            test.a1 = 11
        with pytest.raises(FrozenInstanceError):
            test.a2 = 22

        with pytest.raises(FrozenInstanceError):
            test.rxfield1 = 131

        with pytest.raises(FrozenInstanceError):
            test.rxfield1 = 141