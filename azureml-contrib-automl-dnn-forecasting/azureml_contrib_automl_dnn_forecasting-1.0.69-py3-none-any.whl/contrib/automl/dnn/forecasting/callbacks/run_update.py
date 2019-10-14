# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Callbacks which computes and uploads metric to run."""
import logging
import os
from typing import Union, Any, List, Dict
import pkg_resources

import json
import pandas as pd
import numpy as np

from ..constants import ForecastConstant
from ..wrapper.forecast_wrapper import DNNForecastWrapper, DNNParams
from ..metrics.metrics import compute_metric, get_target_values, save_metric
from azureml.automl.core import inference, package_utilities
from azureml.automl.core.data_transformation import _get_data_snapshot
from azureml.automl.core.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from azureml.core.run import Run
import azureml.dataprep as dprep
from azureml.train.automl._azureautomlruncontext import AzureAutoMLRunContext
from forecast.callbacks import Callback


class RunUpdateCallback(Callback):
    """Wraps AutoML metric computation and upload in a callback."""

    def __init__(self,
                 model_wrapper: DNNForecastWrapper,
                 run_context: Run,
                 X_valid: Union[pd.DataFrame, dprep.Dataflow],
                 y_valid: Union[pd.DataFrame, dprep.Dataflow],
                 params: DNNParams,
                 logger: logging.Logger = None):
        """Initialize callback to compute and upload metric to the run context.

        :param model_wrapper: DNNForecastWrapper Model that is being trained
        :param run_context:AutoML run context to be used for uploading model/metrices
        :param X_valid: X validation data used for computing metrices
        :param y_valid: y validation data used for computing metrices
        :param params: DNNParams
        :param logger: Logger
        """
        super().__init__()
        self.model_wrapper = model_wrapper
        self.run_context = run_context
        self.X_valid = X_valid
        self.y_valid = y_valid
        self.ds_valid = None
        self.params = params
        self.logger = logger
        self._scores = None

        self.telemetry_logger = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(logger, interval=10)
        self.automl_run_context = AzureAutoMLRunContext(self.run_context)
        # Add properties required for automl UI.
        run_properties_for_ui = {"runTemplate": "automl_child",
                                 "run_preprocessor": "",
                                 "run_algorithm": self.model_wrapper.name,
                                 ForecastConstant.primary_metric: params.get_value(ForecastConstant.primary_metric)}
        self.run_context.add_properties(run_properties_for_ui)

        self.report_interval = params.get_value(ForecastConstant.report_interval)
        self.num_epochs = params.get_value(ForecastConstant.num_epochs)
        self.num_epochs_done = 0

    def on_train_epoch_end(self, epoch, loss, metrics) -> None:
        """On each train epoch end set to compute metric and upload.

        :param epoch: Current epoch number
        :param loss: current loss
        :param metrics: metrics already computed
        """
        # TODO move this to different Telemetry callback
        self.telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][After DNN Train epoch {} completed]".format(
                self.automl_run_context.run_id, epoch),
            is_sending_telemetry=True
        )
        if self._is_validation_data_available():
            if self.ds_valid is None:
                self.ds_valid = self.model_wrapper._get_timeseries(self.X_valid, self.y_valid)
            # else:
            # validation data is already transformed and cached, so no need to transform it again
            # self.ds_valid.transform = None
            y_pred = self.model_wrapper._predict(self.ds_valid)
            horizon = self.model_wrapper.params.get_value(ForecastConstant.Horizon)
            assert horizon == y_pred.shape[-1], "h={0} y={1}".format(horizon, y_pred.shape)
            y_test = get_target_values(self.X_valid, self.y_valid, self.model_wrapper, horizon, self.ds_valid)

            scores = compute_metric(y_pred=y_pred, y_true_forecast=y_test, horizon=horizon, scalar_only=True)
            score = self._get_primary_metric_score(scores)
            self.logger.info("Scores: '{0}'".format(scores))
            primary_metric = self.params.get_value(ForecastConstant.primary_metric)
            self.run_context.log(primary_metric, np.float(score))
            save_metric(self.run_context, scores, self.logger)

        if epoch == self.num_epochs - 1:  # epochs start at 0
            if self._is_validation_data_available():
                self.upload_properties_tabular_metrics(y_pred=y_pred, y_test=y_test)
            self.upload_model()

    def _is_validation_data_available(self):
        return self.ds_valid is not None or (self.X_valid is not None and self.y_valid is not None)

    def _get_primary_metric_score(self, scores) -> float:
        score = float('nan')
        primary_metric = self.params.get_value(ForecastConstant.primary_metric)
        if primary_metric in scores:
            score = scores[primary_metric]
        else:
            self.logger.warning("Primary metric '{0}' is missing from the scores".format(primary_metric))
        return score

    def upload_properties_tabular_metrics(self, y_pred, y_test, ) -> None:
        """On train end set to upload tabular metrics.

        :param y_pred: predicted target values
        :param y_test: actual target values
        """
        # upload tabular metrics
        horizon = self.model_wrapper.params.get_value(ForecastConstant.Horizon)
        scores = compute_metric(y_pred=y_pred, y_true_forecast=y_test, horizon=horizon, scalar_only=False)
        save_metric(self.run_context, scores, self.logger)

        # Add the score that is mandatory for the ui to show the run in UI
        score = self._get_primary_metric_score(scores)
        self.run_context.add_properties({"score": float(score)})

    def upload_model(self) -> None:
        """Upload dnn model to run context."""
        model_id = self._get_model_id(self.run_context.id)
        self._save_model_for_automl_inference(model_id, self.model_wrapper, self.logger)

    # this code has to be refactored in automl sdk where it can take the model and context and save
    # all inferencing related data
    def _save_model_for_automl_inference(self, model_id: str,
                                         model: DNNForecastWrapper, logger: logging.Logger):
        """Save model and runproperties needed for inference.

        :param model_id: the unique id for identifying the model with in the workspace.
        :param model: model to save in artifact.
        :param logger: logger to report all messages.
        :return:
        """
        all_dependencies = package_utilities._all_dependencies()
        strs_to_save = {}

        # save versions to artifacts
        strs_to_save[ForecastConstant.automl_constants.DEPENDENCIES_PATH] = json.dumps(all_dependencies, indent=4)

        # save conda environment file into artifacts
        try:
            strs_to_save[ForecastConstant.automl_constants.CONDA_ENV_FILE_PATH] = self._create_conda_env_file_content()
        except Exception as e:
            logger.warning("Failed to create conda environment file. Error seen is: " + str(e))

        # generate sample data for scoring file, by looking at first row fom validation data
        try:
            sample_str = _get_data_snapshot(self.X_valid, is_forecasting=True)
        except Exception as e:
            logger.warning("Failed to create score inference file. Error : " + str(e))
            sample_str = "None"

        # save scoring file into artifacts
        try:
            scoring_file_str = self._get_scoring_file(model_id, sample_str)
            strs_to_save[ForecastConstant.automl_constants.SCORING_FILE_PATH] = scoring_file_str
        except Exception as e:
            logger.warning("Failed to create score inference file. Error : " + str(e))

        # Upload files to artifact store
        models_to_upload = {ForecastConstant.automl_constants.MODEL_PATH: model}
        self.automl_run_context.batch_save_artifacts(strs_to_save, models_to_upload)

        # save artifact ids as properties
        properties_to_add = {inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation:
                             self.automl_run_context._get_artifact_id(
                                 ForecastConstant.automl_constants.CONDA_ENV_FILE_PATH),
                             inference.AutoMLInferenceArtifactIDs.ModelDataLocation:
                             self.automl_run_context._get_artifact_id(ForecastConstant.automl_constants.MODEL_PATH)}

        properties_to_add.update({inference.AutoMLInferenceArtifactIDs.ScoringDataLocation:
                                  self.automl_run_context._get_artifact_id(
                                      ForecastConstant.automl_constants.SCORING_FILE_PATH),
                                  inference.AutoMLInferenceArtifactIDs.ModelName: model_id})

        # automl code saves the graph json for the pipeline. Todo add code to save the model graph.

        self.automl_run_context._run.add_properties(properties_to_add)

    def _get_model_id(self, runid: str):
        """Generate a model name from runid.

        :param runid:  runid string of the hyperdrive child run.
        :return: the id produced by taking run number and last 12 chars from hyperdrive runid.
        """
        name = 'DNN'
        parent_num_part = ''
        child_num = ''
        if runid:
            parts = runid.split("_")
            if len(parts) > 0:
                child_num = parts[-1]
            if len(parts) > 1:
                parent_num_part = parts[-2][-12:]

        return name + parent_num_part + child_num

    def _get_scoring_file(self, model_id: str, input_sample_str: str = "pd.DataFrame()") -> str:
        """
        Return scoring file to be used at the inference time.

        If there are any changes to the scoring file, the version of the scoring file should
        be updated in the vendor.

        :return: Scoring python file as a string
        """
        scoring_file_path = pkg_resources.resource_filename(
            inference.inference.PACKAGE_NAME, os.path.join('inference', 'score_forecasting.txt'))

        inference_data_type = inference.inference.PandasParameterType

        with open(scoring_file_path, 'r') as scoring_file_ptr:
            content = scoring_file_ptr.read()
            content = content.replace('<<ParameterType>>', inference_data_type)
            content = content.replace('<<input_sample>>', input_sample_str)
            content = content.replace('<<modelid>>', model_id)

        return content

    def _create_conda_env_file_content(self):
        """
        Return conda/pip dependencies for the current AutoML run.

        If there are any changes to the conda environment file, the version of the conda environment
        file should be updated in the vendor.

        :return: Conda dependencies as string
        """
        from azureml.core.conda_dependencies import CondaDependencies
        sdk_dependencies = package_utilities._all_dependencies()
        pip_package_list_with_version = []
        for pip_package in inference.AutoMLPipPackagesList:
            if 'azureml' in pip_package:
                if pip_package in sdk_dependencies:
                    pip_package_list_with_version.append(pip_package + "==" + sdk_dependencies[pip_package])
            else:
                pip_package_list_with_version.append(pip_package)
        AutoMLCondaPackagesList = inference.AutoMLCondaPackagesList
        AutoMLCondaPackagesList.append("pytorch>=1.2")
        pip_package_list_with_version.extend(self._get_dnn_dependencies())

        myenv = CondaDependencies.create(conda_packages=AutoMLCondaPackagesList,
                                         pip_packages=pip_package_list_with_version,
                                         python_version='3.7',
                                         pin_sdk_version=False)
        myenv.add_channel("pytorch")
        return myenv.serialize_to_string()

    def _get_dnn_dependencies(self):
        """Get the dependencies for the package for inferencing."""
        dp = "https://forecastdnnpips.blob.core.windows.net/dist/" \
             + "azureml_automl_dnn_forecasting-0.1.0.0-py3-none-any.whl"
        return ["future>=0.17.1",
                "GitPython>=2.1.11",
                "numpy>=1.16.2",
                "pandas>=0.23.4",
                "tensorboard>=1.14.0",
                "torch>=1.2.0",
                "tqdm>=4.32.1",
                dp]

    def _get_dict_from_dataflow(self, dflow: Any,
                                logger: logging.Logger,
                                feature_columns: List[str],
                                label_column: str) -> Dict[str, Any]:
        fit_iteration_parameters_dict = {}  # type: Dict[str, Any]
        if len(feature_columns) == 0:
            X = dflow.drop_columns(label_column)
        else:
            X = dflow.keep_columns(feature_columns)

        X = self._get_inferred_types_dataflow(X, logger)
        y = dflow.keep_columns(label_column)
        y = y.to_number(label_column)
        logger.info('X: {}'.format(X))
        logger.info('y: {}'.format(y))

        fit_iteration_parameters_dict = {
            "X": X,
            "y": y,
            "sample_weight": None,
            "X_valid": None,
            "y_valid": None,
            "sample_weight_valid": None,
            "X_test": None,
            "y_test": None,
            "cv_splits_indices": None,
        }
        return fit_iteration_parameters_dict

    def _get_inferred_types_dataflow(self, dflow: dprep.Dataflow,
                                     logger: logging.Logger) -> dprep.Dataflow:
        logger.info('Inferring type for feature columns.')
        set_column_type_dflow = dflow.builders.set_column_types()
        set_column_type_dflow.learn()
        set_column_type_dflow.ambiguous_date_conversions_drop()
        return set_column_type_dflow.to_dataflow()
