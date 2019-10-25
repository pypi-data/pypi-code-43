# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for timeseries preprocessing."""
from typing import Any, cast, DefaultDict, Dict, List, Optional, Type, Union
import copy
import inspect
import json
import logging
import warnings
import numpy as np
import operator
import pandas as pd

from collections import defaultdict
from itertools import chain
from enum import Enum
from sklearn.base import TransformerMixin

from automl.client.core.runtime import memory_utilities
from automl.client.core.common.constants import TimeSeriesInternal, TimeSeries
from automl.client.core.runtime.time_series_data_frame import TimeSeriesDataFrame
from automl.client.core.runtime.forecasting_ts_utils import detect_seasonality_tsdf
from automl.client.core.runtime.forecasting_verify import is_iterable_but_not_string
from automl.client.core.runtime.types import DataInputType, DataSingleColumnInputType, FeaturizationSummaryType
from automl.client.core.common.exceptions import ConfigException,\
    ClientException
from azureml.automl.core.constants import FeatureType as _FeatureType
from azureml.automl.core.constants import SupportedTransformersInternal as _SupportedTransformersInternal
from .category_binarizer import CategoryBinarizer
from azureml.automl.core.featurization_info_provider import FeaturizationInfoProvider
from azureml.automl.core.featurizer.transformer.timeseries.short_grain_dropper import ShortGrainDropper
from .max_horizon_featurizer import MaxHorizonFeaturizer
from .restore_dtypes_transformer import RestoreDtypesTransformer
from .rolling_window import RollingWindow
from .lag_lead_operator import LagLeadOperator
from .missingdummies_transformer import MissingDummiesTransformer
from .numericalize_transformer import NumericalizeTransformer
from .abstract_timeseries_transformer import AbstractTimeSeriesTransformer
from .forecasting_base_estimator import AzureMLForecastTransformerBase
from .forecasting_pipeline import AzureMLForecastPipeline
from .forecasting_heuristic_utils import get_heuristic_max_horison, analyze_pacf_per_grain
from .stl_featurizer import STLFeaturizer
from ..automltransformer import AutoMLTransformer
from ...._engineered_feature_names import \
    _FeatureTransformersAsJSONObject, _OperatorNames, _Transformer, _FeatureTransformers, \
    _RawFeatureFeaturizationInfo

# Prevent warnings when using Jupyter
warnings.simplefilter("ignore")
pd.options.mode.chained_assignment = None


class TimeSeriesPipelineType(Enum):
    """
    Enum for type of pipeline to construct for time-series preprocessing.

    Full is a pipeline with all steps requested through AutoML settings.
    CV Reduced is a pipeline to be run on CV splits where only some steps need recomputing (e.g. STL Featurizer)
    """

    FULL = 1
    CV_REDUCED = 2


