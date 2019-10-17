import pandas as pd
import pytest

from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder
from azureml.studio.common.error import InvalidLearnerError, LearnerTypesNotCompatibleError, UntrainedModelError, \
    UnsupportedParameterTypeError, TooFewRowsInDatasetError
from azureml.studio.modules.feature_selection.permutation_feature_importance.permutation_feature_importance import \
    PermutationFeatureImportanceModule, DataTable, EvaluationMetricType
from azureml.studio.modules.ml.common.base_learner import BaseLearner, CreateLearnerMode
from azureml.studio.modules.ml.common.base_learner_setting import BaseLearnerSetting
from azureml.studio.modules.ml.common.ml_utils import TaskType
from azureml.studio.modules.ml.initialize_models.binary_classifier.boosted_decision_tree_biclassifier.\
    boosted_decision_tree_biclassifier import TwoClassBoostedDecisionTreeModule
from azureml.studio.modules.ml.initialize_models.binary_classifier.decision_forest_biclassifier.\
    decision_forest_biclassifier import TwoClassDecisionForestModule
from azureml.studio.modules.ml.initialize_models.multi_classifier.boosted_decision_tree_multiclassifier.\
    boosted_decision_tree_multiclassifier import MultiClassBoostedDecisionTreeModule
from azureml.studio.modules.ml.initialize_models.regressor.linear_regressor.linear_regressor import \
    LinearRegressionModule, CreateLinearRegressionModelSolutionMethod
from azureml.studio.modules.ml.train.train_generic_model.train_generic_model import train_generic


def is_descending(l):
    for i in range(len(l) - 1):
        if l[i] < l[i + 1]:
            return False
    return True


def create_classification_data_table():
    features = [
        [1.43749224, -2.31180576, -0.80017904, 2.88098529],
        [-0.77583347, -0.59433006, -0.73031927, 0.26679244],
        [2.53661484, -0.364639, 0.93174688, 1.41004666],
        [1.62420019, 0.43557224, 1.01871945, 0.2411938],
        [-1.22758778, 1.47263874, 0.36686864, -1.96424566],
        [1.61583831, 0.46494797, 1.03342342, 0.20868306],
        [1.37313986, -0.56788802, 0.27062421, 1.12970426],
        [2.38422167, -0.24474165, 0.93759461, 1.22842618],
        [-0.55552844, -0.19499792, -0.37746863, -0.03698595],
        [-1.85534282, 1.99359892, 0.40803352, -2.73916372],
        [-0.90408105, -1.10709854, -1.11257586, 0.72083988],
        [-1.92587107, -2.91832221, -2.72331275, 2.08933043],
        [1.9498999, -0.98564495, 0.27121618, 1.78146148],
        [-2.22831066, -2.99773257, -2.91193623, 2.04274006],
        [-0.87121622, 1.23447783, 0.37983076, -1.58127892],
        [-0.97944508, 1.15885171, 0.28254614, -1.55126389],
        [0.39443939, -1.47476226, -0.74980233, 1.62166001],
        [-0.41197528, 2.23734068, 1.22289879, -2.38307119],
        [0.06812472, -0.06659014, -0.01081114, 0.0940389],
        [1.81985678, -1.726387, -0.25569652, 2.46022186]]

    label = [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1]

    df = pd.DataFrame(data=features, columns=["f1", "f2", "f3", "f4"])
    df["label"] = label

    return DataTable(df=df)


def create_regression_data_table():
    features = [
        [0.62054822, -0.16093738, -0.88551237, -0.3882644],
        [-2.65517605, 0.34551794, -0.28913686, -0.39551645],
        [1.37186213, 0.17555329, 0.6731255, -0.30928855],
        [0.64908673, -1.22287354, -0.91469093, 0.53633603],
        [0.45293633, -0.16606091, -2.02231493, 0.21493883],
        [0.76729684, -1.14979258, 0.77314086, -0.77533611],
        [0.61764085, 1.2170708, 0.84740143, 0.22628827],
        [-0.57470921, -0.42149822, -0.00738015, 0.33982096],
        [1.70660495, 0.87358942, -0.3655393, 0.00914435],
        [-1.44004145, 1.19072726, -0.86714616, 1.29939681],
        [-0.94305681, 1.40395874, -1.67350462, -0.0185508],
        [1.36388652, 2.53916272, -0.20586672, -0.32449096],
        [-0.80182784, 1.38401572, 1.39232575, 1.40520531],
        [-0.88064082, 0.07689495, 0.92316261, -0.49343248],
        [-0.35674503, 0.5561218, 0.52644816, 1.04386061],
        [0.50144833, 1.15818665, 0.3145129, 0.25711687],
        [-0.25663018, -0.36782572, -0.29195267, 1.27373362],
        [-1.07253183, -0.99258618, -0.43260928, 0.10234768],
        [-0.6591823, 0.0039373, -0.25902864, 0.4777541],
        [0.17483301, -1.21685489, 1.32510566, 1.04934739]]

    label = [-35.57071694, -53.73247615, 57.83483916, -89.57298085, -62.37520388, -57.91452329, 133.47212743,
             -35.08511964, 88.81144551, 55.11657201, 23.94124818, 197.02426639, 159.22879168, 4.05927043,
             73.50124791, 110.06390839, -11.23212835, -106.39242613, -11.5971412, -14.72633973]

    df = pd.DataFrame(data=features, columns=["f1", "f2", "f3", "f4"])
    df["label"] = label

    return DataTable(df=df)


