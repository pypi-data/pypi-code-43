import inspect
import os
from enum import IntEnum
from typing import Union
from xml.etree import ElementTree

from azureml.studio.core.logger import common_logger, ExceptionFormatter
from azureml.studio.core.utils.strutils import get_args_from_template, remove_suffix
from .types import is_null_or_empty, is_null_or_whitespace

_DIR_NAME = os.path.dirname(os.path.realpath(__file__))
EXCEPTION_FILE_NAME = os.path.join(_DIR_NAME, "Exceptions.xml")
CUSTOMER_SUPPORT_GUIDANCE = "You can contact Studio support team {mailto: amlstudiov2pp@microsoft.com}" \
                            " for further help. Please include the full URL in the browser and" \
                            " timestamp with the failure for better problem diagnosis."


class ErrorType:
    NO_ERROR = 'NoException'
    LIBRARY_ERROR = 'LibraryException'
    MODULE_ERROR = 'ModuleException'


class ErrorInfo:
    def __init__(self, error):
        self._error = error

    @property
    def exception_type(self):
        raise NotImplementedError

    @property
    def error_id(self):
        return self._error.id.name

    @property
    def error_code(self):
        return self._error.id.value

    @property
    def message(self):
        return f'{self.error_id}: {self._error.__str__()}'

    @property
    def traceback(self):
        cause = self._error
        exc_info = (type(cause), cause, cause.__traceback__)
        return ExceptionFormatter().format(exc_info=exc_info).split('\n')

    def to_dict(self):
        return {
            'ErrorId': self.error_id,
            'ErrorCode': self.error_code,
            'ExceptionType': self.exception_type,
            'Traceback': self.traceback,
            'Message': self.message
        }


class ModuleErrorInfo(ErrorInfo):
    @property
    def exception_type(self):
        return ErrorType.MODULE_ERROR


class LibraryErrorInfo(ErrorInfo):
    @property
    def exception_type(self):
        return ErrorType.LIBRARY_ERROR

    @property
    def error_id(self):
        return type(self._error).__name__

    @property
    def error_code(self):
        return LibraryExceptionError(self._error).id.value

    @property
    def message(self):
        return f'Library Error - {self.error_id}: {self._error.__str__()}'


