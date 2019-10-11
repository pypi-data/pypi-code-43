from contextlib import contextmanager
from typing import Any, Dict, Callable

_context = {}


def _reset_context():
    _context.clear()


def get_context() -> Dict[str, Any]:
    """
    Retrieve the current build context

    :return:                        a dictionary describing the current build context
    """
    return _context


@contextmanager
def new_context(**kwargs: Any) -> Dict[str, Any]:
    """
    Create a new context for the duration of a with-block

    :param kwargs:                  entries to initialize the context with
    :return:                        the context
    """
    try:
        global _context
        _context = {**_context, **kwargs}
        yield get_context()
    finally:
        _reset_context()


class _BuilderFunject:
    def __init__(self, wrapped_function, **kwargs):
        self.wrapped_function = wrapped_function
        self.options = kwargs

    def __call__(self, *args, **kwargs):
        return self.wrapped_function(*args, **kwargs)


class _FetcherFunject:
    def __init__(self, wrapped_function, **kwargs):
        self.wrapped_function = wrapped_function
        self.options = kwargs

    def __call__(self, *args, **kwargs):
        return self.wrapped_function(*args, **kwargs)


class _InspectorFunject:
    def __init__(self, wrapped_function,
                 critical: bool = False,
                 post_process: Callable[[], None] = None,
                 checklist_entry: str = None,
                 **kwargs):
        self.wrapped_function = wrapped_function
        self.is_critical = critical
        self.post_process = post_process
        self.checklist_entry = checklist_entry
        self.options = kwargs

    def __call__(self, *args, **kwargs):
        return self.wrapped_function(*args, **kwargs)


_builders = []
_fetchers = []
_inspectors = []


def _reset_registries():
    global _builders
    global _fetchers
    global _inspectors
    _builders = []
    _fetchers = []
    _inspectors = []


@contextmanager
def create_registries():
    """
    Create registries for functions marked as builders, fetchers, and inspectors, for the duration of a with-block

    :return:                        a tuple containing the three registries
    """
    try:
        yield _builders, _fetchers, _inspectors
    finally:
        _reset_registries()


def builder(*args, **kwargs):
    """
    Decorator used to mark a function as a builder
    """
    if len(args) > 0:
        if len(args) != 1:
            raise ValueError("only keyword arguments can be passed to quixote.builder")
        f = args[0]
        _builders.append(_BuilderFunject(f, **kwargs))
        return f
    else:
        return lambda f: _builders.append(_BuilderFunject(f, **kwargs))


def fetcher(*args, **kwargs):
    """
    Decorator used to mark a function as a fetcher
    """
    if len(args) > 0:
        if len(args) != 1:
            raise ValueError("only keyword arguments can be passed to quixote.fetcher")
        f = args[0]
        _fetchers.append(_FetcherFunject(f, **kwargs))
        return f
    else:
        return lambda f: _fetchers.append(_FetcherFunject(f, **kwargs))


def inspector(*args, **kwargs):
    """
    Decorator used to mark a function as an inspector

    :param critical:                whether or not the inspection phase should be aborted if this step fails (default is False)
    """
    if len(args) > 0:
        if len(args) != 1:
            raise ValueError("only keyword arguments can be passed to quixote.inspector")
        f = args[0]
        _inspectors.append(_InspectorFunject(f, **kwargs))
        return f
    else:
        return lambda f: _inspectors.append(_InspectorFunject(f, **kwargs))


class Blueprint:
    """
    Class representing the blueprint of an automated-test job
    """

    def __init__(self, name: str, author: str, inspection_file: str = None, allow_docker: bool = False):
        """
        Create a blueprint

        :param name:                the name of the blueprint
        :param author:              the author of the blueprint
        :param inspection_file:     the file containing additional inspector functions
        :param allow_docker:        whether a docker engine should be made available in the inspection step
        """
        self.name = name
        self.author = author
        self.inspection_file = inspection_file
        self.allow_docker = allow_docker
        self.builders = []
        self.fetchers = []
        self.inspectors = []

    def register_functions(self, builders=None, fetchers=None, inspectors=None):
        """
        Register functions marked as builders, fetchers, or inspectors in the blueprint

        :param builders:            the list of collected builders
        :param fetchers:            the list of collected fetchers
        :param inspectors:          the list of collected inspectors
        """
        self.builders = builders or []
        self.fetchers = fetchers or []
        self.inspectors = inspectors or []
        return self
