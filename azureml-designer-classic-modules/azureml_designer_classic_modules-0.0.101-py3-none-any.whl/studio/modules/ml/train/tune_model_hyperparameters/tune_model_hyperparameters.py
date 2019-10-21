import azureml.studio.modules.ml.common.ml_utils as ml_utils
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table import DataTableColumnSelection
from azureml.studio.common.error import TooFewColumnsInDatasetError, ErrorMapping, \
    NotExpectedLabelColumnError, LearnerTypesNotCompatibleError, ColumnNotFoundError
from azureml.studio.common.input_parameter_checker import InputParameterChecker
from azureml.studio.modulehost.attributes import ModuleMeta, ReleaseState, UntrainedLearnerInputPort, \
    DataTableInputPort, DataTableOutputPort, ColumnPickerParameter, SelectedColumnCategory, \
    ILearnerOutputPort, ModeParameter, IntParameter
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.ml.common.base_learner import BaseLearner
from azureml.studio.modules.ml.common.learner_parameter_sweeper import (
    SweepMethods, BinaryClassificationMetricType, RegressionMetricType,
    LearnerParameterSweeperSetting, LearnerParameterSweeper
)


class TuneModelHyperParametersModule(BaseModule):
    DefaultNumberOfFolds = 3  # Default number of folds before scikit-learn v0.22, will change from 3 to 5 in v0.22.

    @staticmethod
    @module_entry(ModuleMeta(
        name="Tune Model Hyperparameters",
        description="Perform a parameter sweep on the model to determine the optimum parameter settings.",
        category="Machine Learning\\Train",
        version="1.0",
        owner="Microsoft Corporation",
        family_id="038D91B6-C2F2-42A1-9215-1F2C20ED1B40",
        release_state=ReleaseState.Beta,
        is_deterministic=True,
    ))
    def run(
            predictor: UntrainedLearnerInputPort(
                name="Untrained model",
                friendly_name="Untrained model",
                description="Untrained model for parameter sweep",
            ),
            train_data: DataTableInputPort(
                name="Training dataset",
                friendly_name="Training dataset",
                description="Input dataset for training",
            ),
            validation_data: DataTableInputPort(
                name="Validation dataset",
                friendly_name="Optional validation dataset",
                is_optional=True,
                description="Input dataset for validation (for Train/Test validation mode)",
            ),
            sweeping_mode: ModeParameter(
                SweepMethods,
                name="Specify parameter sweeping mode",
                friendly_name="Specify parameter sweeping mode",
                description="Sweep entire grid on parameter space, or sweep with using a limited number of sample runs",
                default_value=SweepMethods.RandomSweep,
            ),
            max_num_of_runs: IntParameter(
                name="Maximum number of runs on random sweep",
                friendly_name="Maximum number of runs on random sweep",
                description="Execute maximum number of runs using random sweep",
                default_value=5,
                parent_parameter="Specify parameter sweeping mode",
                parent_parameter_val=(SweepMethods.RandomSweep,),
                min_value=1,
                max_value=10000,
            ),
            random_seed: IntParameter(
                name="Random seed",
                friendly_name="Random seed",
                description="Provide a value to seed the random number generator",
                default_value=0,
                parent_parameter="Specify parameter sweeping mode",
                parent_parameter_val=(SweepMethods.RandomSweep,),
            ),
            max_num_of_runs1: IntParameter(
                name="Maximum number of runs on random grid",
                friendly_name="Maximum number of runs on random grid",
                description="Execute maximum number of runs using random grid",
                default_value=5,
                parent_parameter="Specify parameter sweeping mode",
                parent_parameter_val=(SweepMethods.RandomGrid,),
                min_value=1,
                max_value=10000,
                release_state=ReleaseState.Alpha
            ),
            random_seed1: IntParameter(
                name="Random seed for random grid",
                friendly_name="Random seed",
                description="Provide a value to seed the random number generator for random grid",
                default_value=0,
                parent_parameter="Specify parameter sweeping mode",
                parent_parameter_val=(SweepMethods.RandomGrid,),
                release_state=ReleaseState.Alpha
            ),
            label_column_index_or_name: ColumnPickerParameter(
                name="Name or numerical index of the label column",
                friendly_name="Label column",
                description="Label column",
                column_picker_for="Training dataset",
                single_column_selection=True,
                column_selection_categories=(SelectedColumnCategory.All,),
            ),
            binary_classification_metric: ModeParameter(
                BinaryClassificationMetricType,
                name="Metric for measuring performance for classification",
                friendly_name="Metric for measuring performance for classification",
                description="Select the metric used for evaluating classification models",
                default_value=BinaryClassificationMetricType.Accuracy,
            ),
            regression_metric: ModeParameter(
                RegressionMetricType,
                name="Metric for measuring performance for regression",
                friendly_name="Metric for measuring performance for regression",
                description="Select the metric used for evaluating regression models",
                default_value=RegressionMetricType.MeanAbsoluteError,
            )
    ) -> (
            DataTableOutputPort(
                name="Sweep results",
                friendly_name="Sweep results",
                description="Results metric for parameter sweep runs",
            ),
            ILearnerOutputPort(
                name="Trained best model",
                friendly_name="Trained best model",
                description="Model with best performance on the training dataset",
            ),
    ):
        input_values = locals()
        output_values = TuneModelHyperParametersModule.tune_model_hyperparameter(**input_values)
        return output_values

    @classmethod
    def _validate_predictor(cls, predictor):
        _support_task_type = (
            ml_utils.TaskType.BinaryClassification, ml_utils.TaskType.MultiClassification, ml_utils.TaskType.Regression)
        task_type = predictor.task_type
        if task_type not in _support_task_type:
            ErrorMapping.throw(LearnerTypesNotCompatibleError(
                actual_learner_type=task_type.name if task_type else 'None',
                expected_learner_type_list=str(_support_task_type)
            ))

    @classmethod
    def _validate_data_set(cls, data_set, task_type, dataset_name, label_column_index_or_name=None,
                           label_column_name=None):
        InputParameterChecker.verify_data_table(data_table=data_set, friendly_name=dataset_name)
        if label_column_name is None:
            label_column_name = ml_utils.get_label_column_name(training_data=data_set,
                                                               column_selection=label_column_index_or_name,
                                                               dataset_name=dataset_name)
        if data_set.number_of_columns < 2:
            ErrorMapping.throw(TooFewColumnsInDatasetError(arg_name=dataset_name, required_columns_count=2))
        ml_utils.validate_training_label(data_set, label_column_name, task_type, dataset_name)

    @classmethod
    def _validate_validation_data_table(cls, train_data: DataTable, label_column_name, task_type, setting,
                                        validation_data: DataTable):
        cls._validate_data_set(data_set=validation_data, label_column_name=label_column_name, task_type=task_type,
                               dataset_name=cls._args.validation_data.friendly_name)
        # validate if the column types are consistent.
        missing_columns = [column_name for column_name in train_data.column_names if
                           column_name not in validation_data.column_names]
        if missing_columns:
            ErrorMapping.throw(ColumnNotFoundError(column_id=','.join(missing_columns),
                                                   arg_name_missing_column=cls._args.validation_data.friendly_name,
                                                   arg_name_has_column=cls._args.train_data.friendly_name))

        ml_utils.check_two_data_tables_col_type_compatible(train_data.data_frame, validation_data.data_frame,
                                                           setting=setting, task_type=task_type)
        if ml_utils.is_classification_task(task_type=task_type):
            # validate if the validate_data's label column is a subset of the train_data's
            train_label_column = train_data.get_column(label_column_name)
            validation_label_column = validation_data.get_column(label_column_name)

            train_label_set = set(train_label_column[train_label_column.notna()])
            validation_label_set = set(validation_label_column[validation_label_column.notna()])
            if validation_label_set - train_label_set:
                ErrorMapping.throw(NotExpectedLabelColumnError(
                    dataset_name=cls._args.validation_data.friendly_name,
                    reason="Validation label column is not consistent with the training label column."))

    @classmethod
    def _validate_full_data_table(cls, train_data: DataTable, label_column_name: str, task_type: ml_utils.TaskType):
        """ When validation data is not provided, validate if K-Fold cross validation could be applied on the train data

        For the Regression task, the DefaultNumberOfFolds cannot greater than the number of non-missing label instances
        For the classification task, the DefaultNumberOfFolds cannot be greater than the number of members in each class
        """
        if ml_utils.is_classification_task(task_type):
            label_members = train_data.get_column(label_column_name).value_counts()  # nan will be dropped
            # The returned label_members is sorted, so check the last element.
            if label_members.iloc[-1] < cls.DefaultNumberOfFolds:
                ErrorMapping.throw(NotExpectedLabelColumnError(
                    dataset_name=cls._args.train_data.friendly_name,
                    reason=f"{cls._args.validation_data.friendly_name} is empty, {cls.DefaultNumberOfFolds}-Fold "
                           f"validation would be applied. The number of members in each class "
                           f"should greater than {cls.DefaultNumberOfFolds}."))
        else:
            non_missing_number = train_data.number_of_rows - train_data.get_number_of_missing_value(label_column_name)
            if non_missing_number < cls.DefaultNumberOfFolds:
                ErrorMapping.throw(NotExpectedLabelColumnError(
                    dataset_name=cls._args.train_data.friendly_name,
                    reason=f"{cls._args.validation_data.friendly_name} is empty, {cls.DefaultNumberOfFolds}-Fold "
                           f"validation would be applied. "
                           f"The number of labeled instances should be greater than {cls.DefaultNumberOfFolds}"))

    @classmethod
    def tune_model_hyperparameter(cls, predictor: BaseLearner, train_data: DataTable,
                                  sweeping_mode: SweepMethods,
                                  label_column_index_or_name: DataTableColumnSelection,
                                  binary_classification_metric: BinaryClassificationMetricType,
                                  regression_metric: RegressionMetricType,
                                  validation_data: DataTable = None,
                                  max_num_of_runs: int = None,
                                  max_num_of_runs1: int = None,
                                  random_seed: int = None,
                                  random_seed1: int = None,
                                  ):
        cls._validate_predictor(predictor)

        task_type = predictor.task_type
        cls._validate_data_set(data_set=train_data, label_column_index_or_name=label_column_index_or_name,
                               task_type=task_type, dataset_name=cls._args.train_data.friendly_name)
        label_column_name = ml_utils.get_label_column_name(training_data=train_data,
                                                           column_selection=label_column_index_or_name,
                                                           dataset_name=cls._args.train_data.friendly_name)
        train_df = train_data.data_frame
        # check validation data
        if validation_data is not None:
            cls._validate_validation_data_table(train_data=train_data, validation_data=validation_data,
                                                label_column_name=label_column_name, task_type=task_type,
                                                setting=predictor.setting
                                                )
            valid_df = validation_data.data_frame
        else:
            cls._validate_full_data_table(train_data=train_data, label_column_name=label_column_name,
                                          task_type=task_type)
            valid_df = None
        # create tune parameter sweeper
        setting = LearnerParameterSweeperSetting(
            sweeping_mode=sweeping_mode,
            binary_classification_metric=binary_classification_metric,
            regression_metric=regression_metric,
            max_num_of_runs=max_num_of_runs, random_seed=random_seed)
        learner = LearnerParameterSweeper(setting=setting, task_type=task_type, sub_model=predictor)
        # start to sweep hyper-parameters
        learner.train(df=train_df, label_column_name=label_column_name, valid_df=valid_df)
        return DataTable(learner.get_report()), learner.get_best_model()