class ErrorId(IntEnum):
    ColumnNotFound = 1
    ParameterParsing = 2
    NullOrEmpty = 3
    GreaterThan = 4
    GreaterThanOrEqualTo = 5
    LessThan = 6
    LessThanOrEqualTo = 7
    NotInRangeValue = 8
    IncorrectAzureStorageOrContainer = 9
    NotEqualColumnNames = 10
    NoColumnsSelected = 11
    UntrainedModel = 12
    InvalidLearner = 13
    ColumnUniqueValuesExceeded = 14
    ErrorDatabaseConnection = 15
    NotCompatibleColumnTypes = 16
    InvalidColumnType = 17
    InvalidDataset = 18
    NotSortedValues = 19
    TooFewColumnsInDataset = 20
    TooFewRowsInDataset = 21
    BadNumberOfSelectedColumns = 22
    InvalidTargetColumn = 23
    NotLabeledDataset = 24
    NotScoredDataset = 25
    EqualColumnNames = 26
    InconsistentSize = 27
    DuplicatedColumnName = 28
    InvalidUri = 29
    CouldNotDownloadFile = 30
    TooFewColumnsSelected = 31
    NaN = 32
    Infinity = 33
    MoreThanOneRating = 34
    MissingFeatures = 35
    DuplicateFeatureDefinition = 36
    MultipleLabelColumns = 37
    InvalidNumberOfElements = 38
    FailedToCompleteOperation = 39
    SingleDeprecation = 40
    MultipleDeprecation = 41
    CouldNotConvertColumn = 42
    MissingEquals = 43
    CannotDeriveElementType = 44
    MixedColumn = 45
    InvalidPathForDirectoryCreation = 46
    TooFewFeatureColumnsInDataset = 47
    CouldNotOpenFile = 48
    FileParsingFailed = 49
    EqualInputOutputFiles = 50
    EqualOutputFiles = 51
    IncorrectAzureStorageKey = 52
    NoUserFeaturesOrItemsFound = 53
    TooFewDistinctValuesInColumn = 54
    DeprecationNoReplacement = 55
    InvalidColumnCategorySelected = 56
    AlreadyExists = 57
    NotExpectedLabelColumn = 58
    ColumnIndexParsing = 59
    InvalidColumnIndexRange = 60
    ColumnCountNotEqual = 61
    FailedToEvaluateRScript = 63
    LearnerTypesNotCompatible = 62
    IncorrectAzureStorageOrKey = 64
    IncorrectAzureBlobName = 65
    UnableToUploadToAzureBlob = 66
    UnexpectedNumberOfColumns = 67
    InvalidHiveScript = 68
    InvalidSQLScript = 69
    AzureTableNotExist = 70
    InvalidCredentials = 71
    TimeoutOccured = 72
    ErrorConvertingColumn = 73
    ErrorConvertingSparseToCategorical = 74
    InvalidBinningFunction = 75
    UnsupportedBlobWriteMode = 77
    HttpRedirectionNotAllowed = 78
    IncorrectAzureContainer = 79
    ColumnWithAllMissings = 80
    PCASparseDatasetWrongDimensionsNumber = 81
    UnableToDeserializeModel = 82
    InvalidTrainingDataset = 83
    UnableToEvaluateCustomModel = 84
    FailedToEvaluateScript = 85
    InvalidCountingTransform = 86
    InvalidCountTableType = 87
    InvalidCountingType = 88
    IncorrectNumberOfClasses = 89
    FailedToCreateHiveTable = 90
    UnsupportedCustomModuleLanguage = 100
    NonUniqueIDs = 101
    InvalidZipFile = 102
    NoModuleDefinitionFilesFound = 103
    RLanguageScriptNotFound = 104
    UnsupportedParameterType = 105
    UnsupportedInputType = 106
    UnsupportedOutputType = 107
    ExceedSupportedPortCount = 108
    ColumnPickerUnsupportedSyntax = 109
    ColumnPickerPortIdNotFound = 110
    InvalidPropertyDefinition = 111
    InvalidModuleDefinitionFile = 112
    ErrorsInModuleDefinitionFile = 113
    BuildCustomModuleFailed = 114
    UnableToWrite = 121
    MultipleWeightColumns = 122
    ColumnOfVectorsLabelFailed = 123
    NonNumericWeightColumn = 124
    SchemaDoesNotMatch = 125
    UnsupportedDomain = 126
    ImageExceedsLimit = 127
    NumberOfUnconditionalProbabilitiesExceedsLimit = 128
    ExceedsColumnLimit = 129
    AllRowsInTrainingDatasetContainMissingValues = 130
    UnzipDatasetsFailed = 131
    UnpackMultipleFilesFound = 132
    UnpackDatasetNotFound = 133
    LabelColumnDoesNotHaveLabeledPoints = 134
    UnsupportedCluster = 135
    NoFileNameFound = 136
    AzureTableConversion = 137
    ModuleOutOfMemory = 138
    CouldNotConvertColumnRow = 139
    OnlyLabelColumnSelected = 140
    NotEnoughNormalizedColumns = 141
    CannotLoadCert = 142
    NotGitHubURL = 143
    GitHubURLWrongTree = 144
    ReplicationDirectoryIssue = 145
    PathTooLong = 146
    GitHubAccess = 147
    UnableExtractData = 148
    GithubFileNotFound = 149
    UnableUnzipWithGithub = 150
    CloudStorageWriteError = 151
    BadAzureCloudType = 152
    BadStorageEndPoint = 153
    JoinOnIncompatibleColumnTypes = 154
    ColumnNamesNotString = 155
    FailedToReadAzureSQLDatabase = 156
    IncorrectAzureMLDatastore = 157
    LibraryException = 1000

    @staticmethod
    def from_name(name):
        """Given a name of ErrorId, find a corresponding item in ErrorId enum.

        :param name: The name of ErrorId.
        :return: The corresponding item in ErrorId enum.
        """
        for e in ErrorId:
            if e.name == name:
                return e
        else:
            raise ValueError(f"Unrecognized ErrorId: {name}")

    @staticmethod
    def from_class_name(class_name):
        """Given a class name of ModuleError, find the corresponding ErrorId for it.

        Assumes that the error class name is named as '{ErrorId.name}Error'.

        :param class_name: The name of ErrorId.
        :return: The corresponding item in ErrorId enum.
        """
        name = remove_suffix(class_name, suffix='Error')
        return ErrorId.from_name(name)


class AlghostRuntimeError(Exception):
    """
    General exception inside alghost. (Internal Server Error for DS)
    """

    def __init__(self, message):
        super().__init__(message)


