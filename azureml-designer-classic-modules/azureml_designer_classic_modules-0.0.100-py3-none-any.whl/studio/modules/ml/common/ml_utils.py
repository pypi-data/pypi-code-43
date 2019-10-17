import azureml.studio.core.utils.missing_value_utils as missing_value_utils
import pandas as pd
from azureml.studio.core.logger import module_logger
from azureml.studio.core.utils.strutils import profile_column_names

import azureml.studio.modules.ml.common.normalizer as normalizer
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table import DataTableColumnSelection
from azureml.studio.common.error import ErrorMapping, NotCompatibleColumnTypesError
from azureml.studio.common.error import LabelColumnDoesNotHaveLabeledPointsError, InvalidTrainingDatasetError
from azureml.studio.common.error import NotLabeledDatasetError, \
    MultipleLabelColumnsError
from azureml.studio.modulehost.attributes import AutoEnum
from azureml.studio.modulehost.constants import ColumnTypeName
from azureml.studio.modules.ml.common.constants import ScoreColumnConstants


class TaskType(AutoEnum):
    BinaryClassification = ()
    MultiClassification = ()
    Regression = ()
    Cluster = ()


def is_classification_task(task_type):
    if not isinstance(task_type, TaskType):
        raise TypeError('"task_type" should be TaskType.')
    return task_type in {TaskType.BinaryClassification, TaskType.MultiClassification}


def drop_illegal_label_instances(df, column_name, task_type):
    """Drop the illegal instances whose label is nan or invalid.

    :param df: pandas.DataFrame
    :param column_name: str. [specified_column could not be a list, since pd.to_numeric only accept 1-dim arg]
    :param task_type: TaskType
    :return:
    """
    if task_type == TaskType.Cluster:
        # Clustering is an unsupervised algorithm. Do not need to check the labels are legal or not.
        return
    if not isinstance(column_name, str):
        raise TypeError(f"argument 'column_name' expects a string but got a {type(column_name)}.")
    module_logger.info("Remove missing label instances.")
    df.dropna(subset=[column_name], inplace=True)
    if task_type == TaskType.Regression:
        module_logger.info("Regression task, remove instances with non-numeric label.")
        # x.replace(',', '') is used to handle str like '100,000'
        df[column_name] = df[column_name].apply(
            lambda x: x.replace(',', '') if isinstance(x, str) else x)
        drop_index = df.index[pd.to_numeric(df[column_name], errors='coerce').isnull()]
        df.drop(drop_index, inplace=True)
    df.reset_index(drop=True, inplace=True)


def get_incompatible_col_names(test_feature_columns_categorized_by_type, train_feature_columns_categorized_by_type):
    """Get incompatible column names.

    :param test_feature_columns_categorized_by_type: tuple((str_fea_col_name_set, numeric_fea_col_name_set,
    datetime_fea_col_name_set))
    :param train_feature_columns_categorized_by_type: tuple((str_fea_col_name_set, numeric_fea_col_name_set,
    datetime_fea_col_name_set))
    :return: incompatible_col_name_set: set
    """
    incompatible_col_name_set = set()
    for i, test_fea_set in enumerate(test_feature_columns_categorized_by_type):
        incompatible_col_name_set |= (test_fea_set - train_feature_columns_categorized_by_type[i])

    return incompatible_col_name_set


def check_test_data_col_type_compatible(test_x, train_feature_columns_categorized_by_type, setting, task_type):
    """Check whether column type consistent between training and scoring.

    :param test_x: pd.DataFrame
    :param train_feature_columns_categorized_by_type: tuple((str_fea_col_name_set, numeric_fea_col_name_set,
    datetime_fea_col_name_set))
    :param setting: ClassifierSetting
    :param task_type: TaskType
    :return:
    """
    test_normalizer = normalizer.Normalizer()
    test_normalize_number = getattr(setting, 'normalize_features', True)
    test_normalizer.build(
        df=test_x,
        feature_columns=test_x.columns.tolist(),
        label_column_name=None,
        normalize_number=test_normalize_number,
        encode_label=task_type is not TaskType.Regression
    )
    test_feature_columns_categorized_by_type = test_normalizer.feature_columns_categorized_by_type
    module_logger.info(f'Successfully built normalizer of test data.')
    if test_feature_columns_categorized_by_type != train_feature_columns_categorized_by_type:
        incompatible_col_names = ','.join(get_incompatible_col_names(test_feature_columns_categorized_by_type,
                                                                     train_feature_columns_categorized_by_type))
        ErrorMapping.throw(NotCompatibleColumnTypesError(first_col_names=incompatible_col_names))


