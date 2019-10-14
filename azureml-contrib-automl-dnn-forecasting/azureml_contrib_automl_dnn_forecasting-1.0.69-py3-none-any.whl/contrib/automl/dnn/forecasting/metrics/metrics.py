# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for calculating metrices for forecast dnn training."""
import numpy as np
from typing import Dict, Any, Union

from azureml.automl.core._vendor.automl.client.core.common import constants
try:
    from azureml.automl.core._vendor.automl.client.core.runtime import metrics as classical_metrics
    from azureml.automl.core._vendor.automl.client.core.runtime.datasets import ClientDatasets
except ImportError:
    from azureml.automl.core._vendor.automl.client.core.common import metrics as classical_metrics
    from azureml.automl.core._vendor.automl.client.core.common.datasets import ClientDatasets

from azureml.automl.core.fit_pipeline import _log_metrics as log_metrics
from ..datasets.timeseries_datasets import TimeSeriesDataset
import Deep4Cast.deep4cast.metrics as forecast_metrics
from forecast.data import FUTURE_DEP_KEY


def compute_metric(y_pred, y_true_forecast, horizon, scalar_only=True) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute the classic and time series metric for the training.

    :param y_pred: forecasted target values.
    :param y_true_forecast: actual target values.
    :param horizon: horizon used for predictions.
    :param scalar_only: whether to compute scalar metrices only.
    :return: scores dictionary.
    """
    y_true_classical = y_true_forecast.reshape(-1)
    y_pred_classical = y_pred.reshape(-1)
    bin_info = None
    metrics_to_compute = constants.Metric.SCALAR_REGRESSION_SET
    if not scalar_only:
        dataset = ClientDatasets()
        bin_info = dataset.make_bin_info(y_true_classical.shape[0], y_true_classical)
        metrics_to_compute = constants.Metric.REGRESSION_SET

    scores = classical_metrics.compute_metrics(y_pred_classical, y_true_classical,
                                               task=constants.Tasks.REGRESSION,
                                               metrics=metrics_to_compute,
                                               bin_info=bin_info)

    # reshape prediction
    # Number of samples predicted per item based on the distribution
    number_of_samples_per_prediction = y_pred.shape[0]
    # Number of forecasting series to predict.
    number_of_items_to_predict = y_true_forecast.shape[0]
    # Number of target variables, we only support one dimensional y.
    number_of_target_variables = 1
    time_steps = horizon
    y_pred = y_pred.reshape(number_of_samples_per_prediction,
                            number_of_items_to_predict,
                            number_of_target_variables,
                            time_steps)
    scores[constants.Metric.ForecastMAPE] = forecast_metrics.mape(y_pred, y_true_forecast).mean()
    return scores


def get_target_values(X_test, y_test, model, horizon, ds_test=None):
    """Get target y values in dataloader indexed order."""
    if ds_test is None:
        ds_test = TimeSeriesDataset(X_dflow=X_test,
                                    y_dflow=y_test,
                                    horizon=horizon,
                                    step=horizon,
                                    has_past_regressors=True,
                                    pre_transform=None,
                                    transform=None,
                                    train_transform=False,
                                    fetch_y_only=True)
        # TODO make it generic for all models
        ds_test.set_lookback(model.model.receptive_field)
    y_true_forecast = []
    for i in range(len(ds_test)):
        sample = ds_test[i]
        if ds_test.has_past_regressors:
            y_true_forecast.append(sample[FUTURE_DEP_KEY].numpy())
        else:
            y_true_forecast.append(sample["y"].numpy())
    y_true_forecast = np.asarray(y_true_forecast)
    return y_true_forecast


def _undo_transform(model, sample):
    sample = model._transform.undo(sample)
    return sample


def save_metric(run, scores, logger):
    """
    Save the metrics into the run history/artifact store.

    :param run: azureml run context
    :param scores: dictionary of score name and values.
    :param logger: Logger to use.
    :return: None
    """
    log_metrics(run, scores, logger)