doc = ElementTree.parse(EXCEPTION_FILE_NAME)


class ErrorMetaClass(type):
    """
    This metaclass is designed to check whether the error classes are defined correctly according to xml file.
    """

    def __new__(mcs, name, bases, namespace, **kargs):
        # Only check subclasses, do not check for base class.
        if name != 'ModuleError':
            init_func = namespace.get('__init__')
            mcs._check_class_definition_is_suitable_to_xml_file(name, init_func)

        return super().__new__(mcs, name, bases, namespace)

    @classmethod
    def _check_class_definition_is_suitable_to_xml_file(mcs, class_name, init_func):
        if not class_name.endswith('Error'):
            raise ValueError(f"Bad class name '{class_name}'. Must end with 'Error'.")

        # Will raise if err_id not found
        err_id = ErrorId.from_class_name(class_name)

        # Check the entry in xml
        err_name = err_id.name
        messages = doc.find(f"Exception[@id='{err_name}']/Messages")
        if not messages:
            raise ValueError(f"No xml entry found for {err_name}.")

        keywords_in_init_func = mcs._get_arg_names_of_func(init_func)

        for m in messages:
            if m.tag == 'Message' and 'args' not in m.attrib:
                # 'Message' tag without 'args' attributes indicates that is a newly kwargs message style.
                keywords_in_template = get_args_from_template(m.text)
                for keyword in keywords_in_template:
                    if keyword not in keywords_in_init_func:
                        raise ValueError(f"Argument '{keyword}' found in xml message,"
                                         f" but does not exist in {class_name}.__init__ method as a param."
                                         f" Maybe a typo?")

    @staticmethod
    def _get_arg_names_of_func(func):
        spec = inspect.getfullargspec(func)

        result = spec.args
        result.remove('self')

        if spec.varkw:
            result.extend(spec.varkw)

        if spec.kwonlyargs:
            result.extend(spec.kwonlyargs)

        return tuple(result)


class ModuleError(Exception, metaclass=ErrorMetaClass):
    def __init__(self, *args, **kwargs):
        class_name = type(self).__name__
        self.id = ErrorId.from_class_name(class_name)

        message = self._format_with_keyword_args(kwargs)
        if not message:
            common_logger.warning(f"Error '{self.id.name}' does not found matching kwargs message, "
                                  f"fallback to positional arguments")
            message = self._format_with_positional_args(args)

        self.message = message
        super().__init__(message)

    def _format_with_keyword_args(self, kwargs: dict):
        messages = doc.findall(f"Exception[@code='{self.id.value}']/Messages/Message")
        for m in messages:
            # 'Message' tag without 'args' attributes indicates that is a newly kwargs message style.
            if 'args' not in m.attrib:
                keywords_in_template = get_args_from_template(m.text)
                keywords_in_kwargs = tuple(kwargs.keys())
                if set(keywords_in_template) == set(keywords_in_kwargs):
                    return m.text.format(**kwargs)
        return None

    def _format_with_positional_args(self, args: tuple):
        arg_count = len(args)

        x_elem = None
        if arg_count > 0:
            x_elem = doc.find("Exception[@code='{0}']/Messages/Message[@args='{1}']".format(self.id.value, arg_count))

        if x_elem is None:
            x_elem = doc.find("Exception[@code='{0}']/Messages/Default".format(self.id.value))

        if x_elem is not None:
            err_msg = x_elem.text.format(*args)
            return err_msg
        else:
            return "{0}(code={1})".format(self.id.name, self.id.value)

    def __str__(self):
        return self.message


class ColumnNotFoundError(ModuleError):
    def __init__(self, column_id: str = None, arg_name_missing_column: str = None, arg_name_has_column: str = None):
        super().__init__(**_valid_kwargs(locals()))


class ParameterParsingError(ModuleError):
    def __init__(self, arg_name_or_column: str = None, to_type: str = None, from_type: str = None, arg_value=None,
                 fmt: str = None):
        super().__init__(**_valid_kwargs(locals()))


class NullOrEmptyError(ModuleError):
    def __init__(self, name: str = None):
        valid_params = _exact_valid_parameters(name)
        super().__init__(*valid_params)


class GreaterThanError(ModuleError):
    def __init__(self, arg_name: str = None, b=None):
        valid_params = _exact_valid_parameters(arg_name, b)
        super().__init__(*valid_params)


class GreaterThanOrEqualToError(ModuleError):
    def __init__(self, arg_name: str = None, target_val=None, true_val=None):
        super().__init__(**_valid_kwargs(locals()))


