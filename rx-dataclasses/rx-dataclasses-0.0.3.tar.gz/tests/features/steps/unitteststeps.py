from os import chdir, environ
import typing
from contextlib import contextmanager
import builtins
from importlib import import_module
import importlib.util
from pathlib import Path
from collections import namedtuple, defaultdict
from functools import wraps
import pytest
import behave

def step(text):
    @wraps(behave.step)
    def _step(function):
        @wraps(function)
        def _function(context, *args, **kwargs):
            if not hasattr(context, 'space'):
                context.space = defaultdict(dict)
            if not hasattr(context, 'spacehistory'):
                context.spacehistory = defaultdict(list)
            return function(context, *args, **kwargs)
        return behave.step(text)(_function)
    return _step


def imported(module, attribute):
    obj = import_module(module)
    if isinstance(attribute, (bytes, str)):
        attribute = attribute.split('.')
    for attr in attribute:
        obj = getattr(obj, attr)
    return obj

@step('imported {space} `{module}:{attribute}` as `{name}`')
def imported_name(context, module, attribute, space, name):
    context.space[space][name] = imported(module, attribute)
    context.spacehistory[space].append(object)


@step('imported {space} `{module}:{attribute}`')
def imported_into_space(context, space, module, attribute):
    context.spacehistory[space].append(imported(module, attribute))


