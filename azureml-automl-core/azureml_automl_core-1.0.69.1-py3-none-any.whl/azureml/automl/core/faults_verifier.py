# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for the Data faults and misconfigurations for AutoML."""
from typing import Dict, List, Optional, Any
import json
import os
import pkg_resources

from sklearn.preprocessing.imputation import Imputer
from sklearn.pipeline import Pipeline

from automl.client.core.common.activity_logger import TelemetryActivityLogger
from automl.client.core.common.constants import AutoMLJson
from azureml.automl.core.automl_run_context import AutoMLAbstractRunContext
from azureml.automl.core.column_purpose_detection.types import StatsAndColumnPurposeType
from azureml.automl.core.constants import FeatureType as _FeatureType

from .stats_computation import RawFeatureStats
from .featurization.data_transformer import DataTransformer


class VerifierResults:
    PASSED = "passed"
    ALERTED = "alerted"
    FIXED = "fixed"
    DONE = "done"
    STATUS = {PASSED, ALERTED, FIXED, DONE}


class VerifiedFaultsTypes:
    CLASS_BALANCING = "_class_balancing"
    TRAIN_TEST_SPLIT = "_train_test_split"
    MISSING_VALUE_IMPUTATION = "_missing_value"
    DETECT_HIGH_CARDINAL_FEATURES = "_detect_high_cardinal_feature"
    CROSS_VALIDATION = "_cross_validation"


class ValidParameterKeys:
    COLUMN_NAME = "column_name"
    MISSING_VALUES = "missing_values"
    IMPUTATION_TYPE = "imputation_type"
    DATASET = "dataset"
    ROW_COUNTS = "row_counts"
    PERCENTAGE = "percentage"
    NUMBER_OF_FOLDS = "number_of_folds"
    CONTENT_TYPE = "content_type"
    SIZE_OF_SMALLEST_CLASS = "size_of_smallest_class"
    NUM_OF_SAMPLES = "num_of_samples"


class ValidParameterValues:
    MEAN = "mean"
    MODE = "mode"
    TRAIN = "train"
    TEST = "test"
    CATEGORICALHASH = "categorical_hash"
    TEXT = "text"


class VerifiedFault:
    def __init__(self,
                 type_name: str,
                 result: str,
                 parameters: Optional[List[Dict[str, Any]]],
                 is_child_run_specific: Optional[bool] = False):
        self.type = type_name
        self.result = result
        self.is_child_run_specific = is_child_run_specific
        if parameters is None:
            self.parameters = []   # type: List[Any]
        else:
            self.parameters = parameters

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "result": self.result,
            "parameters": self.parameters
        }


class VerifiedResult:
    def __init__(self,
                 fault: VerifiedFault,
                 description: Dict[str, Any]):

        self.type = fault.type
        self.result = fault.result
        self.parameters = fault.parameters

        self.fr_type = description["name"]
        self.fr_result = self.add_details_to_result(description["states"][self.result])
        self.fr_parameters = []     # type: List[Dict[Any, str]]

        for param in fault.parameters:
            temp_dict = {}
            for each in param.keys():
                temp_dict[description["parameters"][each]["name"]] = param[each]
            self.fr_parameters.append(temp_dict)

    def add_details_to_result(self, message: str) -> str:
        if self.type == VerifiedFaultsTypes.DETECT_HIGH_CARDINAL_FEATURES and len(self.parameters) > 0:
            message = message.format(self.parameters[0][ValidParameterKeys.CONTENT_TYPE])
        return message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "result": self.result,
            "parameters": self.parameters,
            "friendly_type": self.fr_type,
            "friendly_result": self.fr_result,
            "friendly_parameters": self.fr_parameters
        }