class LessThanError(ModuleError):
    def __init__(self, arg_name: str = None, b=None):
        valid_params = _exact_valid_parameters(arg_name, b)
        super().__init__(*valid_params)


class LessThanOrEqualToError(ModuleError):
    def __init__(self, left_arg_name: str = None, left_arg_val=None, right_arg_name: str = None, right_arg_val=None):
        super().__init__(ErrorId.LessThanOrEqualTo, **_valid_kwargs(locals()))


class NotInRangeValueError(ModuleError):
    def __init__(self, arg_name: str = None, a=None, b=None, reason: str = None):
        super().__init__(**_valid_kwargs(locals()))


class IncorrectAzureStorageOrContainerError(ModuleError):
    def __init__(self, account_name, container_name):
        super().__init__(account_name, container_name)


class NotEqualColumnNamesError(ModuleError):
    def __init__(self, col_index, dataset1, dataset2):
        super().__init__(col_index, dataset1, dataset2)


class NoColumnsSelectedError(ModuleError):
    def __init__(self, column_set: str = None):
        valid_params = _exact_valid_parameters(column_set)
        super().__init__(*valid_params)


class UntrainedModelError(ModuleError):
    def __init__(self, arg_name=None):
        super().__init__(**_valid_kwargs(locals()))


class InvalidLearnerError(ModuleError):
    def __init__(self, arg_name: str = None, learner_type: str = None):
        super().__init__(**_valid_kwargs(locals()))


class ColumnUniqueValuesExceededError(ModuleError):
    def __init__(self, column_name=None, limitation=None):
        super().__init__(**_valid_kwargs(locals()))


class ErrorDatabaseConnectionError(ModuleError):
    def __init__(self, conn_str):
        super().__init__(conn_str)


class NotCompatibleColumnTypesError(ModuleError):
    def __init__(self, first_col_names: str = None, second_col_names: str = None,
                 first_dataset_names: str = None, second_dataset_names: str = None):
        super().__init__(**_valid_kwargs(locals()))


class InvalidColumnTypeError(ModuleError):
    def __init__(self, col_type: Union[type, str] = None, col_name: str = None, arg_name: str = None):
        super().__init__(**_valid_kwargs(locals()))


class InvalidDatasetError(ModuleError):
    def __init__(self, dataset1: str = None, dataset2: str = None, reason: str = None,
                 invalid_data_category: str = None, troubleshoot_hint: str = None):
        super().__init__(**_valid_kwargs(locals()))


class NotSortedValuesError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class TooFewColumnsInDatasetError(ModuleError):
    def __init__(self, arg_name: str = None, required_columns_count: int = None):
        valid_params = _exact_valid_parameters(arg_name, required_columns_count)
        super().__init__(*valid_params)


class TooFewRowsInDatasetError(ModuleError):
    def __init__(self, arg_name: str = None, required_rows_count: int = None, actual_rows_count: int = None,
                 row_type: str = None):
        """

        :param arg_name: dataset name
        :param required_rows_count: the minimum row required.
        :param actual_rows_count: the number of (valid) row instances.
        :param row_type: works as attribute to modify row in error message
        """
        super().__init__(**_valid_kwargs(locals()))


class BadNumberOfSelectedColumnsError(ModuleError):
    def __init__(self, selection_pattern_friendly_name: str = None,
                 exp_col_count: int = None, act_col_count: int = None):
        valid_params = _exact_valid_parameters(selection_pattern_friendly_name, exp_col_count, act_col_count)
        super().__init__(*valid_params)


class InvalidTargetColumnError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class NotLabeledDatasetError(ModuleError):
    def __init__(self, dataset_name: str = None):
        super().__init__(**_valid_kwargs(locals()))


class NotScoredDatasetError(ModuleError):
    def __init__(self, dataset_name: str = None, learner_type: str = None):
        super().__init__(**_valid_kwargs(locals()))


class EqualColumnNamesError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class InconsistentSizeError(ModuleError):
    def __init__(self, friendly_name1: str = None, friendly_name2: str = None):
        valid_params = _exact_valid_parameters(friendly_name1, friendly_name2)
        super().__init__(*valid_params)


class DuplicatedColumnNameError(ModuleError):
    def __init__(self, duplicated_name: str = None, arg_name: str = None, details: str = None):
        super().__init__(**_valid_kwargs(locals()))


class InvalidUriError(ModuleError):
    def __init__(self, invalid_url):
        super().__init__(invalid_url)


