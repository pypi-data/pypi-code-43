import copy
import pandas as pd
from azureml.studio.modulehost.attributes import \
    (DataTableInputPort, ModuleMeta, DataTableOutputPort,
     ReleaseState, DataTypes, UntrainedLearnerInputPort, SelectedColumnCategory,
     ColumnPickerParameter, IntParameter)
from azureml.studio.common.datatable.data_table import DataTableColumnSelection
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.core.logger import module_logger, TimeProfile
from azureml.studio.common.error import ErrorMapping, TooFewColumnsInDatasetError
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.ml.common.base_learner import BaseLearner
from azureml.studio.modules.ml.train.train_generic_model.train_generic_model import train_generic
from azureml.studio.modules.ml.score.score_generic_module.score_generic_module import score_generic
from azureml.studio.modules.ml.evaluate.evaluate_generic_module.evaluate_generic_module import evaluate_generic
from azureml.studio.modules.datatransform.partition_and_sample.partition_and_sample \
    import PartitionMethods, _META_PROPERTY_KEY, n_fold_partition

_MEAN_METRIC_ROW_NAME = 'Mean'
_STD_METRIC_ROW_NAME = 'Standard Deviation'
_FOLD_ROW_NAME = 'Fold Number'
_EXAMPLE_NUM_IN_FOLD_COL_NAME = 'Number of examples in fold'


