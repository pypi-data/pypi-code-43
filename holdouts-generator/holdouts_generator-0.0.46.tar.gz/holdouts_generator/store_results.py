from typing import Dict
import os
import pandas as pd
import numpy as np
from .utils import results_path, hyper_parameters_path, parameters_path, history_path, trained_model_path, true_labels_path, predictions_labels_path
from .utils import dump, load
from .utils import can_save_result_to_holdout_key
from .work_in_progress import remove_work_in_progress, is_work_in_progress
from keras import Model
from glob import glob
import shutil
import humanize


def store_result(
    holdout_key: str,
    new_results: Dict,
    time: int,
    results_directory: str,
    cache_dir:str,
    hyper_parameters: Dict = None,
    parameters: Dict = None
):
    """Store given results in a standard way, so that the skip function can use them.
        holdout_key: str, holdout_key identifier of holdout to be skipped.
        new_results: Dict, results to store.
        time: int, time required for given result.
        results_directory: str, directory where to store the results.
        cache_dir:str, the holdouts cache directory.
        hyper_parameters: Dict, hyper parameters to check for.
        parameters: Dict, parameters used for tuning the model.
    """
    path = results_path(
        results_directory,
        holdout_key,
        hyper_parameters
    )
    if os.path.exists(path):
        raise ValueError("Given holdout_key {holdout_key} and hyper_parameters {hyper_parameters} map already to a result in directory {results_directory}!".format(
            holdout_key=holdout_key,
            hyper_parameters=hyper_parameters,
            results_directory=results_directory
        ))
    if not can_save_result_to_holdout_key(holdout_key, cache_dir):
        raise ValueError("Given holdout_key {holdout_key} does not map to a valid holdout in given cache directory {cache_dir}!".format(
            holdout_key=holdout_key,
            cache_dir=cache_dir
        ))
    hppath = None if hyper_parameters is None else hyper_parameters_path(
        results_directory, holdout_key, hyper_parameters)
    ppath = None if parameters is None else parameters_path(
        results_directory, holdout_key, hyper_parameters)
    dump({
        **new_results,
        "holdout_key": holdout_key,
        "hyper_parameters_path": hppath,
        "parameters_path": ppath,
        "required_time": time,
        "human_required_time": humanize.naturaldelta(time)
    }, path)
    if hyper_parameters is not None:
        dump(hyper_parameters, hppath)
    if parameters is not None:
        dump(parameters, ppath)
    if is_work_in_progress(results_directory, holdout_key, hyper_parameters):
        remove_work_in_progress(
            results_directory,
            holdout_key,
            hyper_parameters=hyper_parameters,
        )


def load_result(results_directory: str, holdout_key: str, hyper_parameters: Dict = None):
    """Return the result corresponding to given holdout_key and hyper_parameters in given results_directory.
        results_directory: str, directory where to store the results.
        holdout_key: str, holdout_key identifier of holdout to be skipped.
        hyper_parameters: Dict, hyper parameters to check for.
    """
    path = results_path(
        results_directory,
        holdout_key,
        hyper_parameters
    )
    if not os.path.exists(path):
        raise ValueError("Given holdout_key {holdout_key} and hyper_parameters {hyper_parameters} do not map to a result in {results_directory}!".format(
            holdout_key=holdout_key,
            hyper_parameters=hyper_parameters,
            results_directory=results_directory
        ))
    return load(path)


def store_keras_result(
    holdout_key: str,
    history: Dict,
    x_test: np.ndarray,
    y_test_true: np.ndarray,
    model: Model,
    time: int,
    results_directory: str,
    cache_dir:str,
    informations: Dict = None,
    hyper_parameters: Dict = None,
    parameters: Dict = None,
    save_model: bool = True
):
    """Store given keras model results in a standard way, so that the skip function can use them.
        holdout_key: str, holdout_key identifier of holdout to be skipped.
        history: Dict, training history to store.
        x_test:np.ndarray, input test values for the model.
        y_test_true:np.ndarray, true output test values.
        model:Model, model to save if save_model is True, used to predict the value.
        time: int, time required for given result.
        results_directory: str, directory where to store the results.
        cache_dir:str, the holdouts cache directory.
        hyper_parameters: Dict, hyper parameters to check for.
        parameters: Dict, parameters used for tuning the model.
        save_model:bool=True, whetever to save or not the model.
    """
    y_pred = model.predict(x_test)
    hpath = history_path(results_directory, holdout_key, hyper_parameters)
    mpath = trained_model_path(results_directory, holdout_key, hyper_parameters)
    plpath = predictions_labels_path(results_directory, holdout_key, hyper_parameters)
    tlpath = true_labels_path(results_directory, holdout_key, hyper_parameters)

    informations = {} if informations is None else informations
    dfh = pd.DataFrame(history)
    store_result(holdout_key, {
        **dfh.iloc[-1].to_dict(),
        **informations,
        "history_path": hpath,
        "model_path": mpath if save_model else None,
        "predictions_labels_path": plpath,
        "true_labels_path": tlpath
    }, time, results_directory, cache_dir, hyper_parameters, parameters)
    dfh.to_csv(hpath, index=False)
    pd.DataFrame(y_pred).to_csv(plpath, index=False)
    pd.DataFrame(y_test_true).to_csv(tlpath, index=False)
    if save_model:
        model.save(mpath)


def delete_results(results_directory: str):
    """Delete the results stored in a given directory.
        results_directory: str, directory where results are stores.
    """
    if os.path.exists(results_directory):
        shutil.rmtree(results_directory)


def regroup_results(results_directory: str) -> pd.DataFrame:
    """Return regrouped results.
        results_directory: str, directory where to store the results.
    """
    return pd.DataFrame([
        load(path) for path in glob(
            "{results_directory}/results/*.json".format(results_directory=results_directory)
        ) if path.endswith(".json")
    ])