class CouldNotDownloadFileError(ModuleError):
    def __init__(self, file_url):
        super().__init__(file_url)


class TooFewColumnsSelectedError(ModuleError):
    def __init__(self, arg_name: str = None, required_columns_count: int = None):
        valid_params = _exact_valid_parameters(arg_name, required_columns_count)
        super().__init__(*valid_params)


class NaNError(ModuleError):
    def __init__(self, arg_name: str = None):
        valid_params = _exact_valid_parameters(arg_name)
        super().__init__(*valid_params)


class InfinityError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class MoreThanOneRatingError(ModuleError):
    def __init__(self, user: str = None, item: str = None, dataset=None):
        super().__init__(**_valid_kwargs(locals()))


class MissingFeaturesError(ModuleError):
    def __init__(self, required_feature_name=None):
        valid_params = _exact_valid_parameters(required_feature_name)
        super().__init__(*valid_params)


class DuplicateFeatureDefinitionError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class MultipleLabelColumnsError(ModuleError):
    def __init__(self, dataset_name: str = None):
        super().__init__(**_valid_kwargs(locals()))


class InvalidNumberOfElementsError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class FailedToCompleteOperationError(ModuleError):
    def __init__(self, failed_operation: str = None):
        super().__init__(**_valid_kwargs(locals()))


class SingleDeprecationError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class MultipleDeprecationError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class CouldNotConvertColumnError(ModuleError):
    def __init__(self, type1: Union[type, str], type2: Union[type, str],
                 col_name1: str = None, col_name2: str = None):
        valid_params = _exact_valid_parameters(type1, type2, col_name1, col_name2)
        super().__init__(*valid_params)


class MissingEqualsError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class CannotDeriveElementTypeError(ModuleError):
    def __init__(self, column_name: str = None, dataset_name: str = None):
        valid_params = _exact_valid_parameters(column_name, dataset_name)
        super().__init__(*valid_params)


class MixedColumnError(ModuleError):
    def __init__(self, column_id: int = None, row_1: int = None, type_1: type = None, row_2: int = None,
                 type_2: type = None, chunk_id_1: int = None, chunk_id_2: int = None, chunk_size: int = None):
        super().__init__(**_valid_kwargs(locals()))


class InvalidPathForDirectoryCreationError(ModuleError):
    def __init__(self, path_name):
        super().__init__(path_name)


class TooFewFeatureColumnsInDatasetError(ModuleError):
    def __init__(self, required_columns_count: int = None, arg_name: str = None):
        super().__init__(**_valid_kwargs(locals()))


class CouldNotOpenFileError(ModuleError):
    def __init__(self, file_name, exception=None):
        valid_params = _exact_valid_parameters(file_name, exception)
        super().__init__(*valid_params)


class FileParsingFailedError(ModuleError):
    def __init__(self, file_format, file_name=None, failure_reason=None):
        super().__init__(**_valid_kwargs(locals()))


class EqualInputOutputFilesError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class EqualOutputFilesError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class IncorrectAzureStorageKeyError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class NoUserFeaturesOrItemsFoundError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class TooFewDistinctValuesInColumnError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class DeprecationNoReplacementError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class InvalidColumnCategorySelectedError(ModuleError):
    def __init__(self, col_name: str = None):
        super().__init__(**_valid_kwargs(locals()))


class AlreadyExistsError(ModuleError):
    def __init__(self, file_path):
        super().__init__(file_path)


class NotExpectedLabelColumnError(ModuleError):
    def __init__(self, dataset_name: str = None, column_name: str = None, reason: str = None):
        super().__init__(**_valid_kwargs(locals()))


class ColumnIndexParsingError(ModuleError):
    def __init__(self, column_index_or_range):
        super().__init__(column_index_or_range)


class InvalidColumnIndexRangeError(ModuleError):
    def __init__(self, column_range):
        super().__init__(column_range)


class ColumnCountNotEqualError(ModuleError):
    def __init__(self, chunk_id_1=None, chunk_id_2=None, chunk_size=None,
                 filename_1=None, filename_2=None, column_count_1=None, column_count_2=None):
        super().__init__(**_valid_kwargs(locals()))


class FailedToEvaluateRScriptError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class LearnerTypesNotCompatibleError(ModuleError):
    def __init__(self, actual_learner_type=None, expected_learner_type_list=None):
        super().__init__(**_valid_kwargs(locals()))


