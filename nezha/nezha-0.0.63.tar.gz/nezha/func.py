from functools import wraps
from typing import Callable, Iterable, Mapping, List, Union, Any


def action_factory(key: str) -> Callable:
    actions = {
        'replace': lambda old, new: new,
        'prefix': lambda old, new: f'{new}{old}',
        'suffix': lambda old, new: f'{old}{new}',
    }
    return actions[key.lower().strip()]


def check_argument(check_func: Callable, arg_flag: Union[int, str],
                   crash_if_failed: bool = True, is_func_decorated: bool = True):
    def _check_argument(arg_flag: Union[int, str], check_func: Callable,
                        crash_if_failed: bool = True, *args, **kwargs) -> Any:
        arg = args[arg_flag] if isinstance(arg_flag, int) else kwargs.get(arg_flag)
        pass_checked = check_func(arg)
        if not pass_checked and crash_if_failed:
            raise ValueError(f'arg {arg} is invalid')
        return pass_checked

    def decorate(func):
        @wraps(func)
        def wrap_method(self, *args, **kwargs):
            _check_argument(arg_flag, check_func, crash_if_failed, *args, **kwargs)
            return func(self, *args, **kwargs)

        @wraps(func)
        def wrap_func(*args, **kwargs):
            _check_argument(arg_flag, check_func, crash_if_failed, *args, **kwargs)
            return func(*args, **kwargs)

        return wrap_func if is_func_decorated else wrap_method

    return decorate


def modify_positional_argument(index: int, val: str, action: str = 'replace', is_func_decorated: bool = True):
    """

    :param index: old positional argument index
    :param val:
    :param action:
        + if action == 'replace', old val -> val
        + if action == 'suffix', old val + val  -> val
        + if action == 'prefix', val + old val -> val
    :param is_func_decorated: if class method or instance method is decorated, self/cls should be passed.
    :return:

    example:

    @modify_positional_argument(0, 'xxxxx', action='prefix')
    def a(xx):
        print(xx)


    class A:

        @modify_positional_argument(0, 'xxxx', is_func_decorated=False)
        def a(self, x):
            print(x)
    """

    def generate_new_args(args: List, index: int, action: str, new_val) -> List:
        new_args = args.copy()
        new_args[index] = action_factory(action)(args[index], new_val)
        return new_args

    def decorate(func):
        @wraps(func)
        def wrap_method(self, *args, **kwargs):
            new_args = generate_new_args(list(args), index, action, val)
            return func(self, *new_args, **kwargs)

        @wraps(func)
        def wrap_func(*args, **kwargs):
            new_args = generate_new_args(list(args), index, action, val)
            return func(*new_args, **kwargs)

        return wrap_func if is_func_decorated else wrap_method

    return decorate


def modify_keyword_argument(new_pairs: Mapping, action: str = 'replace', is_func_decorated: bool = True):
    """

    :param new_pairs: new pair of keyword argument.
    :param action:
        + if action == 'replace', old val -> val
        + if action == 'suffix', old val + val  -> val
        + if action == 'prefix', val + old val -> val
    :param is_func_decorated: if class method or instance method is decorated, self/cls should be passed.
    :return:

    example:

    @modify_keyword_argument({'key': 4444}, action='prefix')
    def a(key=333):
        print(xx)


    class A:

        @modify_keyword_argument({'key': 4444}, action='prefix', is_func_decorated=False)
        def a(self, x):
            print(x)
    """

    def generate_new_pairs(new_pairs, kwargs, action):
        copied_kwargs = kwargs.copy()
        vals = {k: action_factory(action)(kwargs.get(k), new_val) for k, new_val in new_pairs.items()}
        copied_kwargs.update(vals)
        return copied_kwargs

    def decorate(func):
        @wraps(func)
        def wrap_method(self, *args, **kwargs):
            vals = generate_new_pairs(new_pairs, kwargs, action)
            return func(self, *args, **vals)

        @wraps(func)
        def wrap_func(*args, **kwargs):
            vals = generate_new_pairs(new_pairs, kwargs, action)
            return func(*args, **vals)

        return wrap_func if is_func_decorated else wrap_method

    return decorate


def loop(it: Iterable):
    while True:
        try:
            next(it)
        except StopIteration:
            break
