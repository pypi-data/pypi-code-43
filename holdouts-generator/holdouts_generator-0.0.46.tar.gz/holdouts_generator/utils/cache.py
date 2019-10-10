from typing import Callable, List, Dict
from .paths import holdout_pickle_path, holdout_cache_path
from .various import odd_even_split
from .hash import hash_file
from .json import load, dump
import pandas as pd
from glob import glob
import shutil
import zlib
import pickle
import compress_pickle
import os


def uncached(generator: Callable, dataset: List, *args, **kwargs):
    return odd_even_split(generator(dataset)), None


def cached(generator: Callable, dataset: List, cache_dir: str, **parameters: Dict):
    path = holdout_pickle_path(cache_dir, parameters)
    try:
        holdout_key = get_holdout_key(cache_dir, **parameters)
        if holdout_key is not None and not is_valid_holdout_key(path, holdout_key):
            raise ValueError("Holdout has been tempered with!")
        return compress_pickle.load(path), holdout_key
    except (pickle.PickleError, FileNotFoundError, AttributeError,  EOFError, ImportError, IndexError, zlib.error):
        pass
    data = odd_even_split(generator(dataset))
    if os.path.exists(path):
        # In case two competing processes tried to create the same holdout.
        # It can happen only when the generation of the holdout requires a great
        # deal of time.
        return (None, None), holdout_key
    compress_pickle.dump(data, path)
    holdout_key = hash_file(path)
    store_cache(path, holdout_key, parameters, cache_dir)
    return data, holdout_key


def is_valid_holdout_key(path: str, holdout_key: str) -> bool:
    """Return bool representing if given holdout_key is correct sign for given holdout's path.
        path:str, the holdout's path.
        holdout_key:str, the holdout's holdout_key.
    """
    try:
        return hash_file(path) == holdout_key
    except FileNotFoundError:
        return False


def can_save_result_to_holdout_key(holdout_key: str, cache_dir: str) -> bool:
    """Return bool representing if given holdout_key is correct sign for any given holdout.
        holdout_key:str, the holdout's holdout_key.
        cache_dir:str, the holdouts cache directory.
    """
    cache = load_valid_cache(cache_dir)
    return not cache.empty and cache.holdout_key.isin([holdout_key]).any()


def get_holdout_key(cache_dir: str, **holdout_parameters: Dict) -> str:
    """Return holdout_key, if cached, for given holdout else return None.
        cache_dir:str, cache directory to load data from
        holdout_parameters:Dict, parameters used to generated the holdout.
    """
    try:
        return load(holdout_cache_path(
            cache_dir,
            holdout_parameters
        ))["holdout_key"]
    except (FileNotFoundError, IndexError):
        return None


def store_cache(path: str, holdout_key: str, holdout_parameters: Dict, cache_dir: str):
    """Store the holdouts cache.
        path:str, the considered holdout path.
        holdout_key:str, the holdout holdout_key.
        holdout_parameters:Dict, dictionary of parameters used to generate holdout.
        cache_dir:str, the holdouts cache directory.
    """
    dump(
        {
            "path": path,
            "holdout_key": holdout_key,
            "parameters": holdout_parameters
        },
        holdout_cache_path(cache_dir, holdout_parameters)
    )


def clear_invalid_cache(cache_dir: str):
    """Remove the holdouts that do not map to a valid cache.
        cache_dir:str, the holdouts cache directory to be removed.
    """
    for cache_path in glob("{cache_dir}/cache/*.json".format(cache_dir=cache_dir)):
        cache = load(cache_path)
        if not is_valid_holdout_key(cache["path"], cache["holdout_key"]):
            if os.path.exists(cache["path"]):
                os.remove(cache["path"])
            os.remove(cache_path)


def load_valid_cache(cache_dir: str) -> pd.DataFrame:
    """Remove the holdouts that do not map to a valid cache and return valid cache dataframe.
        cache_dir:str, the holdouts cache directory to be removed.
    """
    clear_invalid_cache(cache_dir)
    return pd.DataFrame([
        load(cache_path) for cache_path in glob("{cache_dir}/cache/*.json".format(cache_dir=cache_dir))
    ])


def clear_invalid_results(results_directory: str, cache_dir: str):
    """Remove the results that do not map to a valid holdout cache.
        results_directory: str, directory where results are stores.
        cache_dir:str, the holdouts cache directory to be removed.
    """
    cache = load_valid_cache(cache_dir)
    for result_path in glob("{results_directory}/results/*.json".format(results_directory=results_directory)):
        result = load(result_path)
        if cache.empty or not cache.holdout_key.isin([result["holdout_key"]]).any():
            for holdout_key, path in result.items():
                if holdout_key.endswith("_path") and path is not None and os.path.exists(path):
                    os.remove(path)
            os.remove(result_path)


def clear_cache(cache_dir: str):
    """Remove the holdouts cache directory.
        cache_dir:str, the holdouts cache directory to be removed.
    """
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
