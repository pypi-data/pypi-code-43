# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Metrics constants."""

# Task Types

CLASSIFICATION = 'classification'
REGRESSION = 'regression'
FORECASTING = 'forecasting'

TASKS = {CLASSIFICATION, REGRESSION, FORECASTING}

# Classification Metrics

ACCURACY = 'accuracy'
WEIGHTED_ACCURACY = 'weighted_accuracy'
BALANCED_ACCURACY = 'balanced_accuracy'
NORM_MACRO_RECALL = 'norm_macro_recall'
LOG_LOSS = 'log_loss'
AUC_MACRO = 'AUC_macro'
AUC_MICRO = 'AUC_micro'
AUC_WEIGHTED = 'AUC_weighted'
F1_MACRO = 'f1_score_macro'
F1_MICRO = 'f1_score_micro'
F1_WEIGHTED = 'f1_score_weighted'
PRECISION_MACRO = 'precision_score_macro'
PRECISION_MICRO = 'precision_score_micro'
PRECISION_WEIGHTED = 'precision_score_weighted'
RECALL_MACRO = 'recall_score_macro'
RECALL_MICRO = 'recall_score_micro'
RECALL_WEIGHTED = 'recall_score_weighted'
AVERAGE_PRECISION_MACRO = 'average_precision_score_macro'
AVERAGE_PRECISION_MICRO = 'average_precision_score_micro'
AVERAGE_PRECISION_WEIGHTED = 'average_precision_score_weighted'
ACCURACY_TABLE = 'accuracy_table'
CONFUSION_MATRIX = 'confusion_matrix'

CLASSIFICATION_SCALAR_SET = {
    ACCURACY, WEIGHTED_ACCURACY, BALANCED_ACCURACY,
    NORM_MACRO_RECALL, LOG_LOSS,
    AUC_MACRO, AUC_MICRO, AUC_WEIGHTED,
    F1_MACRO, F1_MICRO, F1_WEIGHTED,
    PRECISION_MACRO, PRECISION_MICRO, PRECISION_WEIGHTED,
    RECALL_MACRO, RECALL_MICRO, RECALL_WEIGHTED,
    AVERAGE_PRECISION_MACRO, AVERAGE_PRECISION_MICRO, AVERAGE_PRECISION_WEIGHTED
}

CLASSIFICATION_NONSCALAR_SET = {
    ACCURACY_TABLE,
    CONFUSION_MATRIX
}

CLASSIFICATION_SET = CLASSIFICATION_SCALAR_SET | CLASSIFICATION_NONSCALAR_SET

CLASSIFICATION_PRIMARY_SET = {
    ACCURACY, AUC_WEIGHTED, NORM_MACRO_RECALL,
    AVERAGE_PRECISION_WEIGHTED, PRECISION_WEIGHTED
}

CLASSIFICATION_BALANCED_SET = {
    # Metrics for which class_weights are recommended
    BALANCED_ACCURACY, AUC_MACRO, NORM_MACRO_RECALL, AVERAGE_PRECISION_WEIGHTED,
    PRECISION_MACRO, F1_MACRO, RECALL_MACRO
}

# Regression Metrics

EXPLAINED_VARIANCE = 'explained_variance'
R2_SCORE = 'r2_score'
SPEARMAN = 'spearman_correlation'
MAPE = 'mean_absolute_percentage_error'
MEAN_ABS_ERROR = 'mean_absolute_error'
NORM_MEAN_ABS_ERROR = 'normalized_mean_absolute_error'
MEDIAN_ABS_ERROR = 'median_absolute_error'
NORM_MEDIAN_ABS_ERROR = 'normalized_median_absolute_error'
RMSE = 'root_mean_squared_error'
NORM_RMSE = 'normalized_root_mean_squared_error'
RMSLE = 'root_mean_squared_log_error'
NORM_RMSLE = 'normalized_root_mean_squared_log_error'
RESIDUALS = 'residuals'
PREDICTED_TRUE = 'predicted_true'

REGRESSION_SCALAR_SET = {
    EXPLAINED_VARIANCE, R2_SCORE, SPEARMAN, MAPE,
    MEAN_ABS_ERROR, NORM_MEAN_ABS_ERROR,
    MEDIAN_ABS_ERROR, NORM_MEDIAN_ABS_ERROR,
    RMSE, NORM_RMSE,
    RMSLE, NORM_RMSLE
}

REGRESSION_NONSCALAR_SET = {
    RESIDUALS,
    PREDICTED_TRUE
}

REGRESSION_SET = REGRESSION_SCALAR_SET | REGRESSION_NONSCALAR_SET

REGRESSION_PRIMARY_SET = {
    R2_SCORE, SPEARMAN, NORM_RMSE, NORM_MEAN_ABS_ERROR
}

# Forecasting Metrics

FORECASTING_MAPE = 'forecast_mean_absolute_percentage_error'
FORECASTING_RESIDUALS = 'forecast_residuals'

FORECASTING_SCALAR_SET = set()

FORECASTING_NONSCALAR_SET = {
    FORECASTING_MAPE,
    FORECASTING_RESIDUALS
}

FORECASTING_SET = FORECASTING_SCALAR_SET | FORECASTING_NONSCALAR_SET

# All Metrics

FULL_SET = CLASSIFICATION_SET | REGRESSION_SET | FORECASTING_SET