class IncorrectAzureStorageOrKeyError(ModuleError):
    def __init__(self, account_name=None):
        super().__init__(**_valid_kwargs(locals()))


class IncorrectAzureBlobNameError(ModuleError):
    def __init__(self, blob_name=None, blob_name_prefix=None, container_name=None, blob_wildcard_path=None):
        super().__init__(**_valid_kwargs(locals()))


class UnableToUploadToAzureBlobError(ModuleError):
    def __init__(self, source_path, dest_path):
        super().__init__(source_path, dest_path)


class UnexpectedNumberOfColumnsError(ModuleError):
    def __init__(self, dataset_name: str = None, expected_column_count: int = None, actual_column_count: int = None):
        super().__init__(**_valid_kwargs(locals()))


class InvalidHiveScriptError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class InvalidSQLScriptError(ModuleError):
    def __init__(self, sql_query, exception=None):
        valid_params = _exact_valid_parameters(sql_query, exception)
        super().__init__(*valid_params)


class AzureTableNotExistError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class InvalidCredentialsError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class TimeoutOccuredError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class ErrorConvertingColumnError(ModuleError):
    def __init__(self, target_type=None):
        valid_params = _exact_valid_parameters(target_type)
        super().__init__(*valid_params)


class ErrorConvertingSparseToCategoricalError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(ErrorId.ErrorConvertingSparseToCategorical,
                         *parameters)


class InvalidBinningFunctionError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class UnsupportedBlobWriteModeError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class HttpRedirectionNotAllowedError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class IncorrectAzureContainerError(ModuleError):
    def __init__(self, container_name):
        super().__init__(container_name)


class ColumnWithAllMissingsError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class PCASparseDatasetWrongDimensionsNumberError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(ErrorId.PCASparseDatasetWrongDimensionsNumber,
                         *parameters)


class UnableToDeserializeModelError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class InvalidTrainingDatasetError(ModuleError):
    def __init__(self, data_name=None, learner_type=None, reason=None):
        valid_params = _exact_valid_parameters(data_name, learner_type, reason)
        super().__init__(*valid_params)


class UnableToEvaluateCustomModelError(ModuleError):
    def __init__(self):
        super().__init__(ErrorId.UnableToEvaluateCustomModel)


class FailedToEvaluateScriptError(ModuleError):
    def __init__(self, script_language, message):
        super().__init__(**_valid_kwargs(locals()))


class InvalidCountingTransformError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class InvalidCountTableTypeError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class InvalidCountingTypeError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class IncorrectNumberOfClassesError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class FailedToCreateHiveTableError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class UnsupportedCustomModuleLanguageError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class NonUniqueIDsError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class InvalidZipFileError(ModuleError):
    def __init__(self):
        super().__init__(ErrorId.InvalidZipFile)


class NoModuleDefinitionFilesFoundError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class RLanguageScriptNotFoundError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class UnsupportedParameterTypeError(ModuleError):
    def __init__(self, parameter_name=None, reason=None):
        super().__init__(**_valid_kwargs(locals()))


class UnsupportedInputTypeError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class UnsupportedOutputTypeError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class ExceedSupportedPortCountError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class ColumnPickerUnsupportedSyntaxError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class ColumnPickerPortIdNotFoundError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class InvalidPropertyDefinitionError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class InvalidModuleDefinitionFileError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class ErrorsInModuleDefinitionFileError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class BuildCustomModuleFailedError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class UnableToWriteError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class MultipleWeightColumnsError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class ColumnOfVectorsLabelFailedError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class NonNumericWeightColumnError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class SchemaDoesNotMatchError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class UnsupportedDomainError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class ImageExceedsLimitError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class NumberOfUnconditionalProbabilitiesExceedsLimitError(ModuleError):
    def __init__(self, *parameters):
        super() \
            .__init__(*parameters)


class ExceedsColumnLimitError(ModuleError):
    def __init__(self, dataset_name: str = None, limit_columns_count: int = None, component_name: str = None):
        super().__init__(**_valid_kwargs(locals()))


class AllRowsInTrainingDatasetContainMissingValuesError(ModuleError):
    def __init__(self, *parameters):
        super() \
            .__init__(*parameters)


class UnzipDatasetsFailedError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class UnpackMultipleFilesFoundError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class UnpackDatasetNotFoundError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class LabelColumnDoesNotHaveLabeledPointsError(ModuleError):
    def __init__(self, required_rows_count: int = None, dataset_name: str = None):
        super().__init__(**_valid_kwargs(locals()))


