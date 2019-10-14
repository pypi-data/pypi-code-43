# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for starting forecast DNN run with passed in model."""
import argparse
import os
from pathlib import Path
import math
import json
import logging
from typing import Any, Dict, Optional, Tuple

from ....constants import ForecastConstant
from ....wrapper.forecast_wrapper import DNNForecastWrapper, DNNParams
from ....wrapper.deep4cast_wrapper import Deep4CastWrapper
from ....wrapper.forecast_tcn_wrapper import ForecastTCNWrapper
from azureml.automl.core.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from azureml.automl.core._vendor.automl.client.core.common import logging_utilities
from azureml.core import Dataset
from azureml.core.run import Run
from azureml.train.automl._azureautomlruncontext import AzureAutoMLRunContext
import azureml.dataprep as dprep


# Minimum parameter needed to initiate a training
required_params = [ForecastConstant.model, ForecastConstant.output_dir,
                   ForecastConstant.report_interval, ForecastConstant.config_json]
# get the logger default logger as placeholder.
logger = logging_utilities.get_logger()


def get_model(model_name: str) -> DNNForecastWrapper:
    """Return a `DNNForcastWrapper` corresponding to the passed in model_name.

    :param model_name:  name of the model to train
    :return: gets a wrapped model for Automl DNN Training.
    """
    model_dict = {ForecastConstant.Deep4Cast: Deep4CastWrapper(), ForecastConstant.ForecastTCN: ForecastTCNWrapper()}
    return model_dict[model_name]


def run() -> None:
    """Start the DNN training based on the passed in parameters.

    :return:
    """
    # get command-line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.model), type=str,
                        help='model name', default="ForecastTCN")
    parser.add_argument('--output_dir', type=str, help='output directory', default="./outputs")
    parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.num_epochs), type=int,
                        default=25,
                        help='number of epochs to train')
    parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.primary_metric), type=str,
                        default="normalized_root_mean_squared_error", help='primary metric')
    parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.report_interval), type=int,
                        default=1, help='number of epochs to report score')
    parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.config_json), type=str,
                        default=ForecastConstant.config_json_default,
                        help='json representation of dataset and training settings from automl SDK')

    args, unknown = parser.parse_known_args()
    os.makedirs(args.output_dir, exist_ok=True)
    logfile = os.path.join(args.output_dir, ForecastConstant.namespace + '.log')
    Path(logfile).touch()
    logger = logging_utilities.get_logger(ForecastConstant.namespace, logfile)
    args_dict = vars(args)
    params = DNNParams(required_params, args_dict, None)

    logger.info("Arguments passed to driver script: {0}".format((args_dict)))
    logger.info("DNN parameters {0}".format(str(params)))
    model = get_model(params.get_value(ForecastConstant.model))

    data, settings = get_parameters_from_settings(params.get_value(ForecastConstant.config_json), logger)
    logger.info("Run settings passed to driver script: {}".format(settings))
    model.init_model(settings)
    data_settings = settings.get(ForecastConstant.dataset_settings, {})
    X, y, X_train, y_train, X_valid, y_valid = _get_training_data(data, data_settings)
    num_epochs = params.get_value(ForecastConstant.num_epochs)

    run_context = Run.get_context()
    automl_run_context = AzureAutoMLRunContext(run_context)

    logging_utilities.log_system_info(logger, prefix_message="[RunId:{}]".format(automl_run_context.run_id))

    telemetry_logger = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(logger, interval=10)

    send_telemetry = settings.get('send_telemetry', True)

    telemetry_logger.send_usage_telemetry_log(
        prefix_message="[RunId:{}][Starting DNN Training]".format(automl_run_context.run_id),
        is_sending_telemetry=send_telemetry
    )

    logging_utilities.log_system_info(logger, prefix_message="[RunId:{}]".format(automl_run_context.run_id))

    telemetry_logger.send_usage_telemetry_log(
        prefix_message="[RunId:{}][Before DNN Train]".format(automl_run_context.run_id),
        is_sending_telemetry=send_telemetry
    )

    model.train(num_epochs, X=X, y=y, X_train=X_train, y_train=y_train,
                X_valid=X_valid, y_valid=y_valid, logger=logger)

    telemetry_logger.send_usage_telemetry_log(
        prefix_message="[RunId:{}][After DNN Train completed]".format(automl_run_context.run_id),
        is_sending_telemetry=send_telemetry
    )


