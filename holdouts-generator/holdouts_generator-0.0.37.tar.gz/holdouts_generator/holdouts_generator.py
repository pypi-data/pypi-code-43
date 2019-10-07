import os
import shutil
from tqdm.auto import tqdm
from typing import List, Callable, Dict, Generator
from .utils import get_level_description, cached, uncached, get_holdout_key
import gc


def empty_generator(*args, **kwargs):
    return []


def _holdouts_generator(*dataset: List, holdouts: List, cacher: Callable, cache_dir: str = None, skip: Callable[[str, Dict, str], bool] = None, level: int = 0, verbose: bool = True):
    """Return validation dataset, its key and another holdout generator.
        dataset, iterable of datasets to generate holdouts from.
        holdouts:List, list of holdouts callbacks.
        cacher:Callable, function used to store the cache.
        cache_dir:str=".holdouts", the holdouts cache directory.
        skip:Callable[str, bool], the callback for choosing to load or not a given holdout.
        level:int=0, the level of the current holdout.
        verbose:bool=True, wethever to show loading bars or not.
    """
    if holdouts is None:
        return None

    def generator(hyper_parameters: Dict = None, results_directory: str = "results"):
        for number, (outer, parameters, inner) in enumerate(tqdm(holdouts, disable=not verbose, desc=get_level_description(level))):
            if cache_dir:
                key = get_holdout_key(cache_dir, **parameters,
                                    level=level, number=number)
            if cache_dir is not None and skip is not None and key is not None and skip(key, hyper_parameters, results_directory):
                yield (None, None), key, empty_generator
            else:
                gc.collect()
                (train, test), key = cacher(outer, dataset, cache_dir,
                                   **parameters, level=level, number=number)
                gc.collect()
                if train is None:
                    yield (None, None), key, empty_generator
                yield (train, test), key, _holdouts_generator(
                    *train,
                    holdouts=inner,
                    cacher=cacher,
                    cache_dir=cache_dir,
                    skip=skip,
                    level=level+1,
                    verbose=verbose
                )
    return generator


def remove_key(generator: Generator):
    if generator is None:
        return None

    def filtered(hyper_parameters: Dict = None, results_directory: str = "results"):
        for values, _, inner in generator(hyper_parameters, results_directory):
            yield values, remove_key(inner)
    return filtered


def holdouts_generator(*dataset: List, holdouts: List, verbose: bool = True):
    """Return validation dataset, its key and another holdout generator
        dataset, iterable of datasets to generate holdouts from.
        holdouts:List, list of holdouts callbacks.
        verbose:bool=True, wethever to show loading bars or not.
    """
    return remove_key(_holdouts_generator(*dataset, holdouts=holdouts, cacher=uncached, verbose=verbose))


def cached_holdouts_generator(*dataset: List, holdouts: List, cache_dir: str = ".holdouts", skip: Callable[[str, Dict, str], bool] = None, verbose: bool = True):
    """Return validation dataset, its key and another holdout generator
        dataset, iterable of datasets to generate holdouts from.
        holdouts:List, list of holdouts callbacks.
        cache_dir:str=".holdouts", the holdouts cache directory.
        skip:Callable[str, bool], the callback for choosing to load or not a given holdout.
        verbose:bool=True, wethever to show loading bars or not.
    """
    return _holdouts_generator(*dataset, holdouts=holdouts, cacher=cached, cache_dir=cache_dir, skip=skip, verbose=verbose)