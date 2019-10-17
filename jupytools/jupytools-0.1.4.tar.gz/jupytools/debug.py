def is_notebook() -> bool:
    """A workaround to distinguish between Jupyter sessions and
    plain python console runs.

    Reference:
        https://stackoverflow.com/questions/15411967/
        how-can-i-check-if-code-is-executed-in-the-ipython-notebook

    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter


def is_debug() -> bool:
    """Checks if DEBUG env variable is set to True value."""
    import os
    debug = os.environ.get('DEBUG')
    if not debug: return False
    try:
        return int(debug) >= 1
    except ValueError:
        return bool(debug)


def auto_set_trace(debug: bool = True) -> 'Callable':
    """Automatically picks proper set_trace function depending on where
    the script is executed (Jupyter vs terminal) and which debugger tool
    (ipdb, pudb or pdb) is available.

    If debug is False then no-operation function is returned.

    XXX: probably don't need this function with python >= 3.7 (see PEP 553).
    """
    if debug:
        if is_notebook():
            from IPython.core.debugger import set_trace
            result = 'ipdb'
        else:
            try:
                from pudb import set_trace
                result = 'pudb'
            except ImportError:
                from pdb import set_trace
                result = 'pdb'
    else:
        def set_trace(*args, **kwargs): pass
        result = 'noop'
    print(f'Version of set_trace(): {result}')
    return set_trace