class VerifierManager:
    PACKAGE_NAME = 'azureml.automl.core'
    REFERENCE_FILE_PATH = pkg_resources.resource_filename(PACKAGE_NAME, 'faults_verifier_message.json')
    ARTIFACT_FILE_PATH = os.path.join('outputs', 'verifier_results.json')

    def __init__(self):
        self.data_faults_names = []  # type: List[str]
        self.data_faults_dict = {}   # type: Dict[str, VerifiedFault]
        self.ret_dict = {}           # type: Dict[str, Any]

    def has_fault_member(self, fault_name: str) -> bool:
        return fault_name in self.data_faults_dict.keys()

    def add_data_fault(self,
                       fault_name: str,
                       result: str,
                       parameters: Optional[List[Dict[str, Any]]] = None,
                       is_child_run_specific: Optional[bool] = False) -> None:
        self.data_faults_names.append(fault_name)
        self.data_faults_dict[fault_name] = VerifiedFault(fault_name,
                                                          result,
                                                          parameters,
                                                          is_child_run_specific)

    def add_data_fault_parameter(self, fault_name: str, parameters: Dict[str, str]) -> None:
        self.data_faults_dict[fault_name].parameters.append(parameters)

    def upload_to_file(self, run_context: AutoMLAbstractRunContext, ret_str: str, file_path: str) -> None:
        run_context.save_str_output(ret_str, file_path, overwrite_mode=True)

    def get_elaborate_dicts(self, friendly_desc: Dict[str, Any]) -> List[Any]:

        dict_list = []

        for fault_name in self.data_faults_names:
            fault = self.data_faults_dict[fault_name]
            res_obj = VerifiedResult(fault, friendly_desc["types"][fault.type])
            dict_list.append(res_obj.to_dict())

        return dict_list

    def write_result_file(self, run_context: AutoMLAbstractRunContext, logger: TelemetryActivityLogger,
                          remote_path: str = '') -> None:
        try:
            with open(self.REFERENCE_FILE_PATH, 'r') as f:
                friendly_desc = json.load(f)

            data_faults = self.get_elaborate_dicts(friendly_desc)

            self.ret_dict = {"schema_type": AutoMLJson.SCHEMA_TYPE_FAULT_VERIFIER,
                             "schema_version": friendly_desc['version'],
                             "faults": data_faults}

            ret_str = json.dumps(self.ret_dict)

            with run_context.get_run():
                try:
                    file_path = os.path.join(remote_path, self.ARTIFACT_FILE_PATH)
                    self.upload_to_file(run_context, ret_str, file_path)   # Upload to Artifacts.

                except Exception:
                    logger.debug("Failed uploading version files to artifact services.")

        except FileNotFoundError:
            logger.debug("Reference file, `faults_verifier_message.json` does not exist.")

    def update_data_verifier_for_cv(self, number_of_folds: int) -> None:
        """
        Update VerifierManager object data fault with number of folds in Cross Validation.

        :param number_of_folds: Number of folds in cross validation.
        :return: None
        """
        self.add_data_fault(
            VerifiedFaultsTypes.CROSS_VALIDATION,
            result=VerifierResults.DONE,
            parameters=[{ValidParameterKeys.NUMBER_OF_FOLDS: str(number_of_folds)}]
        )

    def update_data_verifier_for_train_test_validation(self, train_row_count: int, test_row_count: int) -> None:
        """
        Update VerifierManager object data faults with the train/test sample ratio.

        :param train_row_count: Sample count in training set.
        :param test_row_count: Sample count in verification set.
        :return: None
        """
        self.add_data_fault(
            VerifiedFaultsTypes.TRAIN_TEST_SPLIT,
            result=VerifierResults.DONE,
            parameters=[
                {
                    ValidParameterKeys.DATASET: ValidParameterValues.TRAIN,
                    ValidParameterKeys.ROW_COUNTS: str(train_row_count),
                    ValidParameterKeys.PERCENTAGE: str(100. * train_row_count / (train_row_count + test_row_count))
                },
                {
                    ValidParameterKeys.DATASET: ValidParameterValues.TEST,
                    ValidParameterKeys.ROW_COUNTS: str(test_row_count),
                    ValidParameterKeys.PERCENTAGE: str(100. * test_row_count / (train_row_count + test_row_count))
                }
            ]
        )

    def update_data_verifier_for_missing_values(self, data_transformer: DataTransformer) -> None:
        """
        Detect missing value imputation in DataTransformer and
        update missing values strategy of VerifierManager object.

        :param data_transformer: DataTransformer object.
        :return: None
        """
        if data_transformer.stats_and_column_purposes is None or not data_transformer.transformer_and_mapper_list:
            return
        for col in data_transformer.stats_and_column_purposes:
            self._update_data_verifier_for_missing_value(col[0], col[2])

        if self.has_fault_member(VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION):
            column_fault_verifier_mapping = {
                p[ValidParameterKeys.COLUMN_NAME]: p
                for p in self.data_faults_dict[VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION].parameters
            }
        else:
            self.add_data_fault(VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION, VerifierResults.PASSED)
            return
        for transformer_mapper in data_transformer.transformer_and_mapper_list:
            for f in transformer_mapper.mapper.features:
                col_name = _get_columnName(f)
                if col_name in column_fault_verifier_mapping.keys() and _is_imputer(f[1]):
                    column_fault_verifier_mapping[col_name][ValidParameterKeys.IMPUTATION_TYPE] = f[1][0].strategy

    def update_data_verifier_for_text_class_validation(self, stats_and_column_purpose:
                                                       Optional[List[StatsAndColumnPurposeType]]) -> None:
        """
        Detect high cardinality features from DataTransformer and update VerifierManager object with fault.

        :param stats_and_column_purpose: Statistics and other info about columns from a data transformer.
        :return: None
        """
        if stats_and_column_purpose is None:
            stats_and_column_purpose = []

        for col in stats_and_column_purpose:
            column_purpose = col[1]
            if column_purpose == _FeatureType.CategoricalHash or column_purpose == _FeatureType.Text:
                content_type = ValidParameterValues.CATEGORICALHASH \
                    if column_purpose == _FeatureType.CategoricalHash else ValidParameterValues.TEXT
                if not self.has_fault_member(VerifiedFaultsTypes.DETECT_HIGH_CARDINAL_FEATURES):
                    self.add_data_fault(
                        VerifiedFaultsTypes.DETECT_HIGH_CARDINAL_FEATURES, VerifierResults.DONE)
                self.add_data_fault_parameter(VerifiedFaultsTypes.DETECT_HIGH_CARDINAL_FEATURES, {
                    ValidParameterKeys.COLUMN_NAME: str(col[2]),
                    ValidParameterKeys.CONTENT_TYPE: content_type
                })
        if not self.has_fault_member(VerifiedFaultsTypes.DETECT_HIGH_CARDINAL_FEATURES):
            self.add_data_fault(VerifiedFaultsTypes.DETECT_HIGH_CARDINAL_FEATURES, VerifierResults.PASSED)

    def update_data_verifier_for_class_balancing_validation(self, is_resample: bool, size_of_smallest_class: int,
                                                            num_of_samples: int) -> None:
        """
        Detect class imbalance and update VerifierManager object with fault.

        :param is_resample: Boolean shows whether resampling happens or not
        :param min_size_of_class: number of samples in the smallest class
        :return: None
        """
        if is_resample:
            self.add_data_fault(VerifiedFaultsTypes.CLASS_BALANCING,
                                result=VerifierResults.ALERTED,
                                parameters=[{
                                    ValidParameterKeys.SIZE_OF_SMALLEST_CLASS: str(size_of_smallest_class),
                                    ValidParameterKeys.NUM_OF_SAMPLES: str(num_of_samples)}]
                                )
        else:
            self.add_data_fault(VerifiedFaultsTypes.CLASS_BALANCING, VerifierResults.PASSED)

    def _update_data_verifier_for_missing_value(self, raw_data_stats: RawFeatureStats, col_name: str) -> None:
        """
        Detect missing value data and update missing values of VerifierManager object.

        :param raw_data_stats: RawFeatureStats object.
        :param col_name: column name string.
        :return: None
        """
        if raw_data_stats.num_na > 0:
            if not self.has_fault_member(VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION):
                self.add_data_fault(
                    VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION, VerifierResults.FIXED)
            self.add_data_fault_parameter(VerifiedFaultsTypes.MISSING_VALUE_IMPUTATION, {
                ValidParameterKeys.COLUMN_NAME: col_name
            })


def _get_columnName(features: List[Any]) -> Any:
    """
    Returns column name from features list of a transformer.
    :param features: List of features obtained from a transformer.
    :return: Any: Column name, same type as input dataset.
    """
    if isinstance(features[0], List):
        col_name = features[0][0]     # When input dataset is pandas dataframe.
    else:
        col_name = features[0]       # When input dataset is numpy array.
    return col_name


def _is_imputer(f: Any) -> bool:
    """Check if Transformer is Imputer Type."""
    if isinstance(f, List):
        return isinstance(f[0], Imputer)
    elif isinstance(f, Pipeline):
        return any([_is_imputer(elem[1]) for elem in f.steps])
    else:
        return False


def print_fault_misconfiguration_detection_results(Run: int) -> None:
    """Print the results of fault/misconfiguration detection results."""
    try:
        pass
    except Exception:
        print("Cannot find the fault/misconfiguration detection results file.")
