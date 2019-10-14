# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating a model based on Deep4Cast."""
import argparse
import math
import os
import random
import logging

import numpy as np
import torch

from azureml.core.run import Run

from azureml.automl.core._vendor.automl.client.core.common import logging_utilities
from ..constants import ForecastConstant, TCNForecastParameters
from ..callbacks.run_update import RunUpdateCallback
from ..datasets.timeseries_datasets import TimeSeriesDataset
from ..types import DataInputType
from forecast.callbacks import LRScheduleCallback
from forecast.data.sources.data_source import DataSourceConfig
from forecast.forecaster import Forecaster, ForecastingModel
from forecast.losses import QuantileLoss
from forecast.models.backbone.base import MultilevelType
from forecast.models.canned import create_tcn_quantile_forecaster
from forecast.utils import create_timestamped_dir

from .forecast_wrapper import DNNForecastWrapper, DNNParams


class ForecastTCNWrapper(DNNForecastWrapper):
    """Wrapper for TCN model adapted to work with automl Forecast Training."""

    required_params = [ForecastConstant.Learning_rate, ForecastConstant.Horizon, ForecastConstant.Lookback,
                       ForecastConstant.Batch_size, ForecastConstant.num_epochs, ForecastConstant.Loss,
                       ForecastConstant.Device, ForecastConstant.primary_metric]
    quantiles = [0.1, 0.25, 0.5, 0.75, 0.9]
    loss = QuantileLoss(quantiles)
    default_params = {ForecastConstant.Loss: loss,  # torch.distributions.StudentT,
                      ForecastConstant.Device: 'cuda' if torch.cuda.is_available() else 'cpu'}
    # configure our loss function

    def _init__(self):
        super().__init__()

    def train(self, n_epochs: int, X: DataInputType = None, y: DataInputType = None,
              X_train: DataInputType = None, y_train: DataInputType = None,
              X_valid: DataInputType = None, y_valid: DataInputType = None,
              logger: logging.Logger = None) -> None:
        """
        Start the DNN training.

        :param n_epochs: number of epochs to try.
        :param X: data for training.
        :param y: target data for training.
        :param X_train: training data to use.
        :param y_train: training target to use.
        :param X_valid: validation data to use.
        :param y_valid: validation target to use.
        :param logger: logger.
        """
        settings = self.dataset_settings
        ds = None
        if X_train is not None:
            ds_train = TimeSeriesDataset(X_dflow=X_train,
                                         y_dflow=y_train,
                                         horizon=self.params.get_value(ForecastConstant.Horizon),
                                         step=1,
                                         has_past_regressors=True,
                                         one_hot=False,
                                         train_transform=True,
                                         **settings)
            dset_config = ds_train.dset_config
        else:
            assert X is not None
            assert y is not None
            ds = TimeSeriesDataset(X_dflow=X,
                                   y_dflow=y,
                                   horizon=self.params.get_value(ForecastConstant.Horizon),
                                   step=1,
                                   has_past_regressors=True,
                                   one_hot=False,
                                   train_transform=True,
                                   **settings)
            dset_config = ds.dset_config
        if logger is None:
            logger = logging_utilities.get_logger()
        if self.model is None or self.forecaster is None:
            run_update_callback = self._create_runupdate_callback(X_valid, y_valid, logger)
            self._build_model_forecaster(run_update_callback, dset_config, logger)
        if ds is None:
            ds_train.set_lookback(self.model.receptive_field)
        else:
            ds.set_lookback(self.model.receptive_field)
            ds_train, ds_valid = ds.get_train_test_split()
            run_update_callback.ds_valid = ds_valid
        dataloader_train = self.create_data_loader(ds_train, self.params.get_value(ForecastConstant.Batch_size))

        self.forecaster.fit(
            dataloader_train=dataloader_train,
            loss=self.loss,
            optimizer=self.optimizer,
            epochs=n_epochs)

    def _build_random_canned_model(self, dset_config: DataSourceConfig, horizon: int, num_quantiles: int,
                                   logger: logging.Logger) -> ForecastingModel:
        """
        Build a model based on config.

        :param dset_config:  configuration for the model.
        :param horizon: forecast horizon
        :param num_quantiles: number of quantiles predictions to make.
        :param logger: logger.
        :return: a forecaster model.
        """
        if dset_config.encodings:
            input_channels = dset_config.feature_channels + dset_config.forecast_channels +\
                sum(e.num_vals for e in dset_config.encodings) - len(dset_config.encodings)
        else:
            input_channels = dset_config.feature_channels + dset_config.forecast_channels

        # backbone architecture
        num_cells = self.params.get_value(TCNForecastParameters.NUM_CELLS, random.randint(3, 6))
        multilevel = self.params.get_value(TCNForecastParameters.MULTILEVEL, random.choice(list(MultilevelType)).name)

        # model hyper-parameters
        depth = self.params.get_value(TCNForecastParameters.DEPTH, random.randint(1, 3))
        num_channels = self.params.get_value(TCNForecastParameters.NUM_CHANNELS, random.choice([64, 128, 256]))
        dropout_rate = self.params.get_value(TCNForecastParameters.DROPOUT_RATE,
                                             random.choice([0, 0.1, 0.25, 0.4, 0.5]))
        logger.info('Model used the following hyperparameters: num_cells={}, multilevel={}, depth={}, num_channels={},'
                    ' dropout_rate={}'.format(num_cells, multilevel, depth, num_channels, dropout_rate))

        return create_tcn_quantile_forecaster(input_channels,
                                              num_cells, multilevel,
                                              horizon, num_quantiles,
                                              num_channels, depth, dropout_rate)

    def _create_runupdate_callback(self, X_valid: DataInputType, y_valid: DataInputType,
                                   logger: logging.Logger) -> RunUpdateCallback:
        # get the Azure ML run object
        run_context = Run.get_context()
        return RunUpdateCallback(model_wrapper=self, run_context=run_context, X_valid=X_valid,
                                 y_valid=y_valid, params=self.params, logger=logger)

    def _build_model_forecaster(self, run_update_callback: RunUpdateCallback,
                                dset_config: DataSourceConfig, logger: logging.Logger) -> None:
        self.model = self._build_random_canned_model(dset_config=dset_config,
                                                     horizon=self.params.get_value(ForecastConstant.Horizon),
                                                     num_quantiles=len(self.quantiles), logger=logger)
        chkpt_base = create_timestamped_dir('./chkpts')
        out_dir = create_timestamped_dir(chkpt_base)
        self.model.to_json(os.path.join(out_dir, 'model_arch.json'))

        # Adam with LR decay
        lr = self.params.get_value(ForecastConstant.Learning_rate, 0.001)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.lr_sched = torch.optim.lr_scheduler.ExponentialLR(self.optimizer, 0.98)

        callbacks = [
            run_update_callback,
            LRScheduleCallback(self.lr_sched)
        ]

        # train
        self.forecaster = Forecaster(model=self.model,
                                     device=self.params.get_value(ForecastConstant.Device),
                                     metrics=None,
                                     callbacks=callbacks)

    def predict(self, X: DataInputType, y: DataInputType, n_samples: int = 1) -> np.ndarray:
        """
        Return the predictions for the passed in `X` and `y` values.

        :param X: data values.
        :param y: label for look back and nan for the rest.
        :param n_samples: number of samples to be returned with each prediction.
        :return: numpy ndarray with shape (n_samples, n_rows, horizon).
        """
        ds = self._get_timeseries(X, y)
        return self._predict(ds)

    def _get_timeseries(self, X: DataInputType, y: DataInputType) -> TimeSeriesDataset:
        """
        Get timeseries for given inputs and set_lookback for model.

        :param X: data values
        :param y: label for lookback and nan for rest
        :param n_samples: number of samples to be returned with each prediction.
        :return: Timeseries dataset
        """
        ds = TimeSeriesDataset(X_dflow=X,
                               y_dflow=y,
                               horizon=self.params.get_value(ForecastConstant.Horizon),
                               step=self.params.get_value(ForecastConstant.Horizon),
                               has_past_regressors=True,
                               one_hot=False,
                               pre_transform=self._pre_transform,
                               transform=self._transform)
        ds.set_lookback(self.model.receptive_field)
        return ds

    def _predict(self, ds: TimeSeriesDataset, n_samples: int = 1) -> np.ndarray:
        """
        Return the predictions for the passed timeseries dataset.

        :param ds: TimeSeriesDataset to use for prediction.
        :param n_samples:  number of samples to be returned with each prediction.
        :return: numpy ndarray with shape (n_samples, n_rows, horizon).
        """
        dataloader_test = self.create_data_loader(ds, self.params.get_value(ForecastConstant.Batch_size))

        predictions = np.asarray(self.forecaster.predict(dataloader_test))
        # Currently returning only one prediction: median
        return_predict_index = predictions.shape[0] // 2
        return predictions[return_predict_index:return_predict_index + 1]

    def get_lookback(self):
        """Get lookback used by model."""
        if self.model is not None:
            return self.model.receptive_field
        else:
            return self.params.get_value(ForecastConstant.Lookback)

    @property
    def name(self):
        """Name of the Model."""
        return "ForecastTCN"

    def parse_parameters(self) -> DNNParams:
        """
        Parse parameters from command line.

        return: returns the  DNN  param object from the command line arguments
        """
        parser = argparse.ArgumentParser()

        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.num_epochs), type=int,
                            default=25, help='number of epochs to train')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Lookback), type=int,
                            default=8, help='lookback for model')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Horizon), type=int,
                            default=4, help='horizon for prediction')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Batch_size), type=int,
                            default=8, help='batch_size for training')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.primary_metric), type=str,
                            default='', help='batch_size for training')

        # Model hyper-parameters
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Learning_rate), type=float,
                            default=0.001, help='learning rate')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.NUM_CELLS), type=int,
                            help='num cells')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.MULTILEVEL), type=str,
                            help='multilevel')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.DEPTH), type=int,
                            help='depth')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.NUM_CHANNELS), type=int,
                            help='number of channels')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.DROPOUT_RATE), type=float,
                            help='dropout rate')

        args, unknown = parser.parse_known_args()
        arg_dict = vars(args)
        arg_dict[ForecastConstant.n_layers] = max(int(math.log2(args.lookback)), 1)
        dnn_params = DNNParams(ForecastTCNWrapper.required_params, arg_dict, ForecastTCNWrapper.default_params)
        return dnn_params