class UnsupportedClusterError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class NoFileNameFoundError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class AzureTableConversionError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class ModuleOutOfMemoryError(ModuleError):
    def __init__(self, details: str = None):
        valid_kwargs = _valid_kwargs(locals())
        super().__init__(**valid_kwargs)


class CouldNotConvertColumnRowError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class OnlyLabelColumnSelectedError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class NotEnoughNormalizedColumnsError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class CannotLoadCertError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class NotGitHubURLError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class GitHubURLWrongTreeError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class ReplicationDirectoryIssueError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class PathTooLongError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class GitHubAccessError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class UnableExtractDataError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class GithubFileNotFoundError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class UnableUnzipWithGithubError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class CloudStorageWriteErrorError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class BadStorageEndPointError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class BadAzureCloudTypeError(ModuleError):
    def __init__(self, *parameters):
        super().__init__(*parameters)


class JoinOnIncompatibleColumnTypesError(ModuleError):
    def __init__(self, keys_left: str = None, keys_right: str = None):
        valid_kwargs = _valid_kwargs(locals())
        super().__init__(**valid_kwargs)


class ColumnNamesNotStringError(ModuleError):
    def __init__(self, column_names: list = None):
        valid_kwargs = _valid_kwargs(locals())
        super().__init__(**valid_kwargs)


class FailedToReadAzureSQLDatabaseError(ModuleError):
    def __init__(self, database_server_name: str = None, database_name: str = None,
                 sql_statement: str = None, detailed_message: str = None):
        valid_kwargs = _valid_kwargs(locals())
        super().__init__(**valid_kwargs)


class IncorrectAzureMLDatastoreError(ModuleError):
    def __init__(self,
                 datastore_name: str = None, workspace_name: str = None,
                 ):
        valid_kwargs = _valid_kwargs(locals())
        super().__init__(**valid_kwargs)


class LibraryExceptionError(ModuleError):
    def __init__(self, exception, customer_support_guidance=None):
        valid_params = _exact_valid_parameters(exception, customer_support_guidance)
        super().__init__(*valid_params)


