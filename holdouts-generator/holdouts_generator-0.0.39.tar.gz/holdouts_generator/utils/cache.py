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
        key = get_holdout_key(cache_dir, **parameters)
        if key is not None and not is_valid_holdout_key(path, key):
            raise ValueError("Holdout has been tempered with!")
        return compress_pickle.load(path), key
    except (pickle.PickleError, FileNotFoundError, AttributeError,  EOFError, ImportError, IndexError, zlib.error):
        pass
    data = odd_even_split(generator(dataset))
    if os.path.exists(path):
        # In case two competing processes tried to create the same holdout.
        # It can happen only when the generation of the holdout requires a great
        # deal of time.
        return (None, None), key
    compress_pickle.dump(data, path)
    key = hash_file(path)
    store_cache(path, key, parameters, cache_dir)
    return data, key


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


def clear_invalid_cache(cache_dir: str = ".holdouts"):
    """Remove the holdouts that do not map to a valid cache.
        cache_dir:str=".holdouts", the holdouts cache directory to be removed.
    """
    for cache_path in glob("{cache_dir}/cache/*.json".format(cache_dir=cache_dir)):
        cache = load(cache_path)
        if not is_valid_holdout_key(cache["path"], cache["key"]):
            if os.path.exists(cache["path"]):
                os.remove(cache["path"])
            os.remove(cache_path)


def clear_invalid_results(results_directory: str = "results", cache_dir: str = ".holdouts"):
    """Remove the results that do not map to a valid holdout cache.
        results_directory: str = "results", directory where results are stores.
        cache_dir:str=".holdouts", the holdouts cache directory to be removed.
    """
    clear_invalid_cache(cache_dir)
    cache = pd.DataFrame([
        load(cache_path) for cache_path in glob("{cache_dir}/cache/*.json".format(cache_dir=cache_dir))
    ])
    for result_path in glob("{results_directory}/results/*.json".format(results_directory=results_directory)):
        key = load(result_path)["holdouts_key"]
        if "key" in cache and key not in cache.key:
            os.remove(result_path)


def clear_cache(cache_dir: str = ".holdouts"):
    """Remove the holdouts cache directory.
        cache_dir:str=".holdouts", the holdouts cache directory to be removed.
    """
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
