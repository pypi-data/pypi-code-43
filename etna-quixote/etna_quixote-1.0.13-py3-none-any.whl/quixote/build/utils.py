import quixote.build.output as output


def setup_function(f):
    """
    Decorator used for functions that generate commands for the builder

    :param f:           the function to wrap
    """

    def run(*args, **kwargs):
        output.get_output().append(f(*args, **kwargs))
    run.__doc__ = f.__doc__
    return run
