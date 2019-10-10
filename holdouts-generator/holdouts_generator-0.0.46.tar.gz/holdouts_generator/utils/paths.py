from dict_hash import sha256
from typing import Dict, Callable
import os


def mkdir(path_function: Callable) -> Callable:
    """Decorator for automatically create directory for path returned from given function."""
    def wrapper(*args, **kwargs):
        path = path_function(*args, **kwargs)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        return path
    return wrapper


@mkdir
def holdout_pickle_path(cache_directory: str, holdouts_parameters: Dict) -> str:
    """Return path where to pickle an holdout created with given parameters.
        cache_directory: str, directory where to store the holdouts cache.
        holdouts_parameters: Dict, hyper parameters used to create the holdouts.
    """
    return "{results_directory}/holdouts/{hash}.pickle.gz".format(
        results_directory=cache_directory,
        hash=sha256(holdouts_parameters)
    )


@mkdir
def holdout_cache_path(cache_directory: str, holdouts_parameters: Dict) -> str:
    """Return path where to store the cache file, recording the created holdout.
        cache_directory: str, directory where to store the holdouts cache.
    """
    return "{cache_directory}/cache/{holdouts_parameters}.json".format(
        cache_directory=cache_directory,
        holdouts_parameters=sha256(holdouts_parameters)
    )


@mkdir
def hyper_parameters_path(results_directory: str, holdout_key: str, hyper_parameters: Dict) -> str:
    """Return path where to store metrics tracked during history.
        results_directory: str, directory where to store the prediction_labels.
        holdout_key:str, key that identifies the holdout used for training.
        hyper_parameters: Dict, hyperparameters used to train the model.
    """
    return "{results_directory}/hyper_parameters/{key}.json".format(
        results_directory=results_directory,
        key=sha256({
            "hyper_parameters": hyper_parameters,
            "holdout_key": holdout_key
        })
    )


@mkdir
def parameters_path(results_directory: str, holdout_key: str, hyper_parameters: Dict) -> str:
    """Return path where to store metrics tracked during history.
        results_directory: str, directory where to store the prediction_labels.
        holdout_key:str, key that identifies the holdout used for training.
        hyper_parameters: Dict, hyperparameters used to train the model.
    """
    return "{results_directory}/parameters/{key}.json".format(
        results_directory=results_directory,
        key=sha256({
            "hyper_parameters": hyper_parameters,
            "holdout_key": holdout_key
        })
    )


@mkdir
def history_path(results_directory: str, holdout_key: str, hyper_parameters: Dict) -> str:
    """Return path where to store metrics tracked during history.
        results_directory: str, directory where to store the prediction_labels.
        holdout_key:str, key that identifies the holdout used for training.
        hyper_parameters: Dict, hyperparameters used to train the model.
    """
    return "{results_directory}/histories/{key}.csv".format(
        results_directory=results_directory,
        key=sha256({
            "hyper_parameters": hyper_parameters,
            "holdout_key": holdout_key
        })
    )


@mkdir
def trained_model_path(results_directory: str, holdout_key: str, hyper_parameters: Dict) -> str:
    """Return default path for storing the model trained with given holdout key and given parameters.
        results_directory: str, directory where to store the prediction_labels.
        holdout_key:str, key that identifies the holdout used for training.
        hyper_parameters: Dict, hyperparameters used to train the model.
    """
    return "{results_directory}/trained_models/{key}.h5".format(
        results_directory=results_directory,
        key=sha256({
            "hyper_parameters": hyper_parameters,
            "holdout_key": holdout_key
        })
    )


@mkdir
def results_path(results_directory: str, holdout_key: str, hyper_parameters: Dict) -> str:
    """Return default path for storing the main results csv.
        results_directory: str, directory where to store the prediction_labels.
        holdout_key:str, key that identifies the holdout used for training.
        hyper_parameters: Dict, hyperparameters used to train the model.
    """
    return "{results_directory}/results/{key}.json".format(
        results_directory=results_directory,
        key=sha256({
            "holdout_key": holdout_key,
            "hyper_parameters": hyper_parameters
        })
    )


def work_in_progress_directory(results_directory: str) -> str:
    """Return default path for storing work in progress temporary files.
        results_directory: str, directory where to store the prediction_labels.
    """
    return "{results_directory}/work_in_progress".format(
        results_directory=results_directory
    )


@mkdir
def work_in_progress_path(results_directory: str, holdout_key: str, hyper_parameters: str) -> str:
    """Return default path for storing the main work in progress csv.
        results_directory: str, directory where to store the prediction_labels.
        holdout_key:str, key that identifies the holdout used for training.
        hyper_parameters: Dict, hyperparameters used to train the model.
    """
    return "{wip}/{key}".format(
        wip=work_in_progress_directory(results_directory),
        key=sha256({
            "hyper_parameters": hyper_parameters,
            "holdout_key": holdout_key
        })
    )


@mkdir
def predictions_labels_path(results_directory: str, holdout_key: str, hyper_parameters: str) -> str:
    """Return default path for prediction labels.
        results_directory: str, directory where to store the prediction_labels.
        holdout_key:str, key that identifies the holdout used for training.
        hyper_parameters: Dict, hyperparameters used to train the model.
    """
    return "{results_directory}/predictions_labels/{key}.csv".format(
        results_directory=results_directory,
        key=sha256({
            "holdout_key": holdout_key,
            "hyper_parameters": hyper_parameters
        })
    )


@mkdir
def true_labels_path(results_directory: str, holdout_key: str, hyper_parameters: str) -> str:
    """Return default path for true labels.
        results_directory: str, directory where to store the true_labels.
        holdout_key:str, key that identifies the holdout used for training.
        hyper_parameters: Dict, hyperparameters used to train the model.
    """
    return "{results_directory}/true_labels/{key}.csv".format(
        results_directory=results_directory,
        key=sha256({
            "holdout_key": holdout_key,
            "hyper_parameters": hyper_parameters
        })
    )
