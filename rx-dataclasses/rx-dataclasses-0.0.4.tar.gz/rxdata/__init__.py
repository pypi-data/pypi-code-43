'''reactive dataclasses'''
import types
import typing
from copy import copy
from operator import attrgetter, itemgetter
from collections import namedtuple, defaultdict
from itertools import chain
from inspect import getfullargspec as getargspec
from functools import wraps, partial
import weakref
import warnings
import keyword


import dataclasses

from dataclasses import MISSING


import rx
from rx import subject as rxsubject
from rx import operators as rxo

RXFieldSubjectValue = namedtuple('RXFieldSubjectValue', ('pivot', 'terminal', 'combines'))
class RXFieldSubjectMap(typing.Mapping):
    def __init__(self):
        self.subject = dict()

    def __getitem__(self, object):
        return self.subject[id(object)]

    def __setitem__(self, object, subject):
        self.subject[id(object)] = subject if isinstance(subject, RXFieldSubjectValue) else RXFieldSubjectValue(*(tuple(subject) + (([], ) if len(subject) == 2 else ())))
        weakref.finalize(object, lambda: id(object) in self.subject and self.subject.__delitem__(id(object)))

    def __delitem__(self, object):
        self.subject.__delitem__(id(object))

    def __contains__(self, object):
        return id(object) in self.subject

    def __iter__(self):
        return self.subject.__iter__()

    def __len__(self):
        return self.subject.__len__(self)


@dataclasses.dataclass
class RX:
    SETATTR_MARK = '__rx_dataclass__'
    def _options_class(defaults: typing.Mapping):
        @dataclasses.dataclass
        class Options:
            #if to subscribe on `observes` upon init - update this initial value to observed value(s)
            init_observes: bool = defaults['init_observes']
            #if to enable `evolves` pipeline upon init - check initial value with `evolves` pipeline
            init_evolves: bool = defaults['init_evolves']
            #if to check each setattr value with `evolves` pipeline
            setattr_evolves: bool = defaults['setattr_evolves']
            #if to delattr when `observed` is deleted (subject completed)
            delattr_observes: bool = defaults['delattr_observes']
        return Options

    FieldOptions = _options_class({'init_observes': None,
                                   'init_evolves': None,
                                   'setattr_evolves': None,
                                   'delattr_observes': None})
    FieldOptions.__qualname__ = f'{__module__}.RX.FieldOptions'
    DataclassOptions = _options_class({'init_observes': True,
                                       'init_evolves': True,
                                       'setattr_evolves': True,
                                       'delattr_observes': False})
    DataclassOptions.__qualname__ = f'{__module__}.RX.DataclassOptions'


    def update_ambigous_options(self, options: DataclassOptions):
        for name, value in dataclasses.asdict(options).items():
            if getattr(self.options, name) is None:
                setattr(self.options, name, value)


    def combine(self,
                combine: typing.List,
                merging: typing.List,
                instance: typing.Any,
                *,
                pathsplitter: typing.Sequence = ':.'
                ):
        assert merging
        from . import attribute


        sources = []
        _fields = getattr(type(instance), dataclasses._FIELDS)
        def callfrompartials(values):
            return tuple(value()() if isinstance(value, partial) else value for value in values)

        for source in combine:
            r = source

            if isinstance(source, str):
                if not any(s in source for s in pathsplitter):
                    if source in _fields:
                        source = _fields[source]
                    else:
                        source = rx.just(partial(getattr, instance, source))
                else:
                    source = rx.just(partial(attribute.path.fromstring(source).get))


            if isinstance(source, RXField):
                assert instance in source.rx.subject, (f'Field {source!r} has no subject for {instance!r}')
                source = source.rx.subject[instance].terminal

            elif isinstance(source, dataclasses.Field):
                source = rx.just(partial(partial, getattr, instance, source.name))

            elif callable(source):
                source = rx.just(partial(partial, source))

            elif isinstance(source, (rx.Observable, rxsubject.Subject)):
                pass

            else:
                raise TypeError('Observation reference must be one of [dataclasses.Field, RXField,'
                                f'str("attrname"), str("module:attribute"), rx.Observable]. Got {source!r} instead')

            sources.append(source)

        return rx.combine_latest(*sources).pipe(rxo.map(callfrompartials)).pipe(*merging)

    @property
    def safe_merge_if_possible(self):
        if len(self.observes) == 1 and len(self.merges) == 0:
            return [rxo.map(itemgetter(0))]
        else:
            return self.merges


    options: 'typing.Any' = dataclasses.field(default_factory=FieldOptions)
    scheduler: 'typing.Scheduler' = None
    subject: RXFieldSubjectMap = dataclasses.field(default_factory=RXFieldSubjectMap)
    observes: 'typing.List[rx.Observable]' = dataclasses.field(default_factory=list)
    merges: 'typing.List[typing.Callable]' = dataclasses.field(default_factory=list)
    evolves: 'typing.List[typing.Callable]' = dataclasses.field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.options, typing.Mapping):
            self.options = self.__class__.FieldOptions(**self.options)