class CrossValidateModelModule(BaseModule):
    evaluation_results_as_json = None

    @staticmethod
    @module_entry(ModuleMeta(
        name="Cross Validate Model",
        description="Cross Validate a classification or regression model with standard metrics",
        category="Machine Learning\\Evaluate",
        version="2.0",
        owner="Microsoft Corporation",
        family_id="{75FB875D-6B86-4D46-8BCC-74261ADE5826}",
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
                name="Name or numerical index of the label column",
                friendly_name="Label column",
                description="Select the column that contains the label or outcome column",
                column_picker_for="Dataset",
                single_column_selection=True,
                column_selection_categories=(SelectedColumnCategory.All,),
            ),
            random_seed: IntParameter(
                name="Random seed",
                friendly_name="Random seed",
                description="Specify a numeric seed to use for random number generation. ",
                default_value=0
            ),
    ) -> (
            DataTableOutputPort(
                data_type=DataTypes.DATASET,
                name="Scored results",
                friendly_name="Scored results",
                description="Data scored results",
            ),
            DataTableOutputPort(
                data_type=DataTypes.DATASET,
                name="Evaluation results by fold",
                friendly_name="Evaluation results by fold",
                description="Data evaluation results by fold",
            ),
    ):
        input_values = locals()
        output_values = CrossValidateModelModule.cross_validate_generic(**input_values)
        return output_values

    @classmethod
    def cross_validate_generic(cls, learner: BaseLearner, training_data: DataTable,
                               label_column_index_or_name: DataTableColumnSelection,
                               random_seed: int):
        """Split by fold to do cross validation

        :param learner: BaseLearner
        :param training_data: DataTable
        :param label_column_index_or_name: ColumnSelection
        :param random_seed: int
        :return: score_results_dt: DataTable, eval_results_dt: DataTable
        """
        ErrorMapping.verify_not_null_or_empty(x=training_data, name=cls._args.training_data.friendly_name)
        if training_data.number_of_columns == 0:
            ErrorMapping.throw(TooFewColumnsInDatasetError(
                arg_name=cls._args.training_data.friendly_name, required_columns_count=1))
        fold_indices = cls.get_fold_indices(training_data, random_seed)
        df = training_data.data_frame
        # Save score results of training data
        fold_score_result_dict = {}
        # Save evaluation results
        fold_eval_result = []
        n_example_in_fold = []
        for fold, test_index in enumerate(fold_indices):
            n_example_in_fold.append(len(test_index))
            cv_learner = copy.deepcopy(learner)
            cv_train_df = df[~df.index.isin(test_index)]
            cv_val_df = df[df.index.isin(test_index)]
            # Train
            with TimeProfile(f'Train {fold}'):
                cv_clf = train_generic(
                    learner=cv_learner,
                    training_data=DataTable(cv_train_df, training_data.meta_data),
                    label_column_index_or_name=label_column_index_or_name)
            # Score
            with TimeProfile(f'Score {fold}'):
                prediction = score_generic(
                    learner=cv_clf,
                    test_data=DataTable(cv_val_df, training_data.meta_data),
                    append_or_result_only=True)
            for ind, raw_ind in enumerate(test_index):
                fold_score_result_dict[raw_ind] = (prediction.data_frame.iloc[[ind], :], fold)
            # Evaluate
            with TimeProfile(f'Evaluate {fold}'):
                metric_dt = evaluate_generic(
                    scored_data=prediction,
                    scored_data_to_compare=None)
            fold_eval_result.append(metric_dt.data_frame)
        score_results_dt = cls.format_score_results(fold_score_result_dict, prediction.meta_data)
        eval_results_dt = cls.format_fold_eval_results(pd.concat(fold_eval_result), n_example_in_fold)
        return score_results_dt, eval_results_dt

    @staticmethod
    def format_score_results(fold_score_result_dict, meta_data):
        """Format score results to have all columns in score results and fold numb

        Format of score results based on V1, for example
                f0     f1      f2  ...  Scored Labels  Scored Probabilities  Fold Number
        0   17.990  10.38  122.80  ...              0              0.270907            0
        1   20.570  17.77  132.90  ...              0              0.082611            0
        2   19.690  21.25  130.00  ...              0              0.081996            0
        3   11.420  20.38   77.58  ...              0              0.113693            0
        4   20.290  14.34  135.10  ...              0              0.369674            0
        5   12.450  15.70   82.57  ...              1              0.577297            0
        6   18.250  19.98  119.60  ...              0              0.081996            0
        7   13.710  20.83   90.20  ...              0              0.081996            1
        8   13.000  21.82   87.50  ...              0              0.071424            1
        9   12.460  24.04   83.97  ...              0              0.076004            1
        10  16.020  23.24  102.70  ...              0              0.285608            1
        :param fold_score_result_dict: dict
        :param meta_data: DataFrameSchema
        :return: Datable
        """
        # Sort to keep original order in training_data
        score_results_dt = DataTable(
            pd.concat([fold_score_result_dict[k][0] for k in sorted(fold_score_result_dict.keys())], ignore_index=True),
            meta_data)
        # Add fold assignment column
        fold_assign_series = pd.Series([fold_score_result_dict[k][1] for k in sorted(fold_score_result_dict.keys())])
        score_results_dt.add_column(_FOLD_ROW_NAME, fold_assign_series)
        return score_results_dt

    @staticmethod
    def format_fold_eval_results(fold_eval_result, n_example_in_fold):
        """Calculate evaluation results by fold by adding mean, std and fold numb

        Format of eval results based on V1, for example
                   Fold Number  Number of examples in fold       AUC  Accuracy
        0                    0                          57  0.998024  0.929825
        1                    1                          57  0.983117  0.929825
        2                    2                          57  0.955026  0.894737
        3                    3                          57  0.995074  0.912281
        4                    4                          57  1.000000  0.982456
        5                    5                          57  0.944444  0.964912
        6                    6                          57  0.990854  0.947368
        7                    7                          57  0.998252  0.964912
        8                    8                          57  1.000000  0.964912
        9                    9                          56  0.994633  0.964286
        10                Mean                         569  0.985942  0.945551
        11  Standard Deviation                         569  0.019893  0.027937
        :param fold_eval_result: pd.DataFrame
        :param n_example_in_fold: list
        :return: pd.DataFrame
        """
        # Add mean and std rows to evaluation results
        mean_eval_result = pd.DataFrame(fold_eval_result.mean()).T
        std_eval_result = pd.DataFrame(fold_eval_result.std()).T
        fold_eval_result = pd.concat([fold_eval_result, mean_eval_result, std_eval_result], ignore_index=True)
        # Add Fold Number column to evaluation results in first column
        # -2 means we exclude 'Mean' and 'Standard Deviation' to generate fold number
        fold_num_list = [str(i) for i in range(fold_eval_result.shape[0] - 2)] +\
                        [_MEAN_METRIC_ROW_NAME, _STD_METRIC_ROW_NAME]
        fold_num_df = pd.DataFrame({_FOLD_ROW_NAME: fold_num_list})
        # Add Number of examples in fold to evaluation results in second column
        # *2 means we sum up example nums of all folds for 'Mean' and 'Standard Deviation'
        n_example_in_fold_df = pd.DataFrame({
            _EXAMPLE_NUM_IN_FOLD_COL_NAME: n_example_in_fold + [sum(n_example_in_fold)]*2})
        result = pd.concat([fold_num_df, n_example_in_fold_df, fold_eval_result], axis=1)
        return DataTable(result)

    @staticmethod
    def get_fold_indices(training_data, random_seed):
        # check whether using Partition and Sample Module previously
        fold_indices = training_data.meta_data.extended_properties.get(_META_PROPERTY_KEY, None)
        if fold_indices is None:
            module_logger.info('Not partitioned by fold before. Partition with default fold value 10')
            nfold_partition_dt, = n_fold_partition(
                table=training_data,
                with_replacement=False,
                random_flag=False,
                seed=random_seed,
                partition_method=PartitionMethods.EvenSizePartitioner,
                num_partitions=10,
                folds_prop_list='',
                stratify_flag=False,
                strats_column=None
            )
            fold_indices = nfold_partition_dt.meta_data.extended_properties[_META_PROPERTY_KEY]
        return fold_indices