@step('sample from `{py_source_path}:{attribute}`')
def sample_object_from_source(context, py_source_path, attribute):

    name = f'{py_source_path}:{attribute}'
    module_path = Path(context._config.base_dir) / py_source_path
    spec = importlib.util.spec_from_file_location('sample', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    attribute = attribute.split('.')
    context.space['sample'][name] = getattr(module, attribute[0])
    for attr in attribute[1:]:
        context.space['sample'][name] = getattr(context.space['sample'][name], attr)

    context.spacehistory['sample'].append(context.space['sample'][name])

@step('{destspace} created by calling imported `{module}:{attribute}` on arguments {argspace}')
def object_created_by_imported_with_args(context, destspace, module, attribute, argspace):
    callable = imported(module, attribute)
    argument = context.spacehistory[argspace][-1]
    context.spacehistory[destspace].append(callable(*argument))


@step('{destspace} created by calling imported `{module}:{attribute}` on keywords {argspace}')
def object_created_by_imported_with_kwargs(context, destspace, module, attribute, argspace):
    callable = imported(module, attribute)
    print(callable.__doc__)
    argument = context.spacehistory[argspace][-1]
    context.spacehistory[destspace].append(callable(**argument))


@step('{destspace} created by calling imported `{module}:{attribute}` on {argspace}')
def object_created_by_function(context, destspace, module, attribute, argspace):
    callable = imported(module, attribute)
    argument = context.spacehistory[argspace][-1]
    context.spacehistory[destspace].append(callable(argument))


@step('{destspace} created by calling {callable_space} on keywords {kwargs_space}')
def object_created_by_calling_space_with_kwargs(context, destspace, callable_space, kwargs_space):
    callable = context.spacehistory[callable_space][-1]
    kwargs = context.spacehistory[kwargs_space][-1]
    context.spacehistory[destspace].append(callable(**kwargs))

@step('{destspace} created by calling {callable_space} on arguments {args_space}')
def object_created_by_calling_space_with_kwargs(context, destspace, callable_space, args_space):
    callable = context.spacehistory[callable_space][-1]
    args = context.spacehistory[args_space][-1]
    context.spacehistory[destspace].append(callable(*args))


@step('{destspace} `{dest}` created by calling {callspace} `{function}` on {argspace} `{arg}`')
def object_created_by_function(context, destspace, dest, callspace, function, argspace, arg):
    value = context.space[callspace][function](context.space[argspace][arg])
    context.space[destspace][dest] = value
    context.spacehistory[destspace].append(value)


@step('{destspace} `{dest}` created by calling {callspace} `{function}`')
def object_created_by_function(context, destspace, dest, callspace, function):
    value = context.space[callspace][function]()
    context.space[destspace][dest] = value
    context.spacehistory[destspace].append(value)



UNIT = 'unit'

@contextmanager
def args_execution(context):
    columns = environ.get('COLUMNS', '110')
    environ['COLUMNS'] = '110'
    initial = Path().resolve()
    basedir = Path(context._config.base_dir) / UNIT
    try:
        chdir(str(basedir.resolve()))
        yield ['-s', '--rootdir', str(basedir)]
    finally:
        environ['COLUMNS'] = columns
        chdir(str(initial))
    

def collect_nodes(args, expressions=None, mark=None, files=None):

    if expressions is not None:
        for expression in expressions:
            args.extend(['-k', expression.strip()])

    if mark is not None:
        args.extend(['-m', f'{mark.strip()}'])

    if files is not None:
        args.extend(files)

    class BehaveCollectionPlugin:
        def __init__(self):
            self.items = []
        def pytest_itemcollected(self, item):
            self.items.append(item)

        def pytest_deselected(self, items):
            for item in items:
                self.items.remove(item)

    collection = BehaveCollectionPlugin()

    pytest.main(args=['--collect-only'] + args, plugins=[collection])

    nodeids = [item._nodeid for item in collection.items]
    assert nodeids
    return nodeids

@step('`{expressions}` is satisfied')
def pytest_collect_matched_expressions(context, expressions):
    with args_execution(context) as args:
        args.extend(['-p', 'no:terminal'])
        nodes = collect_nodes(args, expressions=expressions.split(','))
    if nodes:
        context.execute_steps(f'Then pytest run `{",".join(nodes)}`')

@step('`{expressions}` from `{files}` is satisfied with {space}')
def pytest_collect_matched_expressions_from_files(context, expressions, files, space):
    with args_execution(context) as args:
        args.extend(['-p', 'no:terminal'])
        nodes = collect_nodes(args, expressions=expressions.split(','), files=files.split(','))
    if nodes:
        context.execute_steps(f'Then pytest run `{",".join(nodes)}` with `{space}`')


@step('`{marks}` is satisfied with {space}')
def pytest_collect_marked_nodes(context, marks, space):
    '''
    `&` is treated as `and`
    `|` is treated as `or`
    repeating spaces are normalized
    '''
    with args_execution(context) as args:
        args.extend(['-p', 'no:terminal'])
        nodes = collect_nodes(args,
            mark=''.join(filter(bool, marks.replace('&', ' and ').replace(':', ' and ').replace('|', ' or '))))
    if nodes:
        context.execute_steps(f'Then pytest run `{",".join(nodes)}` with `{space}`')

@step('pytest run `{nodes}` with `{space}`')
def pytest_run_with_space(context, nodes, space):
    nodes = nodes.split(',')
    space = space
    class BehaveExecutionPlugin:
        @pytest.fixture(name='history', scope='function')
        def _history(self):
            return context.spacehistory[space]

        @pytest.fixture(name=space, scope='function')
        def _space(self):
            return context.space[space]

    with args_execution(context) as args:
        args.append('-vv')
        args.extend(nodes)
        assert pytest.main(args=args, plugins=[BehaveExecutionPlugin()]) is 0


@step('pytest run `{nodes}`')
def pytest_run(context, nodes):
    nodes = nodes.split(',')
    History = namedtuple('SpaceHistory', tuple(context.spacehistory.keys()))
    Space = namedtuple('Space', tuple(context.space.keys()))

    class BehaveExecutionPlugin:
        pass
        @pytest.fixture(name='history', scope='function')
        def history(self):
            return History(**context.spacehistory)

        @pytest.fixture(name='space', scope='function')
        def space(self):
            return Space(**context.space)

    with args_execution(context) as args:
        args.append('-vv')
        args.extend(nodes)
        assert pytest.main(args=args, plugins=[BehaveExecutionPlugin()]) is 0



