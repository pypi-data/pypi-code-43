import datetime
import inspect

from . import lexer, parser, errors, walker
from . import eval as evil

from .language import Language


def generate(text, dates=None, deltas=None, _parser=None, _lexer=None, _evaler=None):
    _parser = _parser or parser.Parser
    _lexer = _lexer or lexer.Lexer
    _evaler = _evaler or evil.Evaluator

    with _lexer(text) as l:
        lexed = list(l)

    with _parser(list(lexed)) as p:
        parsed = list(p)

    with _evaler(parsed, date_factory=dates, delta_factory=deltas) as evaled:
        yield from evaled


def tree(text, _parser=None, _lexer=None):
    _parser = _parser or parser.Parser
    _lexer = _lexer or lexer.Lexer
    with _lexer(text) as l:
        lexed = list(l)

    with _parser(list(lexed)) as p:
        yield from p


def replace(text, **kwargs):
    return ''.join(map(str, generate(text, **kwargs)))


def parse(text, default=None, **kwargs):
    '''Attempts to extract a single datetime or timedelta object.
    If neither is found it will return the default value.
    '''
    items = list(generate(text, **kwargs))
    if len(items) == 0:
        return default
    return items.pop(0)


def range(start, stop=None, step='24 hours', **kwargs):
    '''Iterates through a range of dates yielding a datetime object every
    step. If start is later than stop it will assume step is inverted
    and traverse backwards appropriately.
    '''
    if stop is None:
        stop = start
        start = 'now'

    good_start = parse(start, default=None, **kwargs)
    good_end = parse(stop, default=None, **kwargs)

    good_step = parse(step, **kwargs)

    for original, check in [(start, good_start), (stop, good_end), (step, good_step)]:
        if check is None:
            raise errors.UnableToParse(f'Could not parse "{original}"')

    if good_start > good_end:
        check = '__gt__'
        good_step = -1 * good_step
    else:
        check = '__lt__'

    while getattr(good_start, check)(good_end):
        yield good_start
        good_start = good_start + good_step

    yield good_end
