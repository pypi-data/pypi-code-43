import sys
import functools

import numpy as np

from typing import (
    TypeVar, Any, Iterable,
    List, Dict, Callable,
    Union, overload)

from joblib import Parallel, delayed, cpu_count


T = TypeVar('T')


def _yield_chunks(data_list: List[T], n: int) -> Iterable[List[T]]:
    """ Inspired by np.array_split
    """
    if n <= 0:
        raise RuntimeError(f'`n` must be strictly positive (is {n})')

    num, extras = divmod(len(data_list), n)
    chunk_sizes = ([0] + extras * [num+1] + (n-extras) * [num])
    div_points = np.array(chunk_sizes).cumsum()

    for i in range(n):
        yield data_list[div_points[i]:div_points[i+1]]


@overload
def execute_parallel(
    data_list: List[T], exec_func: Callable[..., List[Any]],
    args: Iterable[str] = (), kwargs: Dict[str, Any] = {},
    n_jobs: int = 0
) -> List[Any]:
    ...


@overload  # noqa: F811
def execute_parallel(
    data_list: List[T], exec_func: Callable[..., Dict[Any, Any]],
    args: Iterable[str] = (), kwargs: Dict[str, Any] = {},
    n_jobs: int = 0
) -> Dict[Any, Any]:
    ...


def execute_parallel(  # noqa: F811
    data_list: List[T],
    exec_func: Callable[..., Union[List[Any], Dict[Any, Any]]],
    args: Iterable[str] = (), kwargs: Dict[str, Any] = {},
    n_jobs: int = 0
) -> Union[List[Any], Dict[Any, Any]]:
    """ Split the given dataset into chunks which are then worked on in parallel
    """
    # sanity checks
    if not (isinstance(data_list, list) or isinstance(data_list, np.ndarray)):
        raise TypeError(f'Invalid input type "{type(data_list)}"')

    if len(data_list) == 0:
        return []

    # split input list into chunks
    n_jobs = min(n_jobs or int(cpu_count() * 3/4), len(data_list))
    chunks = list(_yield_chunks(data_list, n_jobs))

    # execute function
    print(
        f'Parallelizing "{exec_func.__name__}" ' +
        f'({len(chunks)} chunks over {n_jobs} jobs)',
        file=sys.stderr)

    result = Parallel(n_jobs=n_jobs)(
        delayed(exec_func)(item_sub, *args, **kwargs)
        for item_sub in chunks)

    # assemble results
    if isinstance(result[0], list):
        return [entry for sub in result for entry in sub]
    elif isinstance(result[0], dict):
        # assert unique keys
        keys = [k for sub in result for k in sub.keys()]
        assert len(keys) == len(set(keys)), f'Non-unique keys: {keys}'

        return {k: v for sub in result for k, v in sub.items()}
    else:
        raise RuntimeError(f'Invalid result entry type "{type(result[0])}"')


def parallel_chunks(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(list_data: List[Any], *args: Any, **kwargs: Any) -> Any:
        return execute_parallel(list_data, func, args=args, kwargs=kwargs)
    return wrapper
