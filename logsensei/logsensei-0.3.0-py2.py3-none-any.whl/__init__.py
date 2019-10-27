"""Personal Formatting on Loguru"""

__version__ = "0.3.0"
__author__ = "Aditya Kelvianto Sidharta"

import io
import logging
import os
import sys
from collections import Counter
from typing import Any

import numpy as np
from loguru import logger as loguru_logger
from sklearn.metrics import (
    accuracy_score,
    explained_variance_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)

from logsensei.constant import MAX_SET, MAX_LIST, MAX_DF, MAX_ARRAY
from logsensei.utils import _get_datetime


# pylint: disable=too-many-public-methods
class Logger:
    def __init__(self):
        """
        Initialize the logger
        """
        self.default_level = logging.INFO
        self.template = {}
        self.file_index = None
        self.file_path = None
        sys_level = logging.INFO

        time_sys_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green>"
        level_sys_format = "<level>{level}</level>"
        function_sys_format = "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
        message_sys_format = "<level>{message}</level>"
        self.sys_format = "{} | {} | {} | {}".format(
            time_sys_format, level_sys_format, function_sys_format, message_sys_format
        )

        time_file_format = "<green>{time:YYYY-MM-DD HH:mm:ss:SSS}</green>"
        level_file_format = "<level>{level: <8}</level>"
        function_file_format = "<cyan>{name: ^15}</cyan>:<cyan>{function: ^15}</cyan>:<cyan>{line: >3}</cyan>"
        message_file_format = "<level>{message}</level>"
        self.file_format = "{} | {} | {} | {}".format(
            time_file_format, level_file_format, function_file_format, message_file_format
        )

        self.logger = loguru_logger
        self.logger.patch(lambda record: record.update(name="my_module"))

        self.logger.remove(0)
        self.sys_index = self.logger.add(sys.stderr, format=self.sys_format, level=sys_level)

    def reset(self):
        """
        Reset the logger
        """
        if self.file_index is not None:
            self.logger.remove(self.file_index)

        self.logger.remove(self.sys_index)
        self.sys_index = self.logger.add(sys.stderr, format=self.sys_format, level=logging.INFO)

        self.default_level = logging.INFO
        self.template = {}
        self.file_index = None
        self.file_path = None

    def setup(self, name: str, logger_file: str, level: int = logging.DEBUG):
        """
        Saving logs to specified log file
        Args:
            name: Filename of the log file
            logger_file: directory where the log file should be saved
            level: Minimum logging level which will be saved to the log file
        """
        file_name = name
        datetime = _get_datetime()
        file_level = level
        self.file_path = os.path.join(logger_file, "{}_{}.log".format(file_name, datetime))

        if self.file_index is not None:
            self.logger.remove(self.file_index)

        self.file_index = self.logger.add(self.file_path, format=self.file_format, level=file_level)

    def level(self, item: str, level: int):
        """
        Changing the default logging level, the minimum logging level of the system output,
         or the minimum logging level of the file output
        Args:
            item: Types of log which should be changed. One of ['default', 'sys', 'file']
            level: Type of logging level chosen
        """
        if item == "default":
            self.default_level = level
        elif item == "sys":
            self.logger.remove(self.sys_index)
            self.sys_index = self.logger.add(sys.stderr, format=self.sys_format, level=level)
        elif item == "file":
            self.logger.remove(self.file_index)
            self.file_index = self.logger.add(self.file_path, format=self.file_format, level=level)
        else:
            raise ValueError("item must be one of the following: ['default', 'sys', 'file']")

    def debug(self, msg: str, depth: int = 1):
        """
        Performing Debug Logging Message
        Args:
            msg: Message to be logged
            depth: Recursion depth which will be used to retrieve the calling function
        """
        self.logger.opt(depth=depth).debug(msg)

    def info(self, msg: str, depth: int = 1):
        """
        Performing Info Logging Message
        Args:
            msg: Message to be logged
            depth: Recursion depth which will be used to retrieve the calling function
        """
        self.logger.opt(depth=depth).info(msg)

    def warning(self, msg: str, depth: int = 1):
        """
        Performing Warning Logging Message
        Args:
            msg: Message to be logged
            depth: Recursion depth which will be used to retrieve the calling function
        """
        self.logger.opt(depth=depth).warning(msg)

    def error(self, msg: str, depth: int = 1):
        """
        Performing Error Logging Message
        Args:
            msg: Message to be logged
            depth: Recursion depth which will be used to retrieve the calling function
        """
        self.logger.opt(depth=depth).error(msg)

    def critical(self, msg: str, depth: int = 1):
        """
        Performing Critical Logging Message
        Args:
            msg: Message to be logged
            depth: Recursion depth which will be used to retrieve the calling function
        """
        self.logger.opt(depth=depth).critical(msg)

    def log(self, msg: str, level: int, depth: int = 2):
        """
        Performing Logging Message with the chosen logging level
        Args:
            msg: Message to be logged
            level: Chosen Logging level
            depth: Recursion depth which will be used to retrieve the calling function
        """
        if level == logging.DEBUG:
            self.debug(msg, depth=depth)
        elif level == logging.INFO:
            self.info(msg, depth=depth)
        elif level == logging.WARNING:
            self.warning(msg, depth=depth)
        elif level == logging.ERROR:
            self.error(msg, depth=depth)
        elif level == logging.CRITICAL:
            self.critical(msg, depth=depth)
        else:
            raise ValueError("input parameter in level is unknown")

    def create(self, template_name: str, msg: str):
        """
        Creating the template message, saving it within the Logger Class
        Args:
            template_name: Name of the template which should be saved
            msg: Template message
        """
        if template_name in self.template.keys():
            self.logger.warning("Replacing the template message in {}".format(template_name))
        self.template[template_name] = msg

    def apply(self, template_name: str, *args):
        if template_name in self.template:
            self.log(self.template[template_name].format(*args), self.default_level, depth=3)
        else:
            raise ValueError("template_name has not been created before." " use logger.create to create new template.")

    def df(self, df: Any, df_name: str):
        """
        Performing Logging for DataFrame
        Args:
            df: DataFrame to be logged
            df_name:  Name of the DataFrame
        """
        buf = io.StringIO()
        df.info(buf=buf)
        s = buf.getvalue()
        info = "\n".join(s.split("\n")[3:-3])
        shape = df.shape
        self.log("DataFrame {} shape : {}".format(df_name, shape), self.default_level, depth=3)
        if len(info.split("\n")) <= MAX_DF:
            self.log("DataFrame {} info:".format(df_name), self.default_level, depth=3)
            self.log(info, self.default_level, depth=3)

    def array(self, array: np.array, array_name: str):
        """
        Performing Logging for Numpy arrays
        Args:
            array: Numpy Array to be logged
            array_name: Name of the Numpy array
        """
        shape = array.shape
        self.log("Array {} shape : {}".format(array_name, shape), self.default_level, depth=3)
        if array.ndim == 1:
            n_values = len(array)
            unique_values = set(array)
            n_unique_values = len(set(array))
            n_missing_values = np.sum(np.isnan(array))
            if n_unique_values <= MAX_ARRAY:
                self.log("Array {} unique values : {}".format(array_name, unique_values), self.default_level, depth=3)
            self.log("Array {} cardinality : {}".format(array_name, n_unique_values), self.default_level, depth=3)
            self.log(
                "Array {} missing values : {} ({:.2f}%)".format(
                    array_name, n_missing_values, n_missing_values / n_values * 100.0
                ),
                self.default_level,
                depth=3,
            )
            if (array.dtype == float) or (array.dtype == int):
                mean_value = np.nanmean(array)
                std_value = np.nanstd(array)
                max_value = np.nanmax(array)
                min_value = np.nanmin(array)
                median_value = np.nanmedian(array)
                perc_25_value = np.nanpercentile(array, 25)
                perc_75_value = np.nanpercentile(array, 75)
                self.log(
                    "Array {} info : MEAN={} | STD={} | MIN={} | 25TH={} | MEDIAN={} | 75TH={} | MAX={}".format(
                        array_name,
                        mean_value,
                        std_value,
                        min_value,
                        perc_25_value,
                        median_value,
                        perc_75_value,
                        max_value,
                    ),
                    self.default_level,
                    depth=3,
                )
            else:
                most_common = Counter(array).most_common(max(n_unique_values, 5))
                n_most_common = len(most_common)
                self.log(
                    "Array {} top {} values : ".format(array_name, n_most_common)
                    + " | ".join(["{} - {}({:.2f}%)".format(x[0], x[1], x[1] / n_values * 100.0) for x in most_common]),
                    self.default_level,
                    depth=3,
                )

    def compare(self, array_1: np.array, array_2: np.array, array_1_name: str, array_2_name: str):
        """
        Comparing the two Numpy Arrays, checking the intersection between the two arrays
        Args:
            array_1: First Numpy Array to be compared
            array_2: Second Numpy Array to be compared
            array_1_name: Name of the First Numpy Array
            array_2_name: Name of the Second Numpy Array
        """
        array_1_shape = array_1.shape
        array_2_shape = array_2.shape
        array_1_ndim = array_1.ndim
        array_2_ndim = array_2.ndim
        self.log(
            "Compare {} vs {} - shape : {} vs {}".format(array_1_name, array_2_name, array_1_shape, array_2_shape),
            self.default_level,
            depth=3,
        )
        if (array_1_ndim == 1) and (array_2_ndim == 1):
            cardinality = len(set(array_1).union(set(array_2)))
            array_1_unique = set(array_1)
            array_2_unique = set(array_2)
            array_intersection = array_1_unique.intersection(array_2_unique)
            array_1_outer = array_1_unique - array_intersection
            array_2_outer = array_2_unique - array_intersection
            self.log("Compare {} vs {} - cardinality :".format(array_1_name, array_2_name), self.default_level, depth=3)
            self.log(
                "Intersection {} and {} : {} ({:.2f}%)".format(
                    array_1_name, array_2_name, len(array_intersection), len(array_intersection) / cardinality
                ),
                self.default_level,
                depth=3,
            )
            self.log(
                "Unique Values in {} but not in {} : {} ({:.2f}%)".format(
                    array_1_name, array_2_name, len(array_1_outer), len(array_1_outer) / cardinality
                ),
                self.default_level,
                depth=3,
            )
            self.log(
                "Unique Values in {} but not in {} : {} ({:.2f}%)".format(
                    array_2_name, array_1_name, len(array_2_outer), len(array_2_outer) / cardinality
                ),
                self.default_level,
                depth=3,
            )

    def dict(self, dictionary: dict, dictionary_name: str):
        """
        Performing Logging for Python dictionary
        Args:
            dictionary: Python Dictionary to be logged
            dictionary_name: Name of the Python dictionary
        """
        n_values = len(dictionary)
        self.log("Dictionary {} length : {}".format(dictionary_name, n_values), self.default_level, depth=3)
        self.log("Dictionary {}".format(dictionary_name), self.default_level, depth=3)
        for key, value in dictionary.items():
            self.log("{} - {}".format(key, value), self.default_level, depth=3)

    def list(self, input_list: list, input_list_name: str):
        """
        Performing logging for Python list
        Args:
            input_list: Python list to be logged
            input_list_name: Name of the Python list
        """
        n_values = len(input_list)
        self.log("List {} length : {}".format(input_list_name, n_values), self.default_level, depth=3)
        if n_values <= MAX_LIST:
            self.log("List {} : {}".format(input_list_name, input_list), self.default_level, depth=3)

    def set(self, input_set: set, input_set_name: str):
        """
        Performing logging for Python set
        Args:
            input_set: Python set to be logged
            input_set_name: Name of the Python set
        """
        n_values = len(input_set)
        self.log("Set {} length : {}".format(input_set_name, n_values), self.default_level, depth=3)
        if n_values <= MAX_SET:
            self.log("Set {} : {}".format(input_set_name, input_set), self.default_level, depth=3)

    def savepath(self, save_path: str):
        """
        Performing Logging for saving file to a certain path
        Args:
            save_path: Path where the object will be saved
        """
        self.log("Saving to path : {}".format(save_path), self.default_level, depth=3)

    def loadpath(self, load_path: str):
        """
        Performing Logging for loading file to a certain path
        Args:
            load_path: Path where the object is loaded from
        """
        self.log("Loading from path : {}".format(load_path), self.default_level, depth=3)

    def scikit(self, model: Any, model_name: str):
        """
        Performing Logging for Scikit-Learn model
        Args:
            model: Scikit-Learn model to be logged
            model_name: Name of the Scikit-Learn model
        """
        self.log("Model {} type : {}".format(model_name, type(model).__name__), self.default_level, depth=3)
        self.dict(model.get_params(), "Parameters of scikit-learn model {}".format(model_name))

    #     def xgboost(self, model, model_name):
    #         raise NotImplementedError("XGBoost logging will come in the next release")

    #     def lightgbm(self, model, model_name):
    #         raise NotImplementedError("LightGBM logging will come in the next release")

    def pytorch_tensor(self, tensor: Any, tensor_name: str):
        """
        Performing Logging for PyTorch tensor
        Args:
            tensor: PyTorch tensor to be logged
            tensor_name: Name of the PyTorch tensor
        """
        shape = tuple(tensor.shape)
        if tensor.is_cuda:
            array = tensor.cpu().numpy()
        else:
            array = tensor.numpy()
        max_value = np.max(array)
        min_value = np.min(array)
        mean_value = np.mean(array)
        median_value = np.median(array)
        self.log("Tensor {} shape : {}".format(tensor_name, shape), self.default_level, depth=3)
        self.log(
            "Tensor {} info : MEAN={} | MIN={} | MEDIAN={} | MAX={}".format(
                tensor_name, mean_value, min_value, median_value, max_value
            ),
            self.default_level,
            depth=3,
        )

    def tensorflow_tensor(self, tensor: Any, tensor_name: str):
        """
        Performing Logging for TensorFlow Tensor
        Args:
            tensor: TensorFlow tensor to be logged
            tensor_name: Name of the TensorFlow tensor
        """
        shape = tuple(tensor.shape)
        array = tensor.numpy()
        max_value = np.max(array)
        min_value = np.min(array)
        mean_value = np.mean(array)
        median_value = np.median(array)
        self.log("Tensor {} shape : {}".format(tensor_name, shape), self.default_level)
        self.log(
            "Tensor {} info : MEAN={} | MIN={} | MEDIAN={} | MAX={}".format(
                tensor_name, mean_value, min_value, median_value, max_value
            ),
            self.default_level,
            depth=3,
        )

    def tensorflow_model(self, model: Any, model_name: str):
        """
        Performing Logging for TensorFlow model
        Args:
            model: TensorFlow model to be logged
            model_name: Name of the TensorFlow model
        """
        self.log("TensorFlow Model {} Summary :".format(model_name), self.default_level, depth=3)
        self.log(model.summary(), self.default_level, depth=3)

    def regression(self, true_array: np.array, predict_array: np.array, model_name: str):
        """
        Performing Logging for the evaluation of the regression prediction
        Args:
            true_array: Target array of the regression model
            predict_array: Predicted array of the regression model
            model_name: Name of the Regression model
        """
        self.log("{} Regression Score".format(model_name), self.default_level, depth=3)
        self.log("=" * 20, self.default_level, depth=3)
        self.log(
            "Mean Absolute Error : {}".format(mean_absolute_error(true_array, predict_array)),
            self.default_level,
            depth=3,
        )
        self.log(
            "Mean Squared Error : {}".format(mean_squared_error(true_array, predict_array)), self.default_level, depth=3
        )
        self.log("R2 Score : {}".format(r2_score(true_array, predict_array)), self.default_level, depth=3)
        self.log(
            "Explained Variance Score : {}".format(explained_variance_score(true_array, predict_array)),
            self.default_level,
            depth=3,
        )

    def classification(self, true_array: np.array, predict_array: np.array, array_name: str):
        """
        Performing logging for the evaluation of the classification prediction
        Args:
            true_array: Target array of the classification model
            predict_array: Predicted array of the classification model
            array_name: Name of the Classification Model
        """
        self.log("{} Classification Score".format(array_name), self.default_level, depth=3)
        self.log("=" * 20, self.default_level, depth=3)
        self.log("Accuracy Score : {}".format(accuracy_score(true_array, predict_array)), self.default_level, depth=3)
        self.log("Precision Score : {}".format(precision_score(true_array, predict_array)), self.default_level, depth=3)
        self.log("Recall Score : {}".format(recall_score(true_array, predict_array)), self.default_level, depth=3)
        self.log("F1 Score : {}".format(f1_score(true_array, predict_array)), self.default_level, depth=3)
        self.log("ROC AUC Score : {}".format(roc_auc_score(true_array, predict_array)), self.default_level, depth=3)

    def multiclass(self, true_array: np.array, predict_array: np.array, array_name: str):
        """
        Performing logging for the evaluation of the multi-classification prediction
        Args:
            true_array: Target array of the multi-classification prediction
            predict_array: Predicted array of the multi-classification prediction
            array_name: Name of the multi-classification model

        """
        self.log("{} Classification Score".format(array_name), self.default_level, depth=3)
        self.log("=" * 20, self.default_level, depth=3)
        self.log("Accuracy Score : {}".format(accuracy_score(true_array, predict_array)), self.default_level, depth=3)
        self.log(
            "Precision Score : {}".format(precision_score(true_array, predict_array, average="micro")),
            self.default_level,
            depth=3,
        )
        self.log(
            "Recall Score : {}".format(recall_score(true_array, predict_array, average="micro")),
            self.default_level,
            depth=3,
        )
        self.log(
            "F1 Score : {}".format(f1_score(true_array, predict_array, average="micro")), self.default_level, depth=3
        )
        self.log(
            "ROC AUC Score : {}".format(roc_auc_score(true_array, predict_array, average="micro")),
            self.default_level,
            depth=3,
        )


logger = Logger()
