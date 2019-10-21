from azureml.studio.core.logger import module_logger

import azureml.studio.modules.ml.common.ml_utils as ml_utils
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table import DataTableColumnSelection
from azureml.studio.common.error import TooFewColumnsInDatasetError, ErrorMapping
from azureml.studio.common.input_parameter_checker import InputParameterChecker
from azureml.studio.modulehost.attributes import ModuleMeta, ReleaseState, UntrainedLearnerInputPort, \
    DataTableInputPort, ColumnPickerParameter, SelectedColumnCategory, ILearnerOutputPort
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.ml.common.base_learner import BaseLearner


class TrainModelModule(BaseModule):
    key_train_generic_model = {
        "learner": "Untrained model",
        "training_data": "Dataset",
        "otrained_model": "Trained model",
        "label_column_index_or_name": "Label column",
        "train_generic_model": "Train Model"
    }
    min_columns = 2

    @staticmethod
    @module_entry(ModuleMeta(
        name="Train Model",
        description="Trains a classification or regression model in a supervised manner",
        category="Machine Learning\\Train",
        version="2.0",
        owner="Microsoft Corporation",
        family_id="{5CC7053E-AA30-450D-96C0-DAE4BE720977}",
        release_state=ReleaseState.Release,
        is_deterministic=True,
    ))
    def run(
            learner: UntrainedLearnerInputPort(
                name="Untrained model",
                friendly_name="Untrained model",
                description="Untrained learner",
            ),
            training_data: DataTableInputPort(
                name="Dataset",
                friendly_name="Dataset",
                description="Training data",
            ),
            label_column_index_or_name: ColumnPickerParameter(
                name="Label column",
                friendly_name="Label column",
                description="Select the column that contains the label or outcome column",
                column_picker_for="Dataset",
                single_column_selection=True,
                column_selection_categories=(SelectedColumnCategory.All,),
            )
    ) -> (
            ILearnerOutputPort(
                name="Trained model",
                friendly_name="Trained model",
                description="Trained learner",
            ),
    ):
        input_values = locals()
        output_values = TrainModelModule.train_generic_model(**input_values)
        return output_values

    @classmethod
    def _validate_args(cls, learner, training_data):
        ErrorMapping.verify_not_null_or_empty(learner, cls.key_train_generic_model.get("learner", "Untrained model"))
        InputParameterChecker.verify_data_table(data_table=training_data,
                                                friendly_name=cls.key_train_generic_model.get("training_data",
                                                                                              "Dataset"))
        if training_data.number_of_columns < cls.min_columns:
            ErrorMapping.throw(TooFewColumnsInDatasetError(str(cls.min_columns)))

    @classmethod
    def train_generic_model(cls, learner: BaseLearner, training_data: DataTable,
                            label_column_index_or_name: DataTableColumnSelection):
        module_logger.info("Validate input data (learner and training data).")
        cls._validate_args(learner, training_data)
        df = training_data.data_frame
        # This will return a new data frame
        df = df.reset_index(drop=True)
        label_column_name = ml_utils.get_label_column_name(training_data=training_data,
                                                           column_selection=label_column_index_or_name,
                                                           dataset_name=cls._args.training_data.friendly_name)
        module_logger.info(f"{label_column_name} as Label Column.")
        ml_utils.validate_training_label(training_data, label_column_name, task_type=learner.task_type,
                                         data_name=cls._args.training_data.friendly_name)
        try:
            learner.train(df=df, label_column_name=label_column_name)
        except Exception as e:
            raise e
        return tuple([learner])


def train_generic(learner, training_data, label_column_index_or_name):
    train_result, = TrainModelModule.train_generic_model(learner, training_data, label_column_index_or_name)
    return train_result
