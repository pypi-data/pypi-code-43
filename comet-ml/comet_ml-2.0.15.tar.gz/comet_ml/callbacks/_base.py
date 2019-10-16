# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without
#  the express permission of Comet ML Inc.
# *******************************************************

import logging

import six

from ..utils import get_time_monotonic

LOGGER = logging.getLogger(__name__)


def build_base_callback(base):
    class BaseCallback(base):
        """
        Base Keras callback.
        """

        def __init__(self):
            super(BaseCallback, self).__init__()

        def on_epoch_begin(self, epoch, logs=None):
            pass

        def on_epoch_end(self, epoch, logs=None):
            pass

        def on_batch_begin(self, batch, logs=None):
            pass

        def on_batch_end(self, batch, logs=None):
            pass

        def on_train_begin(self, logs=None):
            pass

        def on_train_end(self, logs=None):
            pass

        def on_train_batch_begin(self, batch, logs=None):
            pass

        def on_train_batch_end(self, batch, logs=None):
            pass

        def on_test_batch_begin(self, batch, logs=None):
            pass

        def on_test_batch_end(self, batch, logs=None):
            pass

        def on_test_begin(self, logs=None):
            pass

        def on_test_end(self, logs=None):
            pass

        def on_predict_begin(self, logs=None):
            pass

        def on_predict_end(self, logs=None):
            pass

        def on_predict_batch_begin(self, batch, logs=None):
            pass

        def on_predict_batch_end(self, batch, logs=None):
            pass

    return BaseCallback


def build_predictive_early_stopping_keras_callback(base):
    class PredictiveEarlyStoppingKerasCallback(base):
        def __init__(self, predictor, predict_epoch_rate=1):
            super(PredictiveEarlyStoppingKerasCallback, self).__init__()
            self.predictor = predictor
            self.predict_epoch_rate = predict_epoch_rate

        def on_epoch_end(self, epoch, logs={}):
            if epoch % self.predict_epoch_rate == 0:
                loss = logs.get(self.predictor.loss_name)
                self.predictor.report_loss(loss)

                if self.predictor.stop_early(epoch=epoch):
                    self.model.stop_training = True

    return PredictiveEarlyStoppingKerasCallback


def build_empty_keras_callback(base):
    class EmptyKerasCallback(base):
        """
        Empty Keras callback.
        """

    return EmptyKerasCallback


def build_keras_callback(base):
    class KerasCallback(base):
        """ Keras callback to report params, metrics to Comet.ml Experiment()"""

        def __init__(
            self, experiment, log_params=True, log_metrics=True, log_graph=True
        ):
            """
            Create a new experiment and submit source code.
            :param api_key: User's API key. Required.
            """
            super(KerasCallback, self).__init__()

            # Inits the experiment with reference to the name of this class. Required for loading the correct
            # script file
            self.experiment = experiment
            self.log_params = log_params
            self.log_metrics = log_metrics
            self.log_graph = log_graph
            self.epoch_start_time = None
            self.our_step = 0
            self._ignores = ["verbose", "do_validation", "validation_steps"]

        def on_epoch_begin(self, epoch, logs=None):
            # This function should only be called during train mode.
            LOGGER.debug("On epoch begin %s %s", epoch, logs)
            self.experiment.set_epoch(epoch)
            self.epoch_start_time = get_time_monotonic()

        def on_epoch_end(self, epoch, logs=None):
            # This function should only be called during train mode.
            LOGGER.debug("On epoch end %s %s", epoch, logs)
            if self.log_metrics:
                if self.epoch_start_time is not None:
                    self.experiment.log_metric(
                        "epoch_duration",
                        get_time_monotonic() - self.epoch_start_time,
                        step=self.our_step,
                    )
                    self.epoch_start_time = None
                self.experiment.log_epoch_end(epoch, step=self.our_step)
                if logs:
                    for name, val in logs.items():
                        self.experiment.log_metric(name, val, step=self.our_step)

        def on_batch_begin(self, batch, logs=None):
            # This function called directly when in train mode.
            LOGGER.debug("On batch begin %s %s", batch, logs)

        def on_batch_end(self, batch, logs=None):
            """
            Logs training metrics.
            """
            # This function called directly when in train mode.
            LOGGER.debug("On batch end %s %s", batch, logs)

            self.our_step += 1

            if self.experiment.batch_report_rate > 0:
                if batch is not None and isinstance(batch, six.integer_types):
                    if batch % self.experiment.batch_report_rate == 0:
                        self._send_batch_messages(logs)
                else:
                    self._send_batch_messages(logs)

        def on_train_batch_end(self, batch, logs=None):
            # No context added here, to match previous behavior:
            self.on_batch_end(batch, logs)

        def on_test_batch_end(self, batch, logs=None):
            with self.experiment.validate():
                self.on_batch_end(batch, logs)

        def _send_batch_messages(self, logs):
            if logs and self.log_metrics:
                for name, val in logs.items():
                    if name in ["size", "batch"]:
                        ## these don't change
                        continue
                    self.experiment.log_metric("batch_" + name, val, step=self.our_step)

        def on_train_begin(self, logs=None):
            """
            Sets model graph.
            """
            LOGGER.debug("On train begin %s", logs)

            if self.log_graph:
                self.experiment.set_model_graph(
                    get_keras_json_model(self.experiment, self.model)
                )
            self.experiment.log_other("trainable_params", self.model.count_params())

            if self.log_params:
                if logs:
                    for k, v in logs.items():
                        self.experiment.log_parameter(k, v)

                # Keras Callback doesn't set this parameter at creation by default
                if hasattr(self, "params") and self.params:
                    for k, v in self.params.items():
                        if k != "metrics" and k not in self._ignores:
                            self.experiment.log_parameter(k, v)

                try:
                    optimizer_name = self.model.optimizer.__class__.__name__
                    self.experiment.log_parameters(
                        self.model.optimizer.get_config(), prefix=optimizer_name
                    )
                except Exception:
                    LOGGER.debug(
                        "Failed to extract optimizer information", exc_info=True
                    )

        def on_train_end(self, *args, **kwargs):
            LOGGER.debug("On train end %r", locals())

    return KerasCallback


def get_keras_json_model(experiment, model):
    # With multi-gpu models we save the original model in the experiment
    # storage
    storage_key = "gpu_model_%s" % id(model)
    json_model = experiment._storage["keras"].get(storage_key, None)

    if json_model is not None:
        return json_model
    else:
        try:
            return model.to_json()
        except Exception:
            experiment._log_once_at_level(
                logging.WARNING, "Failed to save keras graph model", exc_info=True
            )