def check_two_data_tables_col_type_compatible(train_x, validation_x, setting, task_type):
    """Check whether column type consistent between two data tables(e.g. training set and validation set).

    :param train_x: pd.DataFrame, training set
    :param validation_x: pd.DataFrame, validation set.
    :param setting: LearnerSetting
    :param task_type: TaskType
    :return:
    """

    train_normalizer = normalizer.Normalizer()
    train_normalize_number = getattr(setting, 'normalize_features', True)
    train_normalizer.build(
        df=train_x,
        feature_columns=train_x.columns.tolist(),
        label_column_name=None,
        normalize_number=train_normalize_number,
        encode_label=task_type is not TaskType.Regression
    )
    train_feature_columns_categorized_by_type = train_normalizer.feature_columns_categorized_by_type

    check_test_data_col_type_compatible(
        test_x=validation_x,
        train_feature_columns_categorized_by_type=train_feature_columns_categorized_by_type,
        setting=setting, task_type=task_type)


def collect_notna_numerical_feature_instance_row_indexes(data_table, label_column_name=None, include_inf=True):
    """Collect the valid instance indexes

    If an instance does not have nan numerical feature, then we regard it as a valid instance.
    :param data_table: DataTable, training data table.
    :param label_column_name: str or None, name of label column.
    :param include_inf: bool, if True, inf value will be used as nan value.
    :return: pandas index, row indexes of valid instances.
    """
    numeric_feature_column_names = [name for name in data_table.column_names
                                    if data_table.get_column_type(name) == ColumnTypeName.NUMERIC]
    if label_column_name in numeric_feature_column_names:
        numeric_feature_column_names.remove(label_column_name)
    if numeric_feature_column_names:
        is_nan_feature_row = missing_value_utils.df_isnull(df=data_table.data_frame,
                                                           column_names=numeric_feature_column_names,
                                                           include_inf=include_inf)
        valid_row_indexes = is_nan_feature_row[~is_nan_feature_row].index
        return valid_row_indexes
    else:
        return data_table.data_frame.index


def append_predict_result(data_table: DataTable, predict_df, valid_row_indexes=None):
    dup_column_names = [x for x in predict_df.columns.tolist() if x in data_table.column_names]
    # If index is not specified, all rows are used.
    if valid_row_indexes is None:
        valid_row_indexes = predict_df.index
    if dup_column_names:
        # Fixes the bug that when scored data is passed to score module, the column name will be duplicated.
        module_logger.warning(f"Found the score columns in the input data, "
                              f"Columns {','.join(dup_column_names)} will be overwritten")

        result_df = data_table.data_frame
        for column in predict_df.columns.tolist():
            result_df.loc[valid_row_indexes, column] = predict_df[column]
    else:
        result_df = pd.concat([data_table.data_frame, predict_df], axis=1)
    return result_df


def _filter_column_names_with_prefix(name_list, prefix=''):
    # if prefix is '', all string.startswith(prefix) is True.
    if prefix == '':
        return name_list
    return [column_name for column_name in name_list if column_name.startswith(prefix)]