class RXField(dataclasses.Field):
    __slots__ = dataclasses.Field.__slots__ + ('rx',)

    def __init__(self, *args, rx: typing.Union[RX, typing.Mapping], **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(rx, typing.Mapping):
            rx = RX(**rx)
        self.rx = rx

    @property
    def value(self):
        return attrgetter(self.name)

    @classmethod
    def instance(cls, object, name):
        if not isinstance(object, type):
            object = type(object)
        return getattr(object, dataclasses._FIELDS)[name]


def fields(object, *, oftype=RXField):
    return tuple(field for field in dataclasses.fields(object) if isinstance(field, oftype))


def field(*args,
          rx: typing.Mapping = MISSING,
          observes: typing.Sequence = MISSING,
          merges: typing.Sequence = MISSING,
          evolves: typing.Sequence = MISSING,
          default=MISSING,
          default_factory=MISSING,
          **kwargs):
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory')
    kwonlydefaults = getargspec(dataclasses.field).kwonlydefaults
    if kwonlydefaults is not None:
        for (k, v) in kwonlydefaults.items():
            kwargs.setdefault(k, v)
    kwargs.update({'default': default, 'default_factory': default_factory})

    if rx is MISSING:
        rx = {}

    assert isinstance(rx, typing.Mapping)

    rx = copy(rx)

    def sequential(value):
        if isinstance(value, str):
            return [value]
        elif not isinstance(value, typing.Sequence):
            return [value]
        else:
            return list(value)

    for name in ('observes', 'merges', 'evolves'):
        if locals()[name] is not MISSING:
            rx[name] = locals()[name]

        if name in rx:
            rx[name] = sequential(rx[name])

    return RXField(*args, rx=rx, **kwargs)

def _rx_init_fn(fields, frozen, has_post_init, self_name):
    # _field_init for RXField always called with frozen=False so `self.attr=attr` always used
    seen_default = False
    for f in fields:
        # Only consider fields in the __init__ call.
        if f.init:
            if not (f.default is MISSING and f.default_factory is MISSING):
                seen_default = True
            elif seen_default:
                raise TypeError(f'non-default argument {f.name!r} '
                                'follows default argument')

    globals = {'MISSING': MISSING,
               '_HAS_DEFAULT_FACTORY': dataclasses._HAS_DEFAULT_FACTORY}

    body_lines = []
    for f in fields:
        line = dataclasses._field_init(f, False if isinstance(f, RXField) else frozen, globals, self_name)
        # line is None means that this field doesn't require
        # initialization (it's a pseudo-field).  Just skip it.
        if line:
            body_lines.append(line)

    # Does this class have a post-init function?
    if has_post_init:
        params_str = ','.join(f.name for f in fields
                              if f._field_type is dataclasses._FIELD_INITVAR)
        body_lines.append(f'{self_name}.{dataclasses._POST_INIT_NAME}({params_str})')

    # If no body lines, use 'pass'.
    if not body_lines:
        body_lines = ['pass']


    locals = {f'_type_{f.name}': f.type for f in fields}
    return dataclasses._create_fn('__init__',
                      [self_name] + [dataclasses._init_param(f) for f in fields if f.init],
                      body_lines,
                      locals=locals,
                      globals=globals,
                      return_type=None)


def _process_class(_cls, rxoptions, *args):
    assert '__setattr__' not in _cls.__dict__, f'Cannot overwrite attribute __setattr__ in class {_cls.__name__}'
    orig_init_fn = dataclasses._init_fn
    dataclasses._init_fn = _rx_init_fn
    dc = dataclasses._process_class(_cls, *args)
    dataclasses._init_fn = orig_init_fn

    params = getattr(dc, dataclasses._PARAMS)

    rx_data_fields = fields(dc)

    for field in filter(lambda field: field.name in dc.__annotations__, rx_data_fields):
        field.rx.update_ambigous_options(rxoptions)


    __init__ = dc.__init__

    __orig_setattr__ = dc.__setattr__

    @wraps(__init__)
    def init(self, *args, **kwargs):
        rxfields = fields(type(self))

        disposed = []
        initialization = defaultdict(list)

        def finalize(*disposable):
            [weakref.finalize(self, disposing.dispose) for disposing in disposable]
            return disposable

        def dispose(*disposable):
            disposed.extend((disposing.dispose for disposing in disposable))

        def evolution(field, evolves):
            for evolve in evolves:
                yield evolve(field=field) if isinstance(evolve, partial) else evolve

        for field in rxfields:
            field.rx.subject[self] = RXFieldSubjectValue(rxsubject.Subject(), rxsubject.Subject(), [])

        for field in rxfields:
            subject = field.rx.subject[self]


            finalize(subject.pivot.pipe(*evolution(field,
                                                    field.rx.evolves)).subscribe(subject.terminal))

            finalize(subject.terminal.subscribe(on_next=partial(object.__setattr__,
                                                                self,
                                                                field.name)))

            if field.rx.observes:
                combined = field.rx.combine(combine=field.rx.observes,
                                            merging=field.rx.safe_merge_if_possible,
                                            instance=self)


                subject.combines.append(combined)
                finalize(combined.pipe(rxo.filter_indexed(lambda v, i: bool(i)))
                                 .subscribe(subject.pivot))

                dispose(combined.pipe().subscribe(on_next=initialization[field].append))



        __init__.__get__(self, dc)(*args, **kwargs)

        [dispose() for dispose in disposed]
        for field, observed in initialization.items():
            
            if observed and field.rx.options.init_observes:
                field.rx.subject[self].pivot.on_next(observed[-1])

        if params.frozen:
            for field in rxfields:
                del field.rx.subject[self]

    dc.__init__ = init


    if not hasattr(dc.__setattr__, RX.SETATTR_MARK):
        @wraps(dc.__setattr__)
        def __setattr(self, name, value):
            names = list(f.name for f in fields(type(self)))
            if name in names:
                field = RXField.instance(self, name)
                if self in field.rx.subject:
                    subject = field.rx.subject[self]
                    if field.rx.options.setattr_evolves:
                        subject = subject.pivot
                    else:
                        subject = subject.terminal
                    return subject.on_next(value)

            __orig_setattr__.__get__(self, dc)(name, value)
        setattr(__setattr, RX.SETATTR_MARK, True)
        dc.__setattr__ = __setattr

    return dc



def dataclass(_cls=None, *,
              rx: typing.Union[RX.DataclassOptions, typing.Mapping] = MISSING,
              **kwargs):

    args = getargspec(dataclasses.dataclass).kwonlydefaults.copy()
    args.update(kwargs)

    if rx is MISSING:
        rx = RX.DataclassOptions(init_evolves=not kwargs.get('frozen', False))

    if isinstance(rx, typing.Mapping):
        rx = copy(rx)
        rx.setdefault('init_evolves', not kwargs.get('frozen', False))
        rx = RX.DataclassOptions(**rx)

    def wrap(cls):
        return _process_class(cls, rx, *args.values())

    if _cls is None:
        return wrap

    return wrap(_cls)


def make_dataclass(cls_name, fields, *, rx=RX.DataclassOptions(), bases=(), namespace=None, init=True,
                   repr=True, eq=True, order=False, unsafe_hash=False,
                   frozen=False):
    if namespace is None:
        namespace = {}
    else:
        namespace = namespace.copy()

    seen = set()
    anns = {}
    for item in fields:
        if isinstance(item, str):
            name = item
            tp = 'typing.Any'
        elif len(item) == 2:
            name, tp, = item
        elif len(item) == 3:
            name, tp, spec = item
            namespace[name] = spec
        else:
            raise TypeError(f'Invalid field: {item!r}')

        if not isinstance(name, str) or not name.isidentifier():
            raise TypeError(f'Field names must be valid identifers: {name!r}')
        if keyword.iskeyword(name):
            raise TypeError(f'Field names must not be keywords: {name!r}')
        if name in seen:
            raise TypeError(f'Field name duplicated: {name!r}')

        seen.add(name)
        anns[name] = tp

    namespace['__annotations__'] = anns

    cls = types.new_class(cls_name, bases, {}, lambda ns: ns.update(namespace))
    return dataclass(cls, rx=rx, init=init, repr=repr, eq=eq, order=order,
                     unsafe_hash=unsafe_hash, frozen=frozen)
