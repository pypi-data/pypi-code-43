from .utils import work_in_progress_path, work_in_progress_directory, results_path
import os
from typing import Dict
from touch import touch
import shutil


def skip(holdout_key: str, hyper_parameters: Dict, results_directory: str) -> bool:
    """Default function to choose to load or not a given holdout.
        holdout_key: str, holdout_key identifier of holdout to be skipped.
        hyper_parameters: Dict, hyper parameters to check for.
        results_directory: str, directory where to store the results.
    """
    return (
        is_work_in_progress(results_directory, holdout_key, hyper_parameters) or
        os.path.exists(results_path(
            results_directory,
            holdout_key,
            hyper_parameters
        ))
    )


def add_work_in_progress(results_directory: str, holdout_key: str, hyper_parameters: Dict = None):
    """Sign given holdout holdout_key as under processing for given results directory.
        results_directory: str, directory where results are stored.
        holdout_key: str, holdout_key identifier of holdout.
        hyper_parameters: Dict, hyper parameters to check for.
    """
    if skip(holdout_key, hyper_parameters, results_directory):
        raise ValueError("Given holdout_key {holdout_key} for given directory {results_directory} is already work in progress or completed!".format(
            holdout_key=holdout_key,
            results_directory=results_directory
        ))
    touch(work_in_progress_path(results_directory, holdout_key, hyper_parameters))


def remove_work_in_progress(results_directory: str, holdout_key: str, hyper_parameters: Dict = None):
    """Remove given holdout holdout_key as under processing for given results directory.
        results_directory: str, directory where results are stored.
        holdout_key: str, holdout_key identifier of holdout.
        hyper_parameters: Dict, hyper parameters to check for.
    """
    if is_work_in_progress(results_directory, holdout_key, hyper_parameters):
        os.remove(work_in_progress_path(
            results_directory, holdout_key, hyper_parameters))
    else:
        raise ValueError("Given holdout_key {holdout_key} for given directory {results_directory} is not work in progress!".format(
            holdout_key=holdout_key,
            results_directory=results_directory
        ))


def is_work_in_progress(results_directory: str, holdout_key: str, hyper_parameters: Dict = None) -> bool:
    """Return boolean representing if given holdout_key is under work for given results directory.
        results_directory: str, directory where results are stored.
        holdout_key: str, holdout_key identifier of holdout.
        hyper_parameters: Dict, hyper parameters to check for.
    """
    return os.path.isfile(work_in_progress_path(results_directory, holdout_key, hyper_parameters))


def clear_work_in_progress(results_directory: str):
    """Delete work in progress log for given results directory.
        results_directory: str, directory where results are stored.
    """
    if os.path.exists(work_in_progress_directory(results_directory)):
        shutil.rmtree(work_in_progress_directory(results_directory))
