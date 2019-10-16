import functools


def run_once(func):
    """ The decorated function will only run once. Other calls to it will
    return None. The original implementation can be found on StackOverflow(https://stackoverflow.com/questions/4103773/efficient-way-of-having-a-function-only-execute-once-in-a-loop)

    :param func: the function to be limited to run once only
    :return: the decorated function
    """  # noqa

    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        if not func_wrapper.has_run:
            func_wrapper.has_run = True
            return func(*args, **kwargs)

    func_wrapper.has_run = False
    return func_wrapper
