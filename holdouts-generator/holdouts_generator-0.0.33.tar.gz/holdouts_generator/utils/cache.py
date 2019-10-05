from typing import Callable, List, Dict
from .paths import holdout_pickle_path, holdout_cache_path
from .various import odd_even_split
from .hash import hash_file
from .json import load, dump
import zlib
import pickle
import compress_pickle


def uncached(generator: Callable, dataset: List, *args, **kwargs):
    return odd_even_split(generator(dataset)), None


def cached(generator: Callable, dataset: List, cache_dir: str, **parameters: Dict):
    path = holdout_pickle_path(cache_dir, parameters)
    try:
        key = get_holdout_key(cache_dir, **parameters)
        if key is not None and not is_valid_holdout_key(path, key):
            raise ValueError("Holdout has been tempered with!")
        return compress_pickle.load(path), key
    except (pickle.PickleError, FileNotFoundError, AttributeError,  EOFError, ImportError, IndexError, zlib.error):
        data = odd_even_split(generator(dataset))
    compress_pickle.dump(data, path)
    key = hash_file(path)
    store_cache(path, key, parameters, cache_dir)
    return (data, key)


def is_valid_holdout_key(path: str, key: str) -> bool:
    """Return bool representing if given key is correct sign for given holdout's path.
        path:str, the holdout's path.
        key:str, the holdout's key.
    """
    try:
        return hash_file(path) == key
    except FileNotFoundError:
        return False


def get_holdout_key(cache_dir: str, **holdout_parameters: Dict) -> str:
    """Return key, if cached, for given holdout else return None.
        cache_dir:str, cache directory to load data from
        holdout_parameters:Dict, parameters used to generated the holdout.
    """
    try:
        return load(holdout_cache_path(
            cache_dir,
            holdout_parameters
        ))["key"]
    except (FileNotFoundError, IndexError):
        return None


def store_cache(path: str, key: str, holdout_parameters: Dict, cache_dir: str):
    """Store the holdouts cache.
        path:str, the considered holdout path.
        key:str, the holdout key.
        holdout_parameters:Dict, dictionary of parameters used to generate holdout.
        cache_dir:str=".holdouts", the holdouts cache directory.
    """
    dump(
        {
            "path": path,
            "key": key,
            "parameters": holdout_parameters
        },
        holdout_cache_path(cache_dir, holdout_parameters)
    )