@pytest.fixture()
def binary_classification_model():
    untrained_model, = TwoClassBoostedDecisionTreeModule.create_boosted_decision_tree_biclassifier(
        mode=CreateLearnerMode.SingleParameter)

    trained_model = train_generic(
        learner=untrained_model,
        training_data=create_classification_data_table(),
        label_column_index_or_name=DataTableColumnSelectionBuilder().include_col_names("label").build()
    )

    return trained_model


@pytest.fixture()
def multiple_classification_model():
    untrained_model, = MultiClassBoostedDecisionTreeModule.create_boosted_decision_tree_multiclassifier(
        mode=CreateLearnerMode.SingleParameter)

    label_column_selection = DataTableColumnSelectionBuilder().include_col_names("label").build()
    trained_model = train_generic(
        learner=untrained_model,
        training_data=create_classification_data_table(),
        label_column_index_or_name=label_column_selection
    )

    return trained_model


@pytest.fixture()
def regression_model():
    untrained_model, = LinearRegressionModule.create_linear_regressor(
        solution_method=CreateLinearRegressionModelSolutionMethod.OnlineGradientDescent,
        mode=CreateLearnerMode.SingleParameter)

    label_column_selection = DataTableColumnSelectionBuilder().include_col_names("label").build()
    trained_model = train_generic(
        learner=untrained_model,
        training_data=create_regression_data_table(),
        label_column_index_or_name=label_column_selection
    )

    return trained_model


@pytest.fixture()
def classification_data_table():
    return create_classification_data_table()


@pytest.fixture()
def regression_data_table():
    return create_regression_data_table()


@pytest.mark.parametrize(
    'metric',
    [
        EvaluationMetricType.Accuracy,
        EvaluationMetricType.Precision,
        EvaluationMetricType.Recall,
    ]
)
def test_permutation_feature_importance_with_binary_classification_model(
        binary_classification_model,
        classification_data_table,
        metric):
    origin_data_table = classification_data_table.clone()
    datatable = PermutationFeatureImportanceModule.run(
        learner=binary_classification_model,
        dataset=classification_data_table,
        random_seed=0,
        evaluation_metric=metric
    )[0]

    assert datatable.number_of_rows == 4
    assert is_descending(datatable.get_column(PermutationFeatureImportanceModule.SCORE_COLUMN_NAME))
    assert classification_data_table.data_frame.equals(origin_data_table.data_frame)


@pytest.mark.parametrize(
    'metric',
    [
        EvaluationMetricType.Accuracy,
        EvaluationMetricType.Precision,
        EvaluationMetricType.Recall,
    ]
)
def test_permutation_feature_importance_with_multiple_classification_model(
        multiple_classification_model,
        classification_data_table,
        metric):
    origin_data_table = classification_data_table.clone()
    datatable = PermutationFeatureImportanceModule.run(
        learner=multiple_classification_model,
        dataset=classification_data_table,
        random_seed=0,
        evaluation_metric=metric
    )[0]

    assert datatable.number_of_rows == 4
    assert is_descending(datatable.get_column(PermutationFeatureImportanceModule.SCORE_COLUMN_NAME))
    assert classification_data_table.data_frame.equals(origin_data_table.data_frame)


@pytest.mark.parametrize(
    'metric',
    [
        EvaluationMetricType.RootMeanSquaredError,
        EvaluationMetricType.CoefficientOfDetermination,
        EvaluationMetricType.RelativeAbsoluteError,
        EvaluationMetricType.MeanAbsoluteError,
        EvaluationMetricType.RelativeSquaredError,
    ]
)
def test_permutation_feature_importance_with_regression_model(
        regression_model,
        regression_data_table,
        metric):
    origin_data_table = regression_data_table.clone()
    datatable = PermutationFeatureImportanceModule.run(
        learner=regression_model,
        dataset=regression_data_table,
        random_seed=0,
        evaluation_metric=metric
    )[0]

    assert datatable.number_of_rows == 4
    assert is_descending(datatable.get_column(PermutationFeatureImportanceModule.SCORE_COLUMN_NAME))
    assert regression_data_table.data_frame.equals(origin_data_table.data_frame)