def _get_training_data(data: dict, data_settings: dict) -> Tuple[Any, Any, Any, Any]:
    """Get the training data the form of tuples from dictionary.

    :param data: Dictionary of dataflow objects.
    :param data_settings: Data settings for dataflow objects.
    :return: A tuple with train and validation data.
    """
    X, y, X_train, y_train, X_valid, y_valid = None, None, None, None, None, None
    if "X_train" in data:
        X_train, y_train = data["X_train"], data["y_train"]
    if "X_valid" in data:
        X_valid, y_valid = data["X_valid"], data["y_valid"]
    if "X" in data:
        X, y = data["X"], data["y"]

    if "training_data" in data and 'label_column_name' in data_settings:
        target_column = data_settings['label_column_name']
        if "validation_data" in data:
            X_train, y_train, _ = _extract_data_from_combined_dataflow(data['training_data'], target_column, None)
            X_valid, y_valid, _ = _extract_data_from_combined_dataflow(data['validation_data'], target_column, None)
        else:
            X, y, _ = _extract_data_from_combined_dataflow(data['training_data'], target_column, None)

    return X, y, X_train, y_train, X_valid, y_valid


def _extract_data_from_combined_dataflow(
        input: dprep.Dataflow,
        label_column_name: str,
        sample_weight_column_name: Optional[str]) -> Tuple[Any, Any, Any]:
    """
    Extract user data from a Dataflow if it contains both training features & labels.

    :param input: The Dataflow to extract X, y, sample_valid from.
    :return: A Dictionary with keys being X, y, sample_weight containing the extracted training data.
    """
    col_names_to_drop = [label_column_name]
    sample_weight = None
    if sample_weight_column_name is not None:
        col_names_to_drop.append(sample_weight_column_name)
        sample_weight = input.keep_columns([sample_weight_column_name])
    X = input.drop_columns(col_names_to_drop)
    y = input.keep_columns([label_column_name])
    return (X, y, sample_weight)


def get_parameters_from_settings(file_name: str, logger: logging.Logger) -> tuple:
    """Create dprep dataset dict and training setting dict.

    :param file_name: file containing the dataset dprep and other training parameters such as
                      lookback, horizon and time column name.
    :return:
    """
    params = json.load(open(file_name, encoding='utf-8-sig'))
    dataset_dict = json.loads(params['datasets.json'])
    clean_settings = clean_general_settings_json_parse(params['general.json'])
    general_setting_dict = json.loads(clean_settings)
    settings = get_parameters_from_general_settings(general_setting_dict)
    dataset = get_dataprep_datasets(dataset_dict, logger)
    return dataset, settings


def clean_general_settings_json_parse(orig_string: str) -> str:
    """Convert word/char into JSON parse form.

    :param orig_string: the original string to convert.
    :return:
    """
    ret_string = orig_string
    replace = {"None": "null", "True": "true", "False": "false", "'": "\""}
    for item in replace:
        ret_string = ret_string.replace(item, replace[item])
    return ret_string


def get_parameters_from_general_settings(general_setting_dict: dict) -> dict:
    """Collect parameter for training from setting.

    :param general_setting_dict: dictionary of parameters from automl settings.
    :return:
    """
    settings = {}
    if ForecastConstant.Horizon in general_setting_dict:
        settings[ForecastConstant.Horizon] = int(general_setting_dict[ForecastConstant.Horizon])
    if ForecastConstant.Lookback in general_setting_dict:
        settings[ForecastConstant.Lookback] = int(general_setting_dict[ForecastConstant.Lookback])
        settings[ForecastConstant.n_layers] = max(int(math.log2(settings[ForecastConstant.Lookback])), 1)
    if ForecastConstant.primary_metric in general_setting_dict:
        settings[ForecastConstant.primary_metric] = general_setting_dict.get(ForecastConstant.primary_metric,
                                                                             ForecastConstant.default_primary_metric)
    dataset_settings = {}
    for setting_name in ForecastConstant.FORECAST_VALID_SETTINGS:
        if setting_name in general_setting_dict:
            dataset_settings[setting_name] = general_setting_dict[setting_name]
    settings[ForecastConstant.dataset_settings] = dataset_settings
    return settings


def _get_data_from_dataset_options(self, dataprep_json_obj: Dict[str, Any],
                                   logger: logging.Logger) -> Dict[str, Any]:
    logger.info('Creating dataflow from dataset.')
    dataset_id = dataprep_json_obj['datasetId']  # mandatory
    label_column = dataprep_json_obj['label']  # mandatory
    feature_columns = dataprep_json_obj.get('features', [])

    ws = self.run_context.experiment.workspace
    dataset = Dataset.get(ws, id=dataset_id)
    dflow = dataset.definition
    return self._get_dict_from_dataflow(dflow, logger, feature_columns, label_column)


def get_dataprep_datasets(dataset_dict, logger) -> dict:
    """Create dataprep object from respective JSON form of dataset.

    :param dataset_dict: dictionary of dataset in JSON format
    :return:
    """
    keys_to_convert = ['X', 'y', 'X_train', 'y_train', 'X_valid', 'y_valid', 'training_data', 'validation_data']
    dataset = {}
    # Coming from UI create dataflow from dataset.
    if "datasetId" in dataset_dict:
        dataset = _get_data_from_dataset_options(dataset_dict, logger)
    else:
        for key in dataset_dict.keys():
            if key in keys_to_convert:
                dataset[key] = dprep.Dataflow.from_json(dataset_dict[key])
    return dataset
