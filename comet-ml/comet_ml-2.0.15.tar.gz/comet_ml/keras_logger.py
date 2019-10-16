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
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import logging

from comet_ml import tensorboard_logger
from comet_ml._logging import GET_CALLBACK_FAILURE, check_module

LOGGER = logging.getLogger(__name__)


def fit_keras_logger(experiment, original, *args, **kwargs):
    return fit_logger("keras", "keras", experiment, original, *args, **kwargs)


def fit_tf_logger(experiment, original, *args, **kwargs):
    return fit_logger(
        "tf-keras", "TensorFlow Keras", experiment, original, *args, **kwargs
    )


def fit_logger(keras_type, framework, experiment, original, *args, **kwargs):
    if not experiment.disabled_monkey_patching:
        try:
            callback = experiment.get_callback(keras_type)
        except Exception:
            LOGGER.warning(GET_CALLBACK_FAILURE, framework)

        if "callbacks" in kwargs and kwargs["callbacks"] is not None:
            callbacks = kwargs["callbacks"]
            # Only append the callback if it's not there.
            if not any(
                x.__class__.__name__ == callback.__class__.__name__ for x in callbacks
            ):
                LOGGER.debug("adding %r logger", framework)
                callbacks.append(callback)
            else:
                LOGGER.debug("not adding %r logger", framework)
        else:
            kwargs["callbacks"] = [callback]

        LOGGER.debug("tensorboard metric logging disabled by %r logger", framework)
        # Disable tensorboard metric logging as it conflicts with keras:
        tensorboard_logger.LOG_METRICS = False

        LOGGER.debug("New keras arguments %r %r", args, kwargs)

    return args, kwargs


def multi_gpu_model_wrapper(experiment, original, model, result, *args, **kwargs):
    try:
        experiment._storage["keras"]["gpu_model_%s" % id(model)] = model.to_json()
    except Exception:
        experiment._log_once_at_level(
            logging.DEBUG, "Failed to saved multi-GPU model", exc_info=True
        )


def patch(module_finder):
    check_module("keras")
    check_module("tensorflow")

    module_finder.register_before("keras.models", "Model.fit", fit_keras_logger)
    module_finder.register_before(
        "keras.models", "Model.fit_generator", fit_keras_logger
    )
    module_finder.register_before(
        "tensorflow.python.keras.models", "Model.fit", fit_tf_logger
    )
    module_finder.register_before(
        "tensorflow.python.keras.models", "Model.fit_generator", fit_tf_logger
    )
    module_finder.register_after(
        "keras.utils.training_utils", "multi_gpu_model", multi_gpu_model_wrapper
    )


check_module("keras")
check_module("tensorflow")