@pytest.mark.parametrize(
    'metric',
    [
        EvaluationMetricType.Accuracy,
        EvaluationMetricType.Precision,
        EvaluationMetricType.Recall,
    ]
)
def test_permutation_feature_importance_with_string_columns(metric):
    features = [
        [1.43749224, 'a', -0.80017904, 'f'],
        [-0.77583347, 'b', -0.73031927, 'g'],
        [2.53661484, 'c', 0.93174688, 'h'],
        [1.62420019, 'd', 1.01871945, 'i'],
        [-1.22758778, 'e', 0.36686864, 'j']]

    label = ['A', 'B', 'A', 'A', 'B']

    df = pd.DataFrame(data=features, columns=["f1", "f2", "f3", "f4"])
    df["label"] = label

    classification_data_table = DataTable(df=df)

    untrained_model, = TwoClassDecisionForestModule.create_decision_forest_biclassifier(
        mode=CreateLearnerMode.SingleParameter)

    trained_model = train_generic(
        learner=untrained_model,
        training_data=classification_data_table,
        label_column_index_or_name=DataTableColumnSelectionBuilder().include_col_names("label").build()
    )

    origin_data_table = classification_data_table.clone()
    datatable = PermutationFeatureImportanceModule.run(
        learner=trained_model,
        dataset=classification_data_table,
        random_seed=0,
        evaluation_metric=metric
    )[0]

    assert datatable.number_of_rows == 4
    assert is_descending(datatable.get_column(PermutationFeatureImportanceModule.SCORE_COLUMN_NAME))
    assert classification_data_table.data_frame.equals(origin_data_table.data_frame)


class DummyTrainedModel(BaseLearner):
    def init_model(self):
        pass

    def __init__(self, setting: BaseLearnerSetting, task_type=None):
        super().__init__(setting, task_type)
        self._is_trained = True


@pytest.mark.parametrize(
    'learner,metric',
    [
        (DummyTrainedModel(setting=BaseLearnerSetting(), task_type=TaskType.BinaryClassification),
         EvaluationMetricType.RootMeanSquaredError),
        (DummyTrainedModel(setting=BaseLearnerSetting(), task_type=TaskType.MultiClassification),
         EvaluationMetricType.RootMeanSquaredError),
        (DummyTrainedModel(setting=BaseLearnerSetting(), task_type=TaskType.Regression),
         EvaluationMetricType.Accuracy),
    ]
)
def test_permutation_feature_importance_with_inconsistent_metric_type(learner, metric):
    with pytest.raises(UnsupportedParameterTypeError,
                       match="Unsupported parameter type 'Metric for measuring performance' specified"):
        PermutationFeatureImportanceModule.run(
            learner=learner,
            dataset=DataTable(),
            random_seed=0,
            evaluation_metric=metric
        )


@pytest.mark.parametrize(
    'learner',
    [
        DummyTrainedModel(setting=BaseLearnerSetting(), task_type=TaskType.Cluster),
        DummyTrainedModel(setting=BaseLearnerSetting(), task_type=None)
    ]
)
def test_permutation_feature_importance_with_invalid_learner_task_type(learner):
    task_type_name = learner.task_type.name if learner.task_type else 'None'
    with pytest.raises(LearnerTypesNotCompatibleError,
                       match=f'Got incompatible learner type: "{task_type_name}".'):
        PermutationFeatureImportanceModule.run(
            learner=learner,
            dataset=DataTable(),
            random_seed=0,
            evaluation_metric=EvaluationMetricType.Accuracy
        )


def test_permutation_feature_importance_with_untrained_model():
    learner = BaseLearner(setting=BaseLearnerSetting(), task_type=TaskType.BinaryClassification)

    with pytest.raises(UntrainedModelError,
                       match='Untrained model [(]Trained model[)], use trained model.'):
        PermutationFeatureImportanceModule.run(
            learner=learner,
            dataset=DataTable(),
            random_seed=0,
            evaluation_metric=EvaluationMetricType.Accuracy
        )


def test_permutation_feature_importance_with_invalid_learner():
    learner = DummyTrainedModel(setting=BaseLearnerSetting(), task_type=TaskType.BinaryClassification)

    with pytest.raises(InvalidLearnerError,
                       match='Learner "Trained model" has invalid type.'):
        learner.label_column_name = None
        learner.init_feature_columns_names = []
        PermutationFeatureImportanceModule.run(
            learner=learner,
            dataset=DataTable(),
            random_seed=0,
            evaluation_metric=EvaluationMetricType.Accuracy
        )

    with pytest.raises(InvalidLearnerError,
                       match='Learner "Trained model" has invalid type.'):
        learner.label_column_name = "label"
        learner.init_feature_columns_names = None
        PermutationFeatureImportanceModule.run(
            learner=learner,
            dataset=DataTable(),
            random_seed=0,
            evaluation_metric=EvaluationMetricType.Accuracy
        )


def test_permutation_feature_importance_with_invalid_dataset():
    learner = DummyTrainedModel(setting=BaseLearnerSetting(), task_type=TaskType.BinaryClassification)

    with pytest.raises(TooFewRowsInDatasetError,
                       match='Number of rows in input dataset "Test data" is '):
        learner.label_column_name = "label"
        learner.init_feature_columns_names = []
        PermutationFeatureImportanceModule.run(
            learner=learner,
            dataset=DataTable(),
            random_seed=0,
            evaluation_metric=EvaluationMetricType.Accuracy
        )
