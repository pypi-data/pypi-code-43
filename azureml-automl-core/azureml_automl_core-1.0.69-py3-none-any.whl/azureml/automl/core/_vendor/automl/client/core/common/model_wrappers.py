# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Backwards compatible pass through during package migration."""
try:
    from automl.client.core.runtime import model_wrappers
    from automl.client.core.runtime.model_wrappers import _AbstractModelWrapper, LightGBMClassifier, \
        XGBoostClassifier, CatBoostClassifier, SparseNormalizer, SparseScaleZeroOne, PreprocWrapper, \
        StandardScalerWrapper, NBWrapper, TruncatedSVDWrapper, SVCWrapper, NuSVCWrapper, SGDClassifierWrapper, \
        EnsembleWrapper, LinearSVMWrapper, CalibratedModel, LightGBMRegressor, XGBoostRegressor, CatBoostRegressor, \
        RegressionPipeline, ForecastingPipelineWrapper, PipelineWithYTransformations, QuantileTransformerWrapper, \
        IdentityTransformer, LogTransformer, PowerTransformer, BoxCoxTransformerScipy, PreFittedSoftVotingClassifier, \
        PreFittedSoftVotingRegressor, StackEnsembleBase, StackEnsembleClassifier, StackEnsembleRegressor
except ImportError:
    pass