class TimeSeriesTransformer(AbstractTimeSeriesTransformer, FeaturizationInfoProvider):
    """Class for timeseries preprocess."""

    REMOVE_LAG_LEAD_WARN = "The lag-lead operator was removed due to memory limitation."
    REMOVE_ROLLING_WINDOW_WARN = "The rolling window operator was removed due to memory limitation."

    @staticmethod
    def _join_reusable_features_for_cv(ts_transformer_cv: 'TimeSeriesTransformer', X_cv: pd.DataFrame,
                                       ts_transformer_full: 'TimeSeriesTransformer',
                                       X_full: pd.DataFrame) -> pd.DataFrame:
        """
        Join dataframes from CV_REDUCED and FULL preprocessing pipelines.

        Context: During CV, some features must be recomputed on split sets while others can be reused
        from preprocessing on the whole training set. The goal here is to add the "reuseable" features
        to the output of CV preprocessing where the "non-reuseable" features have been recomputed.
        This method dynamically determines which features should be taken from the re-computed CV pipeline
        and which can be re-used from the FULL pipeline. It does this by finding the intersection of transforms
        from the reduced and full pipelines, then retrieving the set of features created by these overlapping
        transforms.
        This is a private utility method that should only be used in the described context.

        :param ts_transformer_cv: Fitted TimeSeriesTransformer containing reduced/subset pipeline
        :param X_cv: Output from a CV_REDUCED transform pipeline
        :param ts_transformer_full: Fitted TimeSeriesTransformer containing full pipeline
        :param X_full: Output from a FULL transform pipeline
        :return: Joined dataframe
        """
        assert ts_transformer_full.target_column_name == ts_transformer_cv.target_column_name, \
            'Transformer target column names must match'
        assert ts_transformer_full.grain_column_names == ts_transformer_cv.grain_column_names, \
            'Transformer grain column names must match'
        assert ts_transformer_full.time_column_name == ts_transformer_cv.time_column_name, \
            'Transformer time column names must match'
        assert ts_transformer_full.origin_column_name == ts_transformer_cv.origin_column_name, \
            'Transformer origin column names must match'

        feat_dict_full = ts_transformer_full._get_features_by_transform()
        feat_dict_cv = ts_transformer_cv._get_features_by_transform()

        assert all(trans in feat_dict_full for trans in feat_dict_cv), \
            'CV pipeline transforms must be a subset of FULL pipeline transforms'

        target_column_name = ts_transformer_full.target_column_name
        origin_column_name = ts_transformer_full.origin_column_name

        # Find the set of common transforms to both pipelines
        transforms_overlap = set(feat_dict_cv.keys()).intersection(set(feat_dict_full.keys()))
        feats_overlap = list()  # type: List[str]
        for trans in transforms_overlap:
            feats_overlap.extend(feat_dict_cv[trans])

        # Recompute features in the transform overlap and also the target
        feats_recompute = set(feats_overlap).union([target_column_name])

        # Drop recomputed columns from X_full prior to join
        X_temp = X_full.drop(columns=list(feats_recompute), errors='ignore')

        # If X_full has origin times and X_cv does not, temporarily move them out of the index.
        # If X_cv has origins, then X_full must also have origins, so don't need to handle reverse case
        cv_has_origin = origin_column_name in X_cv.index.names
        full_has_origin = origin_column_name in X_temp.index.names
        full_remove_origin = full_has_origin and (not cv_has_origin)
        if full_remove_origin:
            X_temp = X_temp.reset_index(origin_column_name)

        # Do the join using the indices as the keys
        # Join type is inner (important in cases where e.g. FULL pipeline includes NaN removal from Lag/RW features)
        cols_drop_cv = set(X_cv.columns) - feats_recompute
        X_cv_new = (X_cv.drop(columns=list(cols_drop_cv), errors='ignore')
                    .merge(X_temp, how='inner', left_index=True, right_index=True))

        # Put origins back in the index if they were removed before join
        if full_remove_origin:
            X_cv_new = X_cv_new.set_index(origin_column_name, append=True)

        return X_cv_new

    def __init__(self, pipeline_type: TimeSeriesPipelineType = TimeSeriesPipelineType.FULL,
                 logger: Optional[logging.Logger] = None, **kwargs: Any) -> None:
        """
        Construct a TimeSeriesTransformer.

        :param pipeline_type: Type of pipeline to construct. Either Full or Reduced for CV split featurizing
        :type pipeline_type: TimeSeriesPipelineType
        :param logger: The logger to be used in the pipeline.
        :param kwargs: dictionary contains metadata for TimeSeries.
                       time_column_name: The column containing dates.
                       grain_column_names: The set of columns defining the
                       multiple time series.
                       origin_column_name: latest date from which actual values
                       of all features are assumed to be known with certainty.
                       drop_column_names: The columns which will needs
                       to be removed from the data set.
                       group: the group column name.
        :type kwargs: dict
        """
        self._transforms = {}   # type: Dict[str, TransformerMixin]
        self.pipeline_type = pipeline_type  # type: TimeSeriesPipelineType

        self._max_horizon = TimeSeriesInternal.MAX_HORIZON_DEFAULT
        # Check if TimeSeries.MAX_HORIZON is not set to TimeSeries.AUTO.
        if isinstance(kwargs.get(TimeSeries.MAX_HORIZON, TimeSeriesInternal.MAX_HORIZON_DEFAULT), int):
            self._max_horizon = kwargs.get(TimeSeries.MAX_HORIZON, TimeSeriesInternal.MAX_HORIZON_DEFAULT)

        self.use_stl = kwargs.get(TimeSeries.USE_STL,
                                  TimeSeriesInternal.USE_STL_DEFAULT)
        if self.use_stl is not None and self.use_stl not in TimeSeriesInternal.STL_VALID_OPTIONS:
            raise ConfigException('{} setting must be None or one of the following: {}'.format(
                TimeSeries.USE_STL, TimeSeriesInternal.STL_VALID_OPTIONS))
        self.seasonality = kwargs.get(TimeSeries.SEASONALITY,
                                      TimeSeriesInternal.SEASONALITY_VALUE_DEFAULT)
        self.force_time_index_features = kwargs.get(TimeSeriesInternal.FORCE_TIME_INDEX_FEATURES_NAME,
                                                    TimeSeriesInternal.FORCE_TIME_INDEX_FEATURES_DEFAULT)
        self.time_index_non_holiday_features = []  # type: List[str]
        self._parameters = dict(kwargs)  # type: Dict[str, Any]
        super(TimeSeriesTransformer, self).__init__(logger, **kwargs)

    def _get_transformer_params(self,
                                cls: 'Type[AzureMLForecastTransformerBase]',
                                name: str,
                                **kwargs: Any) -> None:
        """
        Create the transformer if type cls and put it to the self._transforms with label name.

        :param cls: the class of transformer to be constructed.
        :type cls: type
        :param name: Transformer label.
        :type name: str
        :param kwargs: the dictionary of parameters to be parsed.
        :type kwargs: dict

        """
        rw = {}
        valid_args = inspect.getfullargspec(cls.__init__).args
        for k, v in kwargs.items():
            if k in valid_args:
                rw[k] = v

        self._transforms[name] = cls(**rw)

    def _construct_pre_processing_pipeline(self,
                                           tsdf: TimeSeriesDataFrame,
                                           drop_column_names: List[str]) -> AzureMLForecastPipeline:
        """Return the featurization pipeline."""
        from .forecasting_pipeline import AzureMLForecastPipeline
        from .grain_index_featurizer import GrainIndexFeaturizer
        from .time_series_imputer import TimeSeriesImputer
        from .time_index_featurizer import TimeIndexFeaturizer

        numerical_columns = [x for x in tsdf.select_dtypes(include=[np.number]).columns
                             if x not in drop_column_names]
        if self.target_column_name in numerical_columns:
            numerical_columns.remove(self.target_column_name)
        if self.original_order_column in numerical_columns:
            numerical_columns.remove(self.original_order_column)

        imputation_dict = {col: tsdf[col].median() for col in numerical_columns}
        impute_missing_numerical_values = TimeSeriesImputer(
            input_column=numerical_columns, value=imputation_dict, freq=self.freq, logger=self.logger)

        datetime_columns = [x for x in tsdf.select_dtypes(include=[np.datetime64]).columns
                            if x not in drop_column_names]
        fillna_imputer_ffill = TimeSeriesImputer(option='fillna', method='ffill',
                                                 input_column=datetime_columns,
                                                 freq=self.freq, logger=self.logger)
        fillna_imputer_bfill = TimeSeriesImputer(option='fillna', method='bfill',
                                                 input_column=datetime_columns,
                                                 freq=self.freq, logger=self.logger)
        # In forecasting destination date function, neither forward or backward will work
        # have to save the last non null value to impute
        # TODO: make both numeric and this imputation grain aware
        datetime_imputation_dict = {col: tsdf.loc[tsdf[col].last_valid_index()][col]
                                    for col in datetime_columns}
        datetime_imputer_final = TimeSeriesImputer(option='fillna',
                                                   input_column=datetime_columns,
                                                   value=datetime_imputation_dict,
                                                   freq=self.freq)

        # pipeline:
        # TODO: unify the imputers to support all data types
        default_pipeline = AzureMLForecastPipeline([
            (TimeSeriesInternal.MAKE_NUMERIC_NA_DUMMIES, MissingDummiesTransformer(numerical_columns)),
            (TimeSeriesInternal.IMPUTE_NA_NUMERIC_COLUMNS, impute_missing_numerical_values),
            (TimeSeriesInternal.IMPUTE_NA_FORWARD, fillna_imputer_ffill),
            (TimeSeriesInternal.IMPUTE_NA_BACKWARD, fillna_imputer_bfill),
            (TimeSeriesInternal.IMPUTE_NA_FINAL, datetime_imputer_final),
        ])

        # If desired, we need to create the transform which will drop the short series.
        if self.parameters.get(TimeSeries.SHORT_SERIES_HANDLING)\
                and self.pipeline_type == TimeSeriesPipelineType.FULL:
            params = self.parameters.copy()
            params[TimeSeries.MAX_HORIZON] = self.max_horizon
            default_pipeline.add_pipeline_step(TimeSeriesInternal.SHORT_SERIES_DROPPEER,
                                               ShortGrainDropper(logger=self.logger, **params))

        # After imputation we need to restore the data types using restore_dtypes_transformer RESTORE_DTYPES
        default_pipeline.add_pipeline_step(TimeSeriesInternal.RESTORE_DTYPES,
                                           RestoreDtypesTransformer(tsdf))

        # We introduce the STL transform, only if we need it after the imputation,
        # but before the lag lead operator and rolling window because STL does not support
        # origin time index.
        if self.use_stl is not None:
            only_season_feature = self.use_stl == TimeSeries.STL_OPTION_SEASON
            default_pipeline.add_pipeline_step(
                TimeSeriesInternal.MAKE_SEASONALITY_AND_TREND,
                STLFeaturizer(seasonal_feature_only=only_season_feature,
                              seasonality=self.seasonality,
                              logger=self.logger))

        # Return the pipeline after STL featurizer if it is for reduced CV featurization
        # (i.e. the output of a full pipeline will be re-used for other features like lag, RW, etc)
        if self.pipeline_type is TimeSeriesPipelineType.CV_REDUCED:
            return default_pipeline

        # Insert the max horizon featurizer to make horizon rows and horizon feature
        # Must be *before* lag and rolling window transforms
        if TimeSeriesInternal.LAG_LEAD_OPERATOR in self._transforms or \
           TimeSeriesInternal.ROLLING_WINDOW_OPERATOR in self._transforms:
            default_pipeline.add_pipeline_step(
                TimeSeriesInternal.MAX_HORIZON_FEATURIZER,
                MaxHorizonFeaturizer(self._max_horizon,
                                     origin_time_colname=self.origin_column_name,
                                     horizon_colname=TimeSeriesInternal.HORIZON_NAME))

        # Lag and rolling window transformer
        # To get the determined behavior sort the self._transforms.
        transforms_ordered = sorted(self._transforms.keys())
        for transform in transforms_ordered:
            # Add the transformer to the default pipeline
            default_pipeline.add_pipeline_step(transform, self._transforms[transform])

        # Don't apply grain featurizer when there is single time series
        if self.dummy_grain_column not in self.grain_column_names:
            grain_index_featurizer = GrainIndexFeaturizer(overwrite_columns=True, logger=self.logger)
            default_pipeline.add_pipeline_step(TimeSeriesInternal.MAKE_GRAIN_FEATURES, grain_index_featurizer)

        # If we have generated/have the category columns, we want to convert it to numerical values.
        # To avoid generation of 1000+ columns on some data sets.
        # NumericalizeTransformer is an alternative to the CategoryBinarizer: it will find the categorical
        # features and will turn them to integer numbers and this will allow to avoid detection of these
        # features by the CategoryBinarizer.
        default_pipeline.add_pipeline_step(TimeSeriesInternal.MAKE_CATEGORICALS_NUMERIC,
                                           NumericalizeTransformer(logger=self.logger))

        # We are applying TimeIndexFeaturizer transform after the NumericalizeTransformer because we want to
        # one hot encode holiday features.
        # Add step to preprocess datetime
        time_index_featurizer = TimeIndexFeaturizer(overwrite_columns=True, country_or_region=self.country_or_region,
                                                    freq=self.freq, datetime_columns=datetime_columns,
                                                    logger=self.logger,
                                                    force_feature_list=self.force_time_index_features)
        self.time_index_non_holiday_features = time_index_featurizer.preview_non_holiday_feature_names(tsdf)
        default_pipeline.add_pipeline_step(TimeSeriesInternal.MAKE_TIME_INDEX_FEATURES, time_index_featurizer)

        # Add step to preprocess categorical data
        default_pipeline.add_pipeline_step(TimeSeriesInternal.MAKE_CATEGORICALS_ONEHOT,
                                           CategoryBinarizer(logger=self.logger))

        return default_pipeline

    def _create_feature_transformer_graph(self, X: pd.DataFrame,
                                          y: Optional[DataSingleColumnInputType] = None) -> None:
        """
        Create the feature transformer graph from pipeline steps.

        The transformer graph is stored as a dictionary where keys are engineered feature names
        and values are sequences of raw feature name, transform pairs.
        """
        assert hasattr(self, 'pipeline') and getattr(self, 'pipeline') is not None, \
            'Missing or null pipeline. Call fit method first to create the pipeline.'
        # Convert X to a TimeSeriesDataFrame if it isn't one already
        if isinstance(X, TimeSeriesDataFrame):
            tsdf = X  # type: TimeSeriesDataFrame
        else:
            if y is None:
                assert self.target_column_name in X.columns, 'X must contain target column if y is not provided'
            X_safe = X
            if y is not None:
                X_safe = X_safe.assign(**{self.target_column_name: y})
            if (self.dummy_grain_column in self.grain_column_names) and (self.dummy_grain_column not in X.columns):
                X_safe = X_safe.assign(**{self.dummy_grain_column: self.dummy_grain_column})

            tsdf = self._create_tsdf_from_data(X_safe,
                                               time_column_name=self.time_column_name,
                                               target_column_name=self.target_column_name,
                                               grain_column_names=self.grain_column_names)

        graph = defaultdict(list)   # type: DefaultDict[str, List[List[Union[str, TransformerMixin]]]]

        def append_node(feature_from: str, feature_to: str, transformer: AutoMLTransformer) -> None:
            """Append a feature transformation to a graph node."""
            if feature_to in graph:
                graph[feature_to].append([feature_from, transformer])
            else:
                if feature_from in graph:
                    # Deep copy the feature's pre transformers
                    graph[feature_to] = copy.deepcopy(graph[feature_from])
                    graph[feature_to].append([feature_from, transformer])
                else:
                    graph[feature_to] = [[feature_from, transformer]]
        # self.pipeline cannot None, because it is populated during fit.
        assert(self.pipeline is not None)
        for name, transformer in self.pipeline._steps:
            if name == TimeSeriesInternal.MAKE_NUMERIC_NA_DUMMIES:
                for col in transformer.numerical_columns:
                    append_node(col, col + '_WASNULL', name)
            elif name == TimeSeriesInternal.IMPUTE_NA_NUMERIC_COLUMNS:
                for col in transformer.input_column:
                    append_node(col, col, name)
            elif name == TimeSeriesInternal.MAKE_TIME_INDEX_FEATURES:
                for col in transformer.preview_time_feature_names(tsdf):
                    append_node(tsdf.time_colname, col, name)
                for date_col in transformer.datetime_columns:
                    for dst in transformer._datetime_sub_feature_names:
                        append_node(date_col, date_col + "_" + dst, name)
            elif name == TimeSeriesInternal.MAKE_GRAIN_FEATURES:
                for col in tsdf.grain_colnames:
                    append_node(col, 'grain_' + col, name)
            elif name == TimeSeriesInternal.MAKE_CATEGORICALS_NUMERIC:
                for col in transformer._categories_by_col.keys():
                    append_node(col, col, name)
            elif name == TimeSeriesInternal.MAKE_CATEGORICALS_ONEHOT:
                for col in transformer._categories_by_col.keys():
                    for dst in transformer._categories_by_col[col]:
                        append_node(col, str(col) + '_' + str(dst), name)
            elif name == TimeSeriesInternal.MAX_HORIZON_FEATURIZER:
                for col in transformer.preview_column_names(tsdf):
                    append_node(tsdf.time_colname, col, name)
            elif name in [TimeSeriesInternal.LAG_LEAD_OPERATOR,
                          TimeSeriesInternal.ROLLING_WINDOW_OPERATOR]:
                for col in transformer.preview_column_names(tsdf):
                    if name == TimeSeriesInternal.LAG_LEAD_OPERATOR:
                        features = transformer.lags_to_construct.keys()
                    else:
                        features = transformer.transform_dict.values()
                    raw_feature = tsdf.ts_value_colname
                    for feature in features:
                        if col.startswith(feature):
                            raw_feature = feature
                    append_node(raw_feature, col, name)
            elif name == TimeSeriesInternal.MAKE_SEASONALITY_AND_TREND:
                raw_feature = tsdf.ts_value_colname
                for col in transformer.preview_column_names(tsdf):
                    append_node(raw_feature, col, name)

        self._feature_graph = graph

    def _create_feature_transformer_graph_if_not_set(self,
                                                     X: pd.DataFrame,
                                                     y: Optional[DataSingleColumnInputType] = None) -> None:
        """Create the feature transformer graph if it is not set as a TimeSeriesTranformer property."""
        if not hasattr(self, '_feature_graph'):
            self._create_feature_transformer_graph(X, y=y)

    def _get_features_by_transform(self) -> DefaultDict[str, List[str]]:
        """Get a dictionary of features indexed by TimeSeriesTransformer transform names."""
        assert hasattr(self, '_feature_graph'), 'TimeSeriesTransformer object does not have a feature graph'
        features_by_transform = defaultdict(list)  # type: DefaultDict[str, List[str]]

        for feature in self._feature_graph:
            for _, trans in self._feature_graph[feature]:
                trans_name = type(trans).__name__ if isinstance(trans, TransformerMixin) else trans
                features_by_transform[trans_name].append(feature)

        return features_by_transform

    def _generate_json_for_engineered_features(self, tsdf: TimeSeriesDataFrame) -> None:
        """
        Create the transformer json format for each engineered feature.

        :param tsdf: time series data frame
        """
        self._create_feature_transformer_graph(tsdf)

        if self.engineered_feature_names is None:
            # This can happen only if user invoked _generate_json_for_engineered_features
            # outside the transform function without setting engineered_feature_names.
            raise ConfigException("No feature were generated to build json.")

        graph = self._feature_graph
        for engineered_feature_name in self.engineered_feature_names or []:
            col_transformers = graph.get(engineered_feature_name, [])
            transformers = []   # type: List[_Transformer]
            val = ''
            for col, transformer in col_transformers:
                input_feature = col
                # for each engineered feature's transform path, only store the first transformer's
                # input which is raw feature name, other transformers' input are previous transformer
                if len(transformers) > 0:
                    input_feature = len(transformers)
                if transformer == TimeSeriesInternal.MAKE_NUMERIC_NA_DUMMIES:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.ImputationMarker,
                            operator=None,
                            feature_type=_FeatureType.Numeric,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.IMPUTE_NA_NUMERIC_COLUMNS:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.Imputer,
                            operator=_OperatorNames.Mean,
                            feature_type=_FeatureType.Numeric,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAKE_TIME_INDEX_FEATURES:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.DateTimeTransformer,
                            operator=None,
                            feature_type=_FeatureType.DateTime,
                            should_output=True)
                    )
                    val = engineered_feature_name
                elif transformer == TimeSeriesInternal.MAKE_GRAIN_FEATURES:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.GrainMarker,
                            operator=None,
                            feature_type=_FeatureType.Ignore,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAKE_CATEGORICALS_NUMERIC:
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.LabelEncoder,
                            operator=None,
                            feature_type=_FeatureType.Categorical,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAKE_CATEGORICALS_ONEHOT:
                    val = engineered_feature_name
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.OneHotEncoder,
                            operator=None,
                            feature_type=_FeatureType.Categorical,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAX_HORIZON_FEATURIZER:
                    val = engineered_feature_name
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.MaxHorizonFeaturizer,
                            operator=None,
                            feature_type=_FeatureType.DateTime,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.LAG_LEAD_OPERATOR:
                    # engineered_feature_name of lag operation is %target_col_name%_lags%size%%period"
                    # put the %size%%period% to val
                    val = engineered_feature_name[(len(col) + 4):]
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.Lag,
                            operator=None,
                            feature_type=_FeatureType.Numeric,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.ROLLING_WINDOW_OPERATOR:
                    # engineered_feature_name of rollingwindow operation is %target_col_name%_func%size%%period"
                    # put the %size%%period% to val
                    func_value = engineered_feature_name[len(col) + 1:].split("_", 2)
                    func = func_value[0]
                    val = func_value[1]
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.RollingWindow,
                            operator=func,
                            feature_type=_FeatureType.Numeric,
                            should_output=True)
                    )
                elif transformer == TimeSeriesInternal.MAKE_SEASONALITY_AND_TREND:
                    # engineered_feature_name of STL operation is %target_col_name%_seasonal"
                    transformers.append(
                        _Transformer(
                            parent_feature_list=[input_feature],
                            transformation_fnc=_SupportedTransformersInternal.STLFeaturizer,
                            operator=None,
                            feature_type=_FeatureType.Numeric,
                            should_output=True)
                    )

            feature_transformers = _FeatureTransformers(transformers)
            # Create the JSON object
            transformation_json = feature_transformers.encode_transformations_from_list()
            transformation_json._set_value_tag(val)
            self._engineered_feature_name_objects[engineered_feature_name] = transformation_json

    def _get_json_str_for_engineered_feature_name(self,
                                                  engineered_feature_name: str) -> str:
        """
        Return JSON string for engineered feature name.

        :param engineered_feature_name: Engineered feature name for
            whom JSON string is required
        :return: JSON string for engineered feature name
        """
        # If the JSON object is not valid, then return None
        if engineered_feature_name not in self._engineered_feature_name_objects:
            return json.dumps([])
        else:
            engineered_feature_name_json_obj = \
                cast(_FeatureTransformersAsJSONObject,
                     self._engineered_feature_name_objects[engineered_feature_name])._entire_transformation_json_data
            # Convert JSON into string and return
            return json.dumps(engineered_feature_name_json_obj)

    def get_json_strs_for_engineered_feature_names(self,
                                                   engi_feature_name_list: Optional[List[str]] = None) -> List[str]:
        """
        Return JSON string list for engineered feature names.

        :param engi_feature_name_list: Engineered feature names for
            whom JSON strings are required
        :return: JSON string list for engineered feature names
        """
        engineered_feature_names_json_str_list = []

        if engi_feature_name_list is None:
            engi_feature_name_list = self.get_engineered_feature_names()

        # Walk engineering feature name list and get the corresponding
        # JSON string
        for engineered_feature_name in cast(List[str], engi_feature_name_list):

            json_str = \
                self._get_json_str_for_engineered_feature_name(
                    engineered_feature_name)

            engineered_feature_names_json_str_list.append(json_str)

        # Return the list of JSON strings for engineered feature names
        return engineered_feature_names_json_str_list

    def get_featurization_summary(self) -> FeaturizationSummaryType:
        """
        Return the featurization summary for all the input features seen by TimeSeriesTransformer.

        :return: List of featurization summary for each input feature.
        """
        entire_featurization_summary = _RawFeatureFeaturizationInfo.get_coalesced_raw_feature_featurization_mapping(
            self._engineered_feature_name_objects)
        user_friendly_verion = []
        for featurization_summary in entire_featurization_summary:
            user_friendly_verion.append(featurization_summary.to_user_friendly_repr())
        return user_friendly_verion

    def _select_known_before_date(self, X: pd.DataFrame, date: pd.Timestamp,
                                  freq: pd.DateOffset) -> pd.DataFrame:
        """
        Select rows from X where all horizon dependent information is known prior to the requested date.

        This selection only makes sense for dataframes with origin times.
        """

        assert self.origin_column_name in X.index.names, "X doesn't contain origin times"

        # Need some special logic for lag features. Here, the latest known date isn't necessarily the origin time.
        # Lags are defined with respect to the origin, so latest known is actually the origin + (min(lag_orders) - 1)
        latest_known_date = date
        if len(self._transforms) == 1 and TimeSeriesInternal.LAG_LEAD_OPERATOR in self._transforms:
            lag_setting = self._transforms[TimeSeriesInternal.LAG_LEAD_OPERATOR].lags_to_construct

            # Lag orders may be ints or list of ints. Get orders as a list of lists so we can safely iterate
            lag_orders_list = [[lag] if not is_iterable_but_not_string(lag) else lag for lag in lag_setting.values()]

            # minimum lag order determines the latest date we can consider
            min_lag_order = min(chain(*lag_orders_list))
            latest_known_date += freq * (min_lag_order - 1)

        return X[X.index.get_level_values(self.origin_column_name) <= latest_known_date]

    def _select_latest_origin_dates(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Select rows from X with latest origin times within time-grain groups.

        Logic: Group X by time, grain -> Find latest origin in each group
        -> Return row containing latest origin for each group.
        """
        expected_lvls = [self.time_column_name] + self.grain_column_names + [self.origin_column_name]
        assert list(X.index.names) == expected_lvls, "X.index doesn't contain expected levels"

        keys = [self.time_column_name] + self.grain_column_names

        def get_origin_vals(df: pd.DataFrame) -> pd.DatetimeIndex:
            return df.index.get_level_values(self.origin_column_name)

        return (X.groupby(keys, group_keys=False)
                 .apply(lambda df: df[get_origin_vals(df) == get_origin_vals(df).max()]))

    def fit(self, X: pd.DataFrame, y: Optional[np.ndarray] = None) -> 'TimeSeriesTransformer':
        """
        Perform the raw data validation and identify the transformations to apply.

        :param X: Dataframe representing text, numerical or categorical input.
        :type X: pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray

        :return: DataTransform object.
        :raises: DataException for non-dataframe.
        """
        if isinstance(X, pd.DataFrame):
            # Replace auto parameters with the heuristic values.
            # max_horizon
            params_copy = self.parameters.copy()
            if self.parameters.get(TimeSeries.MAX_HORIZON) == TimeSeries.AUTO:
                if self.pipeline is None:
                    # Get heuristics only if we are fitting the first time.
                    self._max_horizon = get_heuristic_max_horison(X, self.time_column_name)
                params_copy[TimeSeries.MAX_HORIZON] = self._max_horizon

            # Make heuristics for lags and rolling window if needed.
            # Figure out if we need auto lags or rolling window.
            lags_to_construct = self.parameters.get(TimeSeriesInternal.LAGS_TO_CONSTRUCT)
            autolags = lags_to_construct is not None and lags_to_construct.get(
                TimeSeriesInternal.DUMMY_TARGET_COLUMN) == [TimeSeries.AUTO]
            autorw = (self.parameters.get(TimeSeriesInternal.WINDOW_SIZE) == TimeSeries.AUTO and
                      self.parameters.get(TimeSeriesInternal.TRANSFORM_DICT) is not None)
            # If we need automatic lags or rolling window, run the PACF analysis.
            if (autolags or autorw):
                if self.pipeline is None:
                    # If we are in the first fit, figure out the heuristics.
                    X[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y
                    lags, rw = analyze_pacf_per_grain(
                        X,
                        self.time_column_name,
                        TimeSeriesInternal.DUMMY_TARGET_COLUMN,
                        self.grain_column_names)
                    X.drop(TimeSeriesInternal.DUMMY_TARGET_COLUMN, axis=1, inplace=True)
                else:
                    # Else take what we already have. We are in the re fit mode.
                    lags_op = self.get_auto_lag()
                    if lags_op is None:
                        lags = 0
                    else:
                        lags = max(lags_op)
                    rw_op = self.get_auto_window_size()
                    if rw_op is None:
                        rw = 0
                    else:
                        rw = rw_op
                # FIXME: We need to design the EffectiveConfig which will include the
                # heuristic parameters, rather then swapping parameters here.
                # Swap lags and rw in the copied parameters if needed.
                if autolags:
                    if lags != 0:
                        params_copy[TimeSeriesInternal.LAGS_TO_CONSTRUCT] = {
                            self.target_column_name: [lag for lag in range(1, lags + 1)]
                        }
                    else:
                        del params_copy[TimeSeriesInternal.LAGS_TO_CONSTRUCT]

                if autorw:
                    if rw != 0:
                        params_copy[TimeSeriesInternal.WINDOW_SIZE] = rw
                    else:
                        del params_copy[TimeSeriesInternal.WINDOW_SIZE]

            # Create Lag lead operator or rolling window if needed.
            if (TimeSeriesInternal.LAGS_TO_CONSTRUCT in params_copy.keys()):
                # We need to backfill the cache to avoid problems with shape.
                params_copy['backfill_cache'] = True
                self._get_transformer_params(LagLeadOperator,
                                             TimeSeriesInternal.LAG_LEAD_OPERATOR,
                                             **params_copy)
            if (TimeSeriesInternal.WINDOW_SIZE in params_copy.keys() and
                    TimeSeriesInternal.TRANSFORM_DICT in params_copy.keys()):
                # We need to disable the horizon detection, because it is very slow on large data sets.
                params_copy['check_max_horizon'] = False
                # We need to backfill the cache to avoid problems with shape.
                params_copy['backfill_cache'] = True
                self._get_transformer_params(RollingWindow,
                                             TimeSeriesInternal.ROLLING_WINDOW_OPERATOR,
                                             **params_copy)

        # Override the parent class fit method to define if there is enough memory
        # for using LagLeadOperator and RollingWindow.
        self._remove_lag_lead_and_rw_maybe(X, y)
        super(TimeSeriesTransformer, self).fit(X, y)
        return self

    def transform(self,
                  df: DataInputType,
                  y: Optional[DataSingleColumnInputType] = None) -> pd.DataFrame:
        """
        Transform the input raw data with the transformations identified in fit stage.

        :param df: Dataframe representing text, numerical or categorical input.
        :type df: pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray

        :return: pandas.DataFrame

        """
        df = super(TimeSeriesTransformer, self).transform(df, y)
        # if we have applied STL transform, we need to make sure that leading np.NaNs are removed
        # from the trend.
        # self.pipeline cannot be None, because it is populated during fit.
        # calling transform before fit will raise the error before this place.
        assert(self.pipeline is not None)
        stl = self.pipeline.get_pipeline_step(TimeSeriesInternal.MAKE_SEASONALITY_AND_TREND)
        if stl:
            cols = stl.preview_column_names(target=self.target_column_name)
            for col in cols:
                if col.endswith(TimeSeriesInternal.STL_TREND_SUFFIX):
                    df = df[df[col].notnull()]

        # remove the possible nans that brought by lags
        check_columns = [col for col in df.columns.values if col != self.target_column_name]
        df.dropna(axis=0, inplace=True, subset=check_columns)
        return df

    def _remove_lag_lead_and_rw_maybe(self, df: pd.DataFrame, y: np.ndarray) -> None:
        """
        Remove the LagLead and or RollingWindow operator from the pipeline if there is not enough memory.

        :param df: DataFrame representing text, numerical or categorical input.
        :type df: pandas.DataFrame
        :param y: To match fit signature.
        :type y: numpy.ndarray

        """
        memory_per_df = memory_utilities.get_data_memory_size(df)
        if y is not None:
            memory_per_df += memory_utilities.get_data_memory_size(y)
        remove_ll_rw = True
        try:
            total_memory = memory_utilities.get_all_ram(self.logger)
            remove_ll_rw = TimeSeriesInternal.MEMORY_FRACTION_FOR_DF < self._max_horizon * memory_per_df / total_memory
        except Exception as e:
            if self.logger is not None:
                self.logger.warning(repr(e))
        if remove_ll_rw:
            self._remove_step_maybe(TimeSeriesInternal.LAG_LEAD_OPERATOR,
                                    TimeSeriesTransformer.REMOVE_LAG_LEAD_WARN)
            self._remove_step_maybe(TimeSeriesInternal.ROLLING_WINDOW_OPERATOR,
                                    TimeSeriesTransformer.REMOVE_ROLLING_WINDOW_WARN)

    def _remove_step_maybe(self, step_name: str, warning_text: str) -> None:
        """
        Safely remove the pipeline step.

        :param step_name: The name of a pipeline step.
        :type step_name: str
        :param warning_text: The warning text to be shown to user.
                             If None, no warning will be shown.
        :type warning_text: str

        """
        if step_name in self._transforms.keys():
            del self._transforms[step_name]
            if warning_text is not None:
                print(warning_text)

    def get_auto_lag(self) -> Optional[List[int]]:
        """
        Return the heuristically inferred lag.

        If lags were not defined as auto, return None.
        ClientException is raised if fit was not called.
        :return: Heuristically defined target lag or None.
        :raises: ClientException
        """
        self._raise_no_fit_exception_maybe()
        # We know that the pipeline is not None, because otherwise
        # _raise_no_fit_exception_maybe will throw the error.
        # mypy do not see this assertion.
        assert(self.pipeline is not None)
        lags = self.parameters.get(TimeSeriesInternal.LAGS_TO_CONSTRUCT)
        if lags is None:
            return None
        if lags.get(TimeSeriesInternal.DUMMY_TARGET_COLUMN) != [TimeSeries.AUTO]:
            return None
        lag_lead = self.pipeline.get_pipeline_step(TimeSeriesInternal.LAG_LEAD_OPERATOR)
        # Return learned lags.
        if lag_lead is None:
            return [0]
        else:
            return cast(List[int],
                        lag_lead.lags_to_construct.get(TimeSeriesInternal.DUMMY_TARGET_COLUMN))

    def get_auto_window_size(self) -> Optional[int]:
        """
        Return the auto rolling window size.

        If rolling window was not defined as auto, return None.
        ClientException is raised if fit was not called.
        :return: Heuristically defined rolling window size or None.
        :raises: ClientException
        """
        self._raise_no_fit_exception_maybe()
        # We know that the pipeline is not None, because otherwise
        # _raise_no_fit_exception_maybe will throw the error.
        # mypy do not see this assertion.
        assert(self.pipeline is not None)
        rw_size = self.parameters.get(TimeSeriesInternal.WINDOW_SIZE)
        if rw_size is None or rw_size != TimeSeries.AUTO:
            return None
        rolling_window = self.pipeline.get_pipeline_step(TimeSeriesInternal.ROLLING_WINDOW_OPERATOR)
        # Return learned window size.
        if rolling_window is None:
            return 0
        else:
            return cast(int, rolling_window.window_size)

    def get_auto_max_horizon(self) -> Optional[int]:
        """
        Return auto max horizon.

        If max_horizon was not defined as auto, return None.
        :return: Heuristically defined max_horizon or None.
        :raises: ClientException
        """
        self._raise_no_fit_exception_maybe()
        # We know that the pipeline is not None, because otherwise
        # _raise_no_fit_exception_maybe will throw the error.
        # mypy do not see this assertion.
        assert(self.pipeline is not None)
        max_horizon = self.parameters.get(TimeSeries.MAX_HORIZON)
        if max_horizon is None or max_horizon != TimeSeries.AUTO:
            return None
        # Return learned max_horison.
        return self.max_horizon

    @property
    def max_horizon(self) -> int:
        """Return the max horizon."""
        return self._max_horizon

    @property
    def parameters(self) -> Dict[str, Any]:
        """Return the parameters needed to reconstruct the time series transformer"""
        return self._parameters
