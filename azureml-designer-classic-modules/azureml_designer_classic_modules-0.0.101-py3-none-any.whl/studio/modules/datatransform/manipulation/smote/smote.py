import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTENC, SMOTE

import azureml.studio.common.utils.datetimeutils as datetimeutils
from azureml.studio.common.datatable.data_table import DataTable, DataTableColumnSelection
from azureml.studio.common.error import ErrorMapping, NotExpectedLabelColumnError, NotInRangeValueError, \
    FailedToCompleteOperationError, InvalidDatasetError, LessThanOrEqualToError, UnexpectedNumberOfColumnsError, \
    TooFewFeatureColumnsInDatasetError
from azureml.studio.core.logger import module_logger, TimeProfile
from azureml.studio.modulehost.attributes import ModuleMeta, ReleaseState, DataTableInputPort, \
    ColumnPickerParameter, DefaultColumnCategory, SelectedColumnCategory, IntParameter, DataTableOutputPort
from azureml.studio.modulehost.constants import ElementTypeName
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule


class SMOTEModule(BaseModule):
    @staticmethod
    @module_entry(
        ModuleMeta(
            name="SMOTE",
            description="Increases the number of low incidence examples in a dataset",
            category="Data Transformation\\Manipulation",
            version="2.0",
            owner="Microsoft Corporation",
            family_id="9F3FE1C4-520E-49AC-A152-2E104169912A",
            release_state=ReleaseState.Beta,
            is_deterministic=True,
        ))
    def run(
            samples: DataTableInputPort(
                name="Samples",
                friendly_name="Samples",
                description="A DataTable of samples",
            ),
            label_column_index_or_name: ColumnPickerParameter(
                name="Label column",
                friendly_name="Label column",
                description="Select the column that contains the label or outcome column",
                default_value=DefaultColumnCategory.AllLabel,
                column_picker_for="Samples",
                single_column_selection=True,
                column_selection_categories=(SelectedColumnCategory.All,),
            ),
            smote_percent: IntParameter(
                name="SMOTE percentage",
                friendly_name="SMOTE percentage",
                description="Amount of oversampling."
                            "If not in integral multiples of 100, "
                            "the minority class will be randomized and downsampled "
                            "from the next integral multiple of 100.",
                default_value=100,
                min_value=0,
            ),
            neighbors: IntParameter(
                name="Number of nearest neighbors",
                friendly_name="Number of nearest neighbors",
                description="The number of nearest neighbors",
                default_value=1,
                min_value=1,
            ),
            seed: IntParameter(
                name="Random seed",
                friendly_name="Random seed",
                description="Random number generator seed",
                default_value=0,
            )
    ) -> (
            DataTableOutputPort(
                name="Table",
                friendly_name="Results dataset",
                description="A DataTable containing original samples "
                            "plus an additional synthetic minority class samples, "
                            "where T is the number of minority class samples",
            ),
    ):
        input_values = locals()
        return SMOTEModule._run_impl(**input_values)

    @classmethod
    def _check_label_column(cls, label_column: DataTable):
        """Check the label column in data table

        1.SMOTE only accepts binary labels
        2.The label column num must be one
        :param label_column: input label data
        :return: None
        """
        actual_label_column_count = label_column.number_of_columns
        if actual_label_column_count != 1:
            ErrorMapping.throw(
                UnexpectedNumberOfColumnsError(
                    expected_column_count=1,
                    actual_column_count=actual_label_column_count))

        label_type_required = 2
        label_column_name = label_column.column_names[0]
        label_to_num_df = label_column.data_frame.groupby(label_column_name).count()

        if label_to_num_df.shape[0] != label_type_required:
            ErrorMapping.throw(
                NotExpectedLabelColumnError(
                    dataset_name=cls._args.samples.friendly_name,
                    reason='SMOTE only accepts binary labels.'))

    @classmethod
    def _check_no_missing_value(cls, data_set: DataTable):
        if data_set.has_na():
            ErrorMapping.throw(InvalidDatasetError(
                dataset1=cls._args.samples.friendly_name,
                invalid_data_category='missing value',
                troubleshoot_hint="Consider using the Clean Missing Data module to remove missing values."))

    @classmethod
    def _normalize_date_columns(cls, dataset: DataTable):
        for column_name in dataset.column_names:
            if dataset.get_element_type(column_name) in (ElementTypeName.TIMESPAN, ElementTypeName.DATETIME):
                dataset.set_column(column_name,
                                   datetimeutils.convert_to_ns(dataset.get_column(col_key=column_name)))
        return dataset

    @classmethod
    def _get_categorical_column_list(cls, data_set: DataTable, column_to_exclude):
        """Get the categorical feature columns list of the input dataset.

        Due to the known limitation of SMOTE and SMOTENC, all categorical dataset could not be handled.
        :param data_set: input data set
        :param column_to_exclude: selected label column name, which would be excluded from the result.
        :return: a list of indices specifying the categorical features;
        Raise error if all feature columns are categorical.
        """
        column_names = [x for x in data_set.column_names if x != column_to_exclude]
        categorical_column_list = [i for i, n in enumerate(column_names) if
                                   data_set.get_element_type(n) not in ElementTypeName.NUMERIC_LIST]
        if len(column_names) == len(categorical_column_list):
            ErrorMapping.throw(FailedToCompleteOperationError(
                failed_operation="Performing SMOTE on dataset, "
                                 "the input dataset should contain at least one numerical feature column. "))
        return categorical_column_list

    @classmethod
    def _run_impl(cls, samples: DataTable,
                  label_column_index_or_name: DataTableColumnSelection,
                  smote_percent: int = None,
                  neighbors: int = None, seed: int = None):

        # Table cannot be empty
        ErrorMapping.verify_number_of_rows_greater_than_or_equal_to(curr_row_count=samples.number_of_rows,
                                                                    required_row_count=1,
                                                                    arg_name=cls._args.samples.friendly_name)
        # Check the label column
        label_column = label_column_index_or_name.select(samples)
        cls._check_label_column(label_column)
        label_column_index = label_column_index_or_name.select_column_indexes(samples)
        label_column_name = samples.get_column_name(label_column_index[0])

        # Dataset could not contain any missing value.
        cls._check_no_missing_value(samples)
        # Convert all date time and time span column to ns
        samples = cls._normalize_date_columns(samples)
        # The number of feature columns must be greater than or equal to one
        feature_columns = samples.data_frame.drop(label_column_name, axis=1)
        if feature_columns.shape[1] < 1:
            ErrorMapping.throw(
                TooFewFeatureColumnsInDatasetError(required_columns_count=1, arg_name=cls._args.samples.friendly_name))

        categorical_column_list = cls._get_categorical_column_list(samples, label_column_name)

        # Calculate the number of minority label and the number of majority label
        label_to_num = pd.value_counts(label_column.data_frame[label_column_name])
        small_class_num, large_class_num = min(label_to_num), max(label_to_num)

        # Neighbors should be smaller than the rows num of majority label
        if neighbors > small_class_num - 1:
            expect = small_class_num - 1
            ErrorMapping.throw(
                LessThanOrEqualToError(left_arg_name=cls._args.neighbors.friendly_name,
                                       left_arg_val=neighbors,
                                       right_arg_val=expect))

        # Calculate the ratio of the number of minority label to the number of majority label after smote
        if smote_percent == 0:
            return samples,

        remainder = smote_percent % 100
        expansion_ratio = smote_percent // 100 if remainder == 0 else smote_percent // 100 + 1
        synthetic_ratio = small_class_num * (expansion_ratio + 1) / large_class_num

        if synthetic_ratio > 1:
            ErrorMapping.throw(
                NotInRangeValueError(arg_name=cls._args.smote_percent.friendly_name,
                                     reason='The ratio of the number of samples in the minority class after resampling '
                                            'to the number of samples in the majority class '
                                            'should be in the range (0, 1].'))

        module_logger.info("Create a smote generator.")
        if categorical_column_list:
            # If categorical column list is not empty, SMOTENC algo should be used.
            smote_generator = SMOTENC(categorical_features=np.array(categorical_column_list),
                                      sampling_strategy=synthetic_ratio, random_state=seed,
                                      k_neighbors=neighbors)
        else:
            # If input data does not contain categorical feature,
            # SMOTE algo should be used due to the limitation of SMOTENC algo.
            # It requires that the input data should contain both numerical and categorical features.
            smote_generator = SMOTE(sampling_strategy=synthetic_ratio, random_state=seed,
                                    k_neighbors=neighbors)
        feature_columns_name = feature_columns.columns.values.tolist()
        with TimeProfile("Fit and transform train dataset"):
            new_features_columns, new_label_column = smote_generator.fit_resample(feature_columns, np.array(
                label_column.data_frame[label_column_name]))

        # Concat the feature part and the label part
        new_features_df = pd.DataFrame(new_features_columns, columns=feature_columns_name)
        new_label_df = pd.DataFrame(new_label_column, columns=[label_column_name])
        # In order to improve the user experience, don't change the order of new_label_df and new_features_df
        # Reason: only the visualization results of the first 100 columns can be viewed.
        result_df = pd.concat([new_label_df, new_features_df], axis=1)

        return DataTable(result_df),