class ErrorMapping:

    @classmethod
    def throw(cls, err: ModuleError):
        raise err

    @classmethod
    def rethrow(cls, e: BaseException, err: ModuleError):
        if isinstance(e, ModuleError):
            cls.throw(e)

        raise err from e

    @classmethod
    def verify_not_null_or_empty(cls, x: Union[str, any], name: str = None):
        def _throw():
            cls.throw(NullOrEmptyError(name))

        if isinstance(x, str):
            if is_null_or_empty(x):
                _throw()
        else:
            if x is None:
                _throw()

    @classmethod
    def verify_value_in_range(cls, value, lower_bound, upper_bound, arg_name: str = None, lower_inclusive=True,
                              upper_inclusive=True):
        if lower_inclusive:
            throw_exception = value < lower_bound
        else:
            throw_exception = value <= lower_bound

        if not throw_exception:
            if upper_inclusive:
                throw_exception = value > upper_bound
            else:
                throw_exception = value >= upper_bound

        if throw_exception:
            cls.throw(NotInRangeValueError(arg_name, lower_bound, upper_bound))

    @classmethod
    def verify_less_than(cls, value, b, arg_name: str = None):
        if value >= b:
            cls.throw(LessThanError(arg_name, b))

    @classmethod
    def verify_less_than_or_equal_to(cls, value, b, arg_name: str = None):
        if value > b:
            cls.throw(LessThanOrEqualToError(arg_name, b))

    @classmethod
    def verify_greater_than(cls, value, b, arg_name: str = None):
        if value <= b:
            cls.throw(GreaterThanError(arg_name, b))

    @classmethod
    def verify_greater_than_or_equal_to(cls, value, b, arg_name: str = None):
        if value < b:
            cls.throw(GreaterThanOrEqualToError(arg_name, b))

    @classmethod
    def verity_sizes_are_consistent(cls, size1: int, size2: int,
                                    friendly_name1: str = None, friendly_name2: str = None):
        if size1 != size2:
            cls.throw(InconsistentSizeError(friendly_name1, friendly_name2))

    @classmethod
    def verify_number_of_rows_greater_than_or_equal_to(cls, curr_row_count: int, required_row_count: int,
                                                       arg_name: str = None):
        if curr_row_count < required_row_count:
            cls.throw(TooFewRowsInDatasetError(arg_name, required_row_count, curr_row_count))

    @classmethod
    def verify_number_of_columns_greater_than_or_equal_to(cls, curr_column_count: int, required_column_count: int,
                                                          arg_name: str = None):
        if curr_column_count < required_column_count:
            cls.throw(TooFewColumnsInDatasetError(arg_name, required_column_count))

    @classmethod
    def verify_number_of_columns_equal_to(cls, curr_column_count: int, required_column_count: int,
                                          arg_name: str = None):
        if curr_column_count != required_column_count:
            cls.throw(UnexpectedNumberOfColumnsError(arg_name, required_column_count, curr_column_count))

    @classmethod
    def verify_number_of_columns_less_than_or_equal_to(cls, curr_column_count: int, required_column_count: int,
                                                       arg_name: str = None):
        if curr_column_count > required_column_count:
            cls.throw(UnexpectedNumberOfColumnsError(dataset_name=arg_name))

    @classmethod
    def verify_amount_of_feature_columns(cls, curr_columns_count: int, required_columns_count: int,
                                         arg_name: str = None):
        if curr_columns_count < required_columns_count:
            cls.throw(TooFewFeatureColumnsInDatasetError(required_columns_count, arg_name))

    @classmethod
    def verify_if_all_columns_selected(cls, act_col_count: int, exp_col_count: int,
                                       selection_pattern_friendly_name: str = None, long_description: bool = False):
        if act_col_count != exp_col_count:
            if long_description:
                cls.throw(BadNumberOfSelectedColumnsError(
                    selection_pattern_friendly_name, exp_col_count, act_col_count))
            else:
                cls.throw(BadNumberOfSelectedColumnsError(selection_pattern_friendly_name, exp_col_count))

    @classmethod
    def verify_are_columns_selected(cls, curr_selected_num: int, required_selected_num: int, arg_name: str = None):
        if curr_selected_num < required_selected_num:
            cls.throw(NoColumnsSelectedError(arg_name))

    @classmethod
    def verify_column_names_are_string(cls, column_names: list):
        not_string_col_names = [col_name for col_name in column_names if not isinstance(col_name, str)]
        if not_string_col_names:
            cls.throw(ColumnNamesNotStringError(column_names=not_string_col_names))

    @classmethod
    def verify_element_type(cls, type_: str, expected_type: str, column_name: str = None, arg_name: str = None):
        """ Verify the DataTable element type of {column_name} column is expected_type.

        :param type_: an element type of dataset column
        :param expected_type: expected element type
        :param column_name: opt, corresponding column name
        :param arg_name: opt, friendly name of the corresponding argument.
        :return:
        """
        if type_ != expected_type:
            cls.throw_invalid_column_type(type_, column_name, arg_name)

    @classmethod
    def convert_to_module_exception(cls, eid, *parameters):
        return ModuleError(eid, *parameters)

    @classmethod
    def throw_invalid_column_type(
            cls, type_: str = None, column_name: str = None, arg_name: str = None):
        if not type_:
            cls.throw(InvalidColumnTypeError())
        elif (not column_name) and (not arg_name):
            cls.throw(InvalidColumnTypeError(type_))
        elif not arg_name:
            cls.throw(InvalidColumnTypeError(type_, column_name))
        else:
            cls.throw(InvalidColumnTypeError(type_, column_name, arg_name))

    @classmethod
    def get_exception_message(cls, ex: Exception):
        message = ex.__str__()
        if not message:
            message = ex.__repr__()
        return message


def _exact_valid_parameters(*parameters):
    valid_params = list()
    for param in parameters:
        if isinstance(param, str) and not is_null_or_whitespace(param):
            valid_params.append(param)
        elif param is not None:
            valid_params.append(param)
        else:
            break
    return valid_params


def _valid_kwargs(kwargs):
    # incoming 'kwargs' param value are expected to come from `locals()` in subclass `__init__` functions.
    # return value are expected to be passed to `super().__init__()` function.
    #
    # for incoming kwargs pre processing,
    #  1) 'self' should be excluded otherwise will cause duplicate 'self' params error
    #  2) items with `None` value should be excluded
    frame = inspect.currentframe().f_back
    if frame.f_code.co_name != '__init__':
        raise ValueError(f"_valid_kwargs is supposed to be called directly in Error class's __init__ function")

    valid_kwargs = {k: kwargs.get(k) for k in frame.f_code.co_varnames
                    if k != 'self' and kwargs.get(k) is not None}
    return valid_kwargs
