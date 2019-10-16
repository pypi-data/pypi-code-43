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
import time

from .api import API
from .config import get_config
from .connection import get_http_session

LOGGER = logging.getLogger(__name__)


class Predictor(object):
    """
    Please email lcp-beta@comet.ml for comments or questions.
    """

    def __init__(
        self,
        experiment,
        loss_name="loss",
        patience=10,
        best_callback=None,
        threshold=0.1,
        api=None,
        optimizer_id=None,
        interval=2,
        start=5,
        mode="local",
        **defaults
    ):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.config = get_config()
        self.experiment = experiment

        self.allowed_modes = ["global", "local"]
        if mode in self.allowed_modes:
            self.mode = mode

        else:
            msg = "{} mode not supported. Please set mode to global or local"
            raise ValueError(msg.format(mode))

        self.loss_name = loss_name
        self.patience = patience
        self.best_callback = best_callback
        self.step = None
        self.done = None
        self.wait = 0
        self.loss = []
        self.defaults = {
            "experiment_key": self.experiment.id,
            "api_key": self.experiment.api_key,
            "TS": self.loss,  # Reference!
            "HP_samples": float("nan"),
            "AP_no_parameters": float("nan"),
            "HP_epochs": float("nan"),
            "HP_learning_rate": float("nan"),
            "HP_batch_size": float("nan"),
        }
        self.set_defaults(**defaults)
        self.threshold = threshold
        if not 0.0 < self.threshold <= 1.0:
            raise ValueError("Threshold must be set between 0.0 and 1.0")

        self.interval = interval
        # If interval is set to 0
        if not self.interval >= 1:
            raise ValueError("Please set interval to at least 1")

        self.base_url = self.config["comet.predictor_url"]
        self.status_url = "{}lc_predictor/status/".format(self.base_url)
        self.predict_url = "{}lc_predictor/predict/".format(self.base_url)
        self._session = get_http_session()
        status = self.status()
        self.experiment.log_other("predictor_loss_name", self.loss_name)
        self.experiment.log_other("predictor_id", status["model_id"])

        self.MAX_TRIES = 5  # TODO: how many get_optimizer_best() retries are needed

        self.latest_prediction = {
            "min": None,
            "mean": None,
            "max": None,
            "probability_of_improvement": None,
        }

        if self.mode == "global":
            # Check if optimizer_id is set
            if self.experiment.optimizer is None:
                if optimizer_id is None:
                    raise ValueError(
                        "Please set an optimizer id to use the Predictor in global mode"
                    )
                else:
                    self.optimizer_id = optimizer_id
                    self.experiment.log_other("optimizer_id", self.optimizer_id)

            else:
                self.optimizer_id = self.experiment.optimizer["optimizer"].id

            # Specifies the number of experiment to include in the sample period
            self.start = start

            self.api = api if api else API()

        else:
            LOGGER.warning("Predictor Local Mode is still experimental.")

    def reset(self):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.step = None
        self.wait = 0
        self.loss[:] = []  # Reference!

    def set_defaults(self, **defaults):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        self.defaults.update(defaults)

    def status(self):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        try:
            response = self._session.get(self.status_url)
        except Exception:
            LOGGER.debug("Error getting the status", exc_info=True)
            pass
        else:
            if response.status_code == 200:
                response_data = response.json()
                return response_data
            else:
                LOGGER.debug("Invalid status code %d", response.status_code)
        return None

    def report_loss(self, loss, step=None):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        try:
            loss = float(loss)
        except Exception:
            raise ValueError("Predictor.report_loss() requires a single number")

        self.step = step if step is not None else self.experiment.curr_step
        self.loss.append(loss)
        self.experiment.log_metric("predictor_tracked_loss", loss, step=self.step)

    def _local_stop_early(self, **data):
        if self.done is not None:
            (lower, mean, upper, p_improvement) = self.done

            # If done is not None keep logging the last predicted value
            self.experiment.log_metrics(
                {
                    "predictor_mean": mean,
                    "predictor_upper": upper,
                    "predictor_lower": lower,
                    "predictor_p_improvement": p_improvement,
                    "predictor_threshold": self.threshold,
                    "predictor_patience": self.patience,
                    "predictor_wait": self.wait,
                },
                step=self.step,
            )
            return True

        if len(self.loss) < 10:
            return False

        # After 10 epochs of data, evaluate curve every N intervals
        if (len(self.loss) - 10) % self.interval == 0:
            current_loss = self.loss[-1]
            lowest_min = min(self.loss[:-1])

            current_best = min(lowest_min, current_loss)

            data.update({"best_metric": current_best})
            lmup = self.get_prediction(**data)

            if lmup is None:
                return False

            (lower, mean, upper, p_improvement) = lmup
            self.experiment.log_metrics(
                {
                    "predictor_mean": mean,
                    "predictor_upper": upper,
                    "predictor_lower": lower,
                    "predictor_p_improvement": p_improvement,
                    "predictor_threshold": self.threshold,
                    "predictor_patience": self.patience,
                    "predictor_wait": self.wait,
                },
                step=self.step,
            )

            # If the loss is improving, reset the wait count
            # Every time we see an improvement, run the callback
            if current_loss < lowest_min:
                self.wait = 0

                if callable(self.best_callback):
                    self.best_callback(self, current_loss)

            # Else increment the wait count
            else:
                self.wait += 1

            # If probability of improvement is less than the threshold
            # Increment patience count
            if p_improvement <= self.threshold:
                self.experiment.log_other(
                    "predictor_stop_step", self.experiment.curr_step
                )
                self.experiment.log_other("predictor_stop_reason", "threshold crossed")
                self.done = (lower, mean, upper, p_improvement)

                return True

            # If patience is exceeded, stop training
            if self.wait >= self.patience:
                self.experiment.log_other(
                    "predictor_stop_step", self.experiment.curr_step
                )
                self.experiment.log_other("predictor_stop_reason", "patience exceeded")
                self.done = (lower, mean, upper, p_improvement)

                return True

        return False

    def _global_stop_early(self, **data):
        # For cases where model is not stopped after _global_stop_early returns True
        if self.wait >= self.patience:
            LOGGER.debug("Patience Exceeded: %s >= %s", self.wait, self.patience)
            return True

        if len(self.loss) < 10:
            return False

        # After 10 epochs of data, evaluate curve every N intervals
        if (len(self.loss) - 10) % self.interval == 0:
            state = self._get_trial_state(**data)

            if state is None:
                return False

            experiment_count = state.get("experiment_count")
            best_metric = state.get("best_metric")

            lower = state.get("lower")
            mean = state.get("mean")
            upper = state.get("upper")

            p_improvement = state.get("prob_improvement")
            self.experiment.log_metrics(
                {
                    "predictor_mean": mean,
                    "predictor_max": upper,
                    "predictor_min": lower,
                    "predictor_threshold": self.threshold,
                    "predictor_patience": self.patience,
                    "predictor_wait": self.wait,
                    "predictor_p_improvement": p_improvement,
                }
            )

            # TODO: Move block into its own function
            if experiment_count > self.start:
                if p_improvement <= self.threshold:
                    self.wait += 1

                    if self.wait >= self.patience:
                        self.experiment.log_other(
                            "predictor_stop_step", self.experiment.curr_step
                        )
                        msg = (
                            "Predicted value {} for metric: {} is higher than the"
                            " best value {} seen in this trial"
                        )
                        self.experiment.log_other(
                            "predictor_stop_reason",
                            msg.format(
                                mean, self.loss_name, best_metric, self.threshold
                            ),
                        )
                        self.done = (lower, mean, upper, p_improvement)

                        return True

        return False

    def _get_trial_state(self, **data):
        """
        Internal method only used in global mode to retrieve best metric
        in an optimizer run
        :param data:
        :return:
        """
        count = 0
        while count < self.MAX_TRIES:
            try:
                LOGGER.debug("calling get_optimizer_best()...")
                response_data = self.api.get_optimizer_best(
                    self.experiment.id, self.optimizer_id, self.loss_name, maximum=False
                )
            except KeyboardInterrupt:
                raise
            except Exception:
                count += 1
                time.sleep(1)
                continue
            break

        if count == self.MAX_TRIES:
            raise Exception("unable to fetch experiments with current optimizer id")

        experiment_count = response_data.get("experimentCount")
        best_metric = response_data.get("metricValue")

        if (experiment_count is None) or (best_metric is None):
            return

        data.update({"best_metric": best_metric})
        lmup = self.get_prediction(**data)

        if lmup:
            lower, mean, upper, p_improvement = lmup

            return {
                "lower": lower,
                "mean": mean,
                "upper": upper,
                "prob_improvement": p_improvement,
                "experiment_count": experiment_count,
                "best_metric": best_metric,
            }

        return

    def stop_early(self, **data):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """
        if self.mode == "global":
            return self._global_stop_early(**data)

        else:
            return self._local_stop_early(**data)

    def get_prediction(self, **request_data):
        """
        Please email lcp-beta@comet.ml for comments or questions.
        """

        # Copy default fields
        prediction_request = self.defaults.copy()

        # Update fields
        prediction_request.update(request_data)

        LOGGER.debug(
            "Get prediction on url %r with data %r",
            self.predict_url,
            prediction_request,
        )

        response = self._session.post(
            self.predict_url, json={"data": prediction_request}, timeout=300
        )

        if response.status_code == 200:
            response_data = response.json().get("response")
            self._set_prediction(response_data)
            return (
                response_data["min"],
                response_data["mean"],
                response_data["max"],
                response_data["probability_of_improvement"],
            )

        elif response.status_code == 201:
            return None
        else:
            raise Exception(
                "Invalid Predictor request for %s: %s" % (request_data, response)
            )

    def _set_prediction(self, prediction):
        self.latest_prediction.update(prediction)

    @property
    def get_latest_prediction(self):
        return self.latest_prediction
