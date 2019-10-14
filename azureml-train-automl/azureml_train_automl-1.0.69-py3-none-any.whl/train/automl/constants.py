# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Various constants used throughout automated machine learning."""

from automl.client.core.common.constants import (
    ModelClassNames,
    MODEL_PATH,
    MODEL_PATH_TRAIN,
    MODEL_PATH_ONNX,
    MODEL_RESOURCE_PATH_ONNX,
    EnsembleConstants,
    Defaults,
    RunState,
    API,
    AcquisitionFunction,
    Status,
    PipelineParameterConstraintCheckStatus,
    OptimizerObjectives,
    Optimizer,
    Tasks as CommonTasks,
    ClientErrors,
    ServerStatus,
    TimeConstraintEnforcement,
    PipelineCost,
    Metric,
    MetricObjective,
    TrainingType,
    NumericalDtype,
    TextOrCategoricalDtype,
    TrainingResultsType,
    get_metric_from_type,
    get_status_from_type,
)

from azureml.automl.core.constants import (
    FeatureType, SupportedTransformers, FeaturizationConfigMode
)


AUTOML_SETTINGS_PATH = "automl_settings.pkl"
AUTOML_FIT_PARAMS_PATH = "fit_params.pkl"
LOCAL_SCRIPT_NAME = "_script.py"
LOCAL_PREDICT_NAME = "_predict.py"
PREDICT_INPUT_FILE = "predict.pkl"
PREDICTED_METRIC_NAME = "predicted"
LOCAL_MODEL_PATH = "model.pkl"


class SupportedModels:
    """Customer Facing Names for all algorithms supported by AutoML."""

    class Classification:
        """Classification model names."""

        LogisticRegression = 'LogisticRegression'
        SGDClassifier = 'SGD'
        MultinomialNB = 'MultinomialNaiveBayes'
        BernoulliNB = 'BernoulliNaiveBayes'
        SupportVectorMachine = 'SVM'
        LinearSupportVectorMachine = 'LinearSVM'
        KNearestNeighborsClassifier = 'KNN'
        DecisionTree = 'DecisionTree'
        RandomForest = 'RandomForest'
        ExtraTrees = 'ExtremeRandomTrees'
        LightGBMClassifier = 'LightGBM'
        GradientBoosting = 'GradientBoosting'
        TensorFlowDNNClassifier = 'TensorFlowDNN'
        TensorFlowLinearClassifier = 'TensorFlowLinearClassifier'
        XGBoostClassifier = 'XGBoostClassifier'
        NimbusMLAveragedPerceptronClassifier = 'NimbusMLAveragedPerceptronClassifier'
        NimbusMLLinearSVMClassifier = 'NimbusMLLinearSVMClassifier'

    class Regression:
        """Regression model names."""

        ElasticNet = 'ElasticNet'
        GradientBoostingRegressor = 'GradientBoosting'
        DecisionTreeRegressor = 'DecisionTree'
        KNearestNeighborsRegressor = 'KNN'
        LassoLars = 'LassoLars'
        SGDRegressor = 'SGD'
        RandomForestRegressor = 'RandomForest'
        ExtraTreesRegressor = 'ExtremeRandomTrees'
        LightGBMRegressor = 'LightGBM'
        TensorFlowLinearRegressor = 'TensorFlowLinearRegressor'
        TensorFlowDNNRegressor = 'TensorFlowDNN'
        XGBoostRegressor = 'XGBoostRegressor'
        NimbusMLFastLinearRegressor = 'NimbusMLFastLinearRegressor'
        NimbusMLOnlineGradientDescentRegressor = 'NimbusMLOnlineGradientDescentRegressor'

    class Forecasting(Regression):
        """Forecasting model names."""

        AutoArima = 'AutoArima'
        Prophet = 'Prophet'
        TCNForecaster = 'TCNForecaster'


MODEL_EXPLANATION_TAG = "model_explanation"

MAX_ITERATIONS = 1000
MAX_SAMPLES_BLACKLIST = 5000
MAX_SAMPLES_BLACKLIST_ALGOS = [SupportedModels.Classification.KNearestNeighborsClassifier,
                               SupportedModels.Regression.KNearestNeighborsRegressor,
                               SupportedModels.Classification.SupportVectorMachine]
EARLY_STOPPING_NUM_LANDMARKS = 20

DATA_SCRIPT_FILE_NAME = "get_data.py"

"""Names of algorithms that do not support sample weights."""
Sample_Weights_Unsupported = {
    ModelClassNames.RegressionModelClassNames.ElasticNet,
    ModelClassNames.ClassificationModelClassNames.KNearestNeighborsClassifier,
    ModelClassNames.RegressionModelClassNames.KNearestNeighborsRegressor,
    ModelClassNames.RegressionModelClassNames.LassoLars
}

"""Algorithm names that we must force to run in single threaded mode."""
SINGLE_THREADED_ALGORITHMS = [
    ModelClassNames.ClassificationModelClassNames.KNearestNeighborsClassifier,
    ModelClassNames.RegressionModelClassNames.KNearestNeighborsRegressor
]

TrainingType.FULL_SET.remove(TrainingType.TrainValidateTest)


class ComputeTargets:
    """Names of compute targets supported by AutoML."""

    DSVM = 'VirtualMachine'
    BATCHAI = 'BatchAI'
    AMLCOMPUTE = 'AmlCompute'
    LOCAL = 'local'


class TimeSeries:
    """Parameters used for timeseries."""

    TIME_COLUMN_NAME = 'time_column_name'
    GRAIN_COLUMN_NAMES = 'grain_column_names'
    DROP_COLUMN_NAMES = 'drop_column_names'
    MAX_HORIZON = 'max_horizon'


class Tasks(CommonTasks):
    """A subclass of Tasks in common.core, extendable to more task types for SDK."""

    CLASSIFICATION = CommonTasks.CLASSIFICATION
    REGRESSION = CommonTasks.REGRESSION
    FORECASTING = 'forecasting'
    ALL = [CommonTasks.CLASSIFICATION, CommonTasks.REGRESSION, FORECASTING]


class ExperimentObserver:
    """Constants used by the Experiment Observer to report progress during preprocessing."""

    EXPERIMENT_STATUS_TAG_NAME = "experiment_status"
    EXPERIMENT_STATUS_DESCRIPTION_TAG_NAME = "experiment_status_descr"