def generate_score_column_meta(task_type, predict_df):
    """Build score_column_names dict according to the task type

    Binary Classification
        Map BinaryClassScoredLabelType to ScoredLabelsColumnName
        Map CalibratedScoreType To ScoredProbabilitiesColumnName
    Multi Classification
        Map MultiClassScoredLabelType to ScoredLabelsColumnName
        Map ScoredProbabilitiesMulticlassColumnTypePattern_X to
            ScoredProbabilitiesMulticlassColumnTypePattern_X FOR EVERY CLASS X
    Regression
        Map RegressionScoredLabelType to ScoredLabelsColumnName
    Custom defined model
        map column name to column name
    When evaluating the scored data, infer the task task with the {TaskType}ScoreLabelType key.

    :param task_type: TaskType Enum
    :param predict_df: the predict result dataframe. Now, it is not used when task_type is binary classification
     or regression. Will be used in all cases after supporting concatenate score columns.
    :return: built score column names dict
    """

    score_columns = {}
    if task_type == TaskType.BinaryClassification:
        score_columns[ScoreColumnConstants.BinaryClassScoredLabelType] = ScoreColumnConstants.ScoredLabelsColumnName
        score_columns[ScoreColumnConstants.CalibratedScoreType] = ScoreColumnConstants.ScoredProbabilitiesColumnName
        module_logger.info("Binary Classification Model Scored Columns are: ")
    elif task_type == TaskType.MultiClassification:
        score_columns = {x: x for x in _filter_column_names_with_prefix(
            predict_df.columns.tolist(), prefix=ScoreColumnConstants.ScoredProbabilitiesMulticlassColumnNamePattern)}
        score_columns[ScoreColumnConstants.MultiClassScoredLabelType] = ScoreColumnConstants.ScoredLabelsColumnName
        module_logger.info("Multi-class Classification Model Scored Columns are: ")
    elif task_type == TaskType.Regression:
        score_columns[ScoreColumnConstants.RegressionScoredLabelType] = ScoreColumnConstants.ScoredLabelsColumnName
        module_logger.info("Regression Model Scored Columns: ")
    elif task_type == TaskType.Cluster:
        score_columns = {x: x for x in _filter_column_names_with_prefix(
            predict_df.columns.tolist(), prefix=ScoreColumnConstants.ClusterDistanceMetricsColumnNamePattern)}
        score_columns[ScoreColumnConstants.ClusterScoredLabelType] = ScoreColumnConstants.ClusterAssignmentsColumnName
        module_logger.info("Cluster Model Assigned Columns: ")
    else:
        # Custom defined python model, map column name to column name now.
        score_columns = {x: x for x in predict_df.columns.tolist()}
        module_logger.info("Custom Defined Module Scored Columns are: ")
    module_logger.info(
        f'There are {len(score_columns.keys())} score columns: "{profile_column_names(list(score_columns.keys()))}"')
    return score_columns


def get_label_column_name(training_data: DataTable, column_selection: DataTableColumnSelection, dataset_name):
    label_column_index = column_selection.select_column_indexes(training_data)
    if len(label_column_index) == 0:
        ErrorMapping.throw(NotLabeledDatasetError(dataset_name=dataset_name))
    elif len(label_column_index) > 1:
        ErrorMapping.throw(MultipleLabelColumnsError(dataset_name=dataset_name))
    label_column_name = training_data.column_names[label_column_index[0]]
    return label_column_name


def validate_training_label(data_table: DataTable, label_column_name, task_type, data_name):
    case_count = data_table.number_of_rows
    if data_table.get_number_of_missing_value(label_column_name) == case_count:
        ErrorMapping.throw(LabelColumnDoesNotHaveLabeledPointsError(required_rows_count=1))
    if task_type == TaskType.Regression:
        # Regression label should be numeric.
        if data_table.get_column_type(label_column_name) != ColumnTypeName.NUMERIC:
            ErrorMapping.throw(InvalidTrainingDatasetError(
                data_name=data_name,
                learner_type="Regression model",
                reason="Regression model cannot accept non-numeric label column"))
    elif task_type == TaskType.BinaryClassification:
        # For a binary classification task, the label column should contain two categories label.
        label_series = data_table.get_column(label_column_name)
        categories = set(label_series[label_series.notna()].tolist())
        if len(categories) != 2:
            ErrorMapping.throw(InvalidTrainingDatasetError(
                data_name=data_name,
                learner_type="Binary classifier",
                reason=f'The number of label classes should equal to 2, got {len(categories)} classes'))
    elif task_type == TaskType.MultiClassification:
        # For a multi-class classification task, the label column should contain more than 1 categories.
        label_series = data_table.get_column(label_column_name)
        categories = set(label_series[label_series.notna()].tolist())
        if len(categories) < 2:
            ErrorMapping.throw(InvalidTrainingDatasetError(
                data_name=data_name,
                learner_type="Multi-class classifier",
                reason=f'The number of label classes should > 1, got {len(categories)} classes'))
    # Do not check other task_type (Cluster or None).
    # Cluster does not need training label.
    # None means that the learner is a Custom Model, we does not know the requirement,
    # users need to check the data themselves