FULL_NONSCALAR_SET = (CLASSIFICATION_NONSCALAR_SET |
                      REGRESSION_NONSCALAR_SET |
                      FORECASTING_NONSCALAR_SET)

FULL_SCALAR_SET = CLASSIFICATION_SCALAR_SET | REGRESSION_SCALAR_SET

METRICS_TASK_MAP = {
    CLASSIFICATION: CLASSIFICATION_SET,
    REGRESSION: REGRESSION_SET,
    FORECASTING: FORECASTING_SET
}

SAMPLE_WEIGHTS_UNSUPPORTED_SET = {
    SPEARMAN, WEIGHTED_ACCURACY, MEDIAN_ABS_ERROR, NORM_MEDIAN_ABS_ERROR
}

# Time Metrics

TRAIN_TIME = 'train time'
FIT_TIME = 'fit_time'
PREDICT_TIME = 'predict_time'

ALL_TIME = {TRAIN_TIME, FIT_TIME, PREDICT_TIME}

FULL_SCALAR_SET_TIME = FULL_SCALAR_SET | ALL_TIME

# Schema Types

# These types will be removed when the artifact-backed
# metrics are defined with protobuf
# Do not use these constants except in artifact-backed metrics
SCHEMA_TYPE_ACCURACY_TABLE = 'accuracy_table'
SCHEMA_TYPE_CONFUSION_MATRIX = 'confusion_matrix'
SCHEMA_TYPE_RESIDUALS = 'residuals'
SCHEMA_TYPE_PREDICTIONS = 'predictions'
SCHEMA_TYPE_MAPE = 'mape_table'

# Clipping

CLIPS_POSITIVE = {
    # TODO: If we are no longer transforming by default reconsider these
    # it is probably not necessary for them to be over 1
    LOG_LOSS: 1,
    NORM_MEAN_ABS_ERROR: 1,
    NORM_MEDIAN_ABS_ERROR: 1,
    NORM_RMSE: 1,
    NORM_RMSLE: 1,
    # current timeout value but there is a long time
    TRAIN_TIME: 10 * 60 * 2
}

CLIPS_NEGATIVE = {
    # TODO: If we are no longer transforming by default reconsider these
    # it is probably not necessary for them to be over 1
    # spearman is naturally limitted to this range but necessary for transform_y to work
    # otherwise spearmen is getting clipped to 0 by default
    SPEARMAN: -1,
    EXPLAINED_VARIANCE: -1,
    R2_SCORE: -1
}

# Objectives

MAXIMIZE = "maximize"
MINIMIZE = "minimize"
NA = 'NA'

OBJECTIVES = {MAXIMIZE, MINIMIZE, NA}

CLASSIFICATION_OBJECTIVES = {
    ACCURACY: MAXIMIZE,
    WEIGHTED_ACCURACY: MAXIMIZE,
    NORM_MACRO_RECALL: MAXIMIZE,
    BALANCED_ACCURACY: MAXIMIZE,
    LOG_LOSS: MINIMIZE,
    AUC_MACRO: MAXIMIZE,
    AUC_MICRO: MAXIMIZE,
    AUC_WEIGHTED: MAXIMIZE,
    F1_MACRO: MAXIMIZE,
    F1_MICRO: MAXIMIZE,
    F1_WEIGHTED: MAXIMIZE,
    PRECISION_MACRO: MAXIMIZE,
    PRECISION_MICRO: MAXIMIZE,
    PRECISION_WEIGHTED: MAXIMIZE,
    RECALL_MACRO: MAXIMIZE,
    RECALL_MICRO: MAXIMIZE,
    RECALL_WEIGHTED: MAXIMIZE,
    AVERAGE_PRECISION_MACRO: MAXIMIZE,
    AVERAGE_PRECISION_MICRO: MAXIMIZE,
    AVERAGE_PRECISION_WEIGHTED: MAXIMIZE,
    ACCURACY_TABLE: NA,
    CONFUSION_MATRIX: NA,
    TRAIN_TIME: MINIMIZE
}

REGRESSION_OBJECTIVES = {
    EXPLAINED_VARIANCE: MAXIMIZE,
    R2_SCORE: MAXIMIZE,
    SPEARMAN: MAXIMIZE,
    MEAN_ABS_ERROR: MINIMIZE,
    NORM_MEAN_ABS_ERROR: MINIMIZE,
    MEDIAN_ABS_ERROR: MINIMIZE,
    NORM_MEDIAN_ABS_ERROR: MINIMIZE,
    RMSE: MINIMIZE,
    NORM_RMSE: MINIMIZE,
    RMSLE: MINIMIZE,
    NORM_RMSLE: MINIMIZE,
    MAPE: MINIMIZE,
    RESIDUALS: NA,
    PREDICTED_TRUE: NA,
    TRAIN_TIME: MINIMIZE
}

FORECASTING_OBJECTIVES = {
    FORECASTING_RESIDUALS: NA,
    FORECASTING_MAPE: NA
}

FULL_OBJECTIVES = {**CLASSIFICATION_OBJECTIVES,
                   **REGRESSION_OBJECTIVES,
                   **FORECASTING_OBJECTIVES}

OBJECTIVES_TASK_MAP = {
    CLASSIFICATION: CLASSIFICATION_OBJECTIVES,
    REGRESSION: REGRESSION_OBJECTIVES,
    FORECASTING: FORECASTING_OBJECTIVES
}

# Pipeline constants

DEFAULT_PIPELINE_SCORE = float('NaN')
