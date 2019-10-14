# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation.  All rights reserved.
# ---------------------------------------------------------
"""A module that contains some forecasting models: ARIMA, Prophet."""

from abc import abstractmethod
from typing import List, Tuple, Any, Optional, Dict, Union

import numpy as np
import pandas as pd
import logging

from automl.client.core.common import (
    forecasting_utils,
    time_series_data_frame,
    constants,
    model_wrappers,
    exceptions,
    utilities)


class _MultiGrainForecastBase:
    """
    Multi-grain forecast base class.

    Enables multi-grain fit and predict on learners that normally can only operate on a single timeseries.
    """

    def __init__(self,
                 timeseries_param_dict: Dict[str, Any]):
        self.timeseries_param_dict = timeseries_param_dict
        self.time_column_name = self.timeseries_param_dict[constants.TimeSeries.TIME_COLUMN_NAME]
        self.grain_column_names = self.timeseries_param_dict.get(constants.TimeSeries.GRAIN_COLUMN_NAMES, [])
        self.grain_column_names = [constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] if \
            self.grain_column_names is None or len(self.grain_column_names) == 0 else self.grain_column_names
        self.drop_column_names = self.timeseries_param_dict.get(constants.TimeSeries.DROP_COLUMN_NAMES, []) or []

        # model state
        self._grain_levels = []  # type: List[Tuple[str]]
        self._models = {}  # type: Dict[Tuple[str], Any]
        self._last_observation_dates = {}  # type: Dict[Tuple[str], pd.Timestamp]
        self._first_observation_dates = {}  # type: Dict[Tuple[str], pd.Timestamp]
        self._freq = None  # type: Optional[pd.DateOffset]
        self._is_fit = False

        # what to predict
        self._quantiles = [.5]

    # TODO: duplicates code from RegressionPipeline
    # /src/automl_client_core_runtime/automl/client/core/runtime/model_wrappers.py
    # Perhaps we should make a QuantileMixin.
    @property
    def quantiles(self) -> List[float]:
        """Quantiles for the model to predict."""
        return self._quantiles

    @quantiles.setter
    def quantiles(self, quantiles: Union[float, List[float]]) -> None:
        if not isinstance(quantiles, list):
            quantiles = [quantiles]

        for quant in quantiles:
            if quant == 0:
                raise ValueError("Quantile 0 is not supported.")
            if quant == 1:
                raise ValueError("Quantile 1 is not supported.")
            if quant < 0 or quant > 1:
                raise ValueError("Quantiles must be strictly less than 1 and greater than 0.")

        self._quantiles = quantiles

    def fit(self,
            X: pd.DataFrame,
            y: np.ndarray,
            **kwargs: Any) -> None:
        """Fit the model.

        :param X: Training data.
        :type X: pd.DataFrame
        :param y: Training label
        :type y: np.ndarray
        :return: Nothing
        :rtype: None
        """
        tsdf = self._construct_tsdf(X, y)

        tsdf_bygrain = tsdf.groupby_grain()
        self._grain_levels = list(tsdf_bygrain.groups)

        # Initialize the models and state variables
        self._models = {lvl: None for lvl in self._grain_levels}
        self._last_observation_dates = {
            lvl: None for lvl in self._grain_levels}
        self._first_observation_dates = {
            lvl: None for lvl in self._grain_levels}

        for lvl, series_frame in tsdf_bygrain:
            self._fit_single_grain(lvl, series_frame, tsdf.time_colname)

        self._freq = tsdf.infer_freq()
        self._is_fit = True

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self._is_fit:
            raise exceptions.UntrainedModelException()

        tsdf = self._construct_tsdf(X)

        max_horizons = self._get_forecast_horizons(tsdf)
        # Make a dataframe of forecasts
        fcast_df = self._get_forecast(tsdf, max_horizons)

        # Get rows containing in-sample data if any
        in_sample_data = pd.DataFrame()
        for g, X_group in tsdf.groupby_grain():
            if g in self._grain_levels:
                in_sample_data = pd.concat([in_sample_data,
                                            X_group.loc[X_group.time_index <= self._last_observation_dates[g]]])
        # Get fitted results for in-sample data
        if in_sample_data.shape[0] > 0:
            in_sample_fitted = self._fit_in_sample(in_sample_data)
            in_sample_fitted = in_sample_fitted.loc[:, fcast_df.columns]
            fcast_df = pd.concat([in_sample_fitted, fcast_df])

        # We're going to join the forecasts to the input - but first:
        # Convert X to a plain data frame and drop the prediction
        #  columns if they already exist
        point_name = constants.TimeSeriesInternal.DUMMY_PREDICT_COLUMN
        X_df = pd.DataFrame(tsdf, copy=False).drop(axis=1,
                                                   labels=[point_name],
                                                   errors='ignore')

        # Left join the forecasts into the input;
        #  the join is on the index levels
        pred_df = X_df.merge(fcast_df, how='left',
                             left_index=True, right_index=True)

        return pred_df[constants.TimeSeriesInternal.DUMMY_PREDICT_COLUMN].values

    def _construct_tsdf(self, X: pd.DataFrame, y: np.ndarray = None) -> time_series_data_frame.TimeSeriesDataFrame:
        X = X.copy()
        if self.grain_column_names == [constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN]:
            X[constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN

        tsdf_kwargs = {'grain_colnames': self.grain_column_names}
        if y is not None:
            X[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y
            tsdf_kwargs['ts_value_colname'] = constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN

        tsdf = time_series_data_frame.TimeSeriesDataFrame(X,
                                                          self.time_column_name,
                                                          **tsdf_kwargs)

        return tsdf

    def _fit_in_sample(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Return the fitted values from a the RecursiveForecaster model.

        :param X:
            A TimeSeriesDataFrame defining the data for which fitted values
            are desired.  Inputting the same data used to fit the model will
            return all fitted data.
        :type X: TimeSeriesDataFrame

        :Returns:
            a ForecastDataFrame containing the fitted values in `pred_point`.
        """
        point_name = constants.TimeSeriesInternal.DUMMY_PREDICT_COLUMN
        origin_name = constants.TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME

        fitted_df = pd.DataFrame()
        for g, X_grain in X.groupby_grain():
            origin_time = self._last_observation_dates[g]
            fitted = self._fit_in_sample_single_grain_impl(self._models[g], g, X_grain)
            assign_dict = {origin_name: origin_time,
                           point_name: fitted}
            X_grain = X_grain.assign(**assign_dict)

            fitted_df = pd.concat([fitted_df, X_grain])

        fitted_df = fitted_df.loc[X.index, :]

        return fitted_df

    def _get_forecast_horizons(self, X: time_series_data_frame.TimeSeriesDataFrame) -> Dict[Tuple[Any], int]:
        """
        Find maximum horizons to forecast in the prediction frame X.

        Returns a dictionary, grain -> max horizon.
        Horizons are calculated relative to the latest training
        dates for each grain in X.
        If X has a grain that isn't present in the training data,
        this method returns a zero for that grain.
        """
        # Internal function for getting horizon for a single grain

        import warnings

        def horizon_by_grain(gr, Xgr):
            try:
                horizon = len(pd.date_range(start=self._last_observation_dates[gr],
                                            end=Xgr.time_index.max(),
                                            freq=self._freq)) - 1
                # -1 because this will INCLUDE the
                # last obs date
            except KeyError:
                horizon = 0

            return horizon
        # ------------------------------------------

        fcast_horizon = {gr: horizon_by_grain(gr, Xgr)
                         for gr, Xgr in X.groupby_grain()}

        negatives = [h <= 0 for h in list(fcast_horizon.values())]
        if any(negatives):
            warnings.warn(('Non-positive forecast horizons detected. Check data for time '
                           'overlap between train and test and/or grains in test data '
                           'that are not present in training data. Failures may occur.'))

        return fcast_horizon

    def _get_forecast(self,
                      X: time_series_data_frame.TimeSeriesDataFrame,
                      max_horizon: Dict[Tuple[Any], int]) -> pd.DataFrame:
        """
        Generate forecasts up to max_horizon for each grain in X.

        The max_horizon parameter can be a single integer or
        a dictionary mapping each grain in X to an integer.

        Returns a pandas DataFrame. The index of this data frame
        will have the same levels as the input, X.
        The ouput will have the following:
        time, grain(s), origin time, point forecast.
        """
        # Get column names from X
        point_name = constants.TimeSeriesInternal.DUMMY_PREDICT_COLUMN
        origin_time_colname = constants.TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME

        grouped = X.groupby_grain()

        # Make max_horizon forecasts for each grain
        # Note: the whole prediction dataframe needs to be passed,
        # not just the grain name.

        fcast_df = pd.concat([
            self._get_forecast_single_grain(gr,
                                            grain_ctx.loc[grain_ctx.time_index > self._last_observation_dates[gr]],
                                            max_horizon[gr],
                                            X.time_colname,
                                            X.grain_colnames,
                                            origin_time_colname,
                                            point_name)
            for gr, grain_ctx in grouped])

        return fcast_df.set_index(X.index.names)

    def _get_forecast_single_grain(self,
                                   grain_level: Tuple[str],
                                   grain_ctx: pd.DataFrame,
                                   max_horizon: int,
                                   time_colname: str,
                                   grain_colnames: List[str],
                                   origin_time_colname: str,
                                   pred_point_colname: str) -> pd.DataFrame:
        """
        Generate forecasts up to max_horizon for a single grain.

        Returns a plain pandas Dataframe with the following columns:
        time, grain(s), origin time, point forecast,
        distribution forecast (optional).
        """
        if grain_level not in self._grain_levels or not self._models[grain_level]:

            raise exceptions.DataException(model_wrappers.ForecastingPipelineWrapper.FATAL_NO_GRAIN_IN_TRAIN)
        # ---------------------------------------------------------------

        # Origin date/time is the latest training date, by definition

        # Note: this does not support the newer forecast interface which
        # allows using a training model away from training data as long
        # as sufficient context is provided.  origin data should instead
        # be computed from the prediction context dataframe (X).
        origin_date = self._last_observation_dates[grain_level]

        # Retrieve the trained model and make a point forecast
        if max_horizon <= 0:
            fcast_dict = {time_colname: np.empty(0),
                          origin_time_colname: np.empty(0),
                          pred_point_colname: np.empty(0)}
        else:
            trained_model = self._models[grain_level]
            point_fcast = self._get_forecast_single_grain_impl(trained_model,
                                                               max_horizon,
                                                               grain_level,
                                                               grain_ctx)

            # Construct the time axis that aligns with the forecasts
            fcast_dates = grain_ctx.index.get_level_values(self.time_column_name)
            fcast_dict = {time_colname: fcast_dates,
                          origin_time_colname: origin_date,
                          pred_point_colname: point_fcast}

        if grain_colnames is not None:
            fcast_dict.update(forecasting_utils.grain_level_to_dict(grain_colnames,
                                                                    grain_level))
        return pd.DataFrame(fcast_dict)

    def _fit_single_grain(self,
                          lvl: Tuple[Any],
                          series_frame: time_series_data_frame.TimeSeriesDataFrame,
                          time_colname: str) -> None:
        """
        Train a single series.

        lvl, series_frame - indicate the grain and the actual series data.
        """
        series_frame.sort_index()
        # series_values = series_frame.ts_value.values
        self._models[lvl] = self._fit_single_grain_impl(series_frame, lvl)

        # Gather the last observation date if time_colname is set
        self._last_observation_dates[lvl] = series_frame.time_index.max()
        self._first_observation_dates[lvl] = series_frame.time_index.min()

    @abstractmethod
    def _fit_in_sample_single_grain_impl(self,
                                         model: Any,
                                         grain_level: Tuple[Any],
                                         X_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """
        Return the fitted in-sample values from a model.

        :param model:
            is an object representation of a model. It is the
            object returned by the _fit_single_grain_impl method.

        :param grain_level:
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting. See ets.py for examples.
        :param X_grain:
            the context data for the in-sample prediction.

        :param start:
            starting frame of the in sample prediction.

        :param end:
            end frame of the in sample prediction.

        :Returns:
            a 1-D numpy array of fitted values for the training data. The data are
            assumed to be in chronological order
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_forecast_single_grain_impl(self,
                                        model: Any,
                                        max_horizon: int,
                                        grain_level: Tuple[Any],
                                        X_pred_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """
        Return the forecasted value for a single grain.

        :param model:
            trained model.
        :param max_horizon:
            int that represents the max horizon.
        :param grain_level:
            tuple that identifies the timeseries the model belongs to.
        :param X_pred_grain
            a dataframe containing the prediction context
        :Returns:
            a 1-D numpy array of fitted values for the training data. The data are
            assumed to be in chronological order
        """
        raise NotImplementedError

    @abstractmethod
    def _fit_single_grain_impl(self,
                               series_values: time_series_data_frame.TimeSeriesDataFrame,
                               grain_level: Tuple[Any]) -> Any:
        """
        Return a fitted model for a single timeseries.

        :param series_values:
            an array that represents the timeseries.
        :param grain_level:
            tuple that identifies the timeseries the model belongs to.
        :Returns:
            a model object that can be used to make predictions.
        """
        raise NotImplementedError


class AutoArima(_MultiGrainForecastBase):
    """AutoArima multigrain forecasting model."""

    def __init__(self, **kwargs):
        """Create an autoarima multi-grain forecasting model."""
        import pmdarima
        self.pmdarima = pmdarima

        timeseries_param_dict = kwargs[constants.TimeSeriesInternal.TIMESERIES_PARAM_DICT]
        super().__init__(timeseries_param_dict)

    def __getstate__(self):
        """Get state for pickle. Removes the pmdarima module object."""
        state = self.__dict__.copy()
        del state['pmdarima']
        return state

    def __setstate__(self, state):
        """Set state for pickle. Adds back the pmdarima module object."""
        self.__dict__.update(state)
        import pmdarima
        self.pmdarima = pmdarima

    def _fit_in_sample_single_grain_impl(self,
                                         model: Any,
                                         grain_level: Tuple[Any],
                                         X_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        date_filter = X_grain.time_index.values
        date_argmax = date_filter.argmax()
        date_range = pd.date_range(
            start=self._first_observation_dates[grain_level],
            end=date_filter[date_argmax],
            freq=self._freq)

        index = np.searchsorted(date_range, date_filter)
        pred = model.predict_in_sample(start=0, end=date_range.shape[0])

        return pred[index]

    def _get_forecast_single_grain_impl(self,
                                        model: Any,
                                        max_horizon: int,
                                        grain_level: Tuple[Any],
                                        X_pred_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:

        # ARIMA (unlike Prophet) needs to have a meaningful max horizon
        if max_horizon <= 0:
            raise exceptions.DataException(model_wrappers.ForecastingPipelineWrapper.FATAL_NONPOSITIVE_HORIZON)

        if len(X_pred_grain.columns) > 1:
            import warnings
            warnings.warn('ARIMA(not-X) ignoring extra features, only predicting from the target')

        pred = model.predict(n_periods=int(max_horizon))

        date_filter = X_pred_grain.time_index.values
        date_min = date_filter.min()
        date_range = pd.date_range(start=date_min, periods=max_horizon, freq=self._freq)
        index = np.searchsorted(date_range, date_filter)

        return pred[index]

    def _fit_single_grain_impl(self, X_pred_grain: pd.DataFrame, grain_level: Tuple[str]) -> Any:

        # Let's warn for now, eventually we'll get the metadata on what the
        # target column is (if different from dummy) and then we can decide
        #  to ignore the rest or incorporate into ARIMAX
        if len(X_pred_grain.columns) > 1:
            import warnings
            warnings.warn('ARIMA can only predict from training data forward and does not take extra features')

        series_values = X_pred_grain[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].values.astype(float)
        model = self.pmdarima.auto_arima(series_values, error_action="ignore")
        return model


class ProphetModel(_MultiGrainForecastBase):
    """Prophet multigrain forecasting model."""

    def __init__(self, **kwargs: Any):
        """
        Construct an instance of the Prophet forecasting model.

        Accepts external regressors, which must be numeric-encoded
        (using LabelEncode, OneHotEncode, whatever, but not actual categoricals).

        Prophet parameters are accepted as a dictionary passed as a kwarg with key
        'prophet_param_dict' (or what `constants.TimeSeriesInternal.PROPHET_PARAM_DICT` says)
        and value being the actual dictionary of Prophet parameters (?help Prophet)
        """
        self.fbprophet = ProphetModel._get_fbprophet()

        timeseries_param_dict = kwargs[constants.TimeSeriesInternal.TIMESERIES_PARAM_DICT]
        super().__init__(timeseries_param_dict)

        self.prophet_param_dict = {}    # type: Dict[str, str]
        if constants.TimeSeriesInternal.PROPHET_PARAM_DICT in kwargs.keys():
            self.prophet_param_dict = kwargs[constants.TimeSeriesInternal.PROPHET_PARAM_DICT]

        # for saving the prediction intervals
        self._pred_intervals = dict()   # type: Dict[float, Any]

    def __getstate__(self):
        """Get state for pickle. Removes the fbprophet module object."""
        state = self.__dict__.copy()
        del state['fbprophet']
        return state

    def __setstate__(self, state):
        """Set state for pickle. Adds back the fbprophet module object."""
        self.__dict__.update(state)
        self.fbprophet = ProphetModel._get_fbprophet()

    @staticmethod
    def _get_fbprophet():
        class _NoPlotlyFilter(logging.Filter):
            def filter(self, record):
                return not record.getMessage() == 'Importing plotly failed. Interactive plots will not work.'

        logger = logging.getLogger('fbprophet')
        logger.addFilter(_NoPlotlyFilter())
        import fbprophet
        return fbprophet

    def _fit_in_sample_single_grain_impl(self,
                                         model: Any,
                                         grain_level: Tuple[Any],
                                         X_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        fitted = self._get_forecast_single_grain_impl(model, 0, grain_level, X_grain)
        return fitted

    def _get_forecast_single_grain_impl(self,
                                        model: Any,
                                        max_horizon: int,
                                        grain_level: Tuple[Any],
                                        X_pred_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """
        Forecast from Prophet model.

        Respects the X_pred_grain parameter, rather than the max_horizon parameter.
        """
        df = pd.DataFrame(X_pred_grain.copy())
        if constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN in df.columns and \
                constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN in df.index.names:
            df.drop(constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN, axis=1, inplace=True)

        df.reset_index(inplace=True)

        future_feats = df.rename(columns={self.time_column_name: 'ds'})
        assert('y' not in future_feats.columns)
        assert('ds' in future_feats.columns)

        # grain = tuple(df.iloc[0][self.grain_column_names])
        # print("INFO: Scoring Prophet on " + str(grain))

        # TODO: how do forecast with Prophet if the user provides recent values
        # of y in a recent context?

        preds = model.predict(future_feats)

        # TODO: save the effects from the output.  The effect is defined as:
        # "yhat is <effect> higher due to the actual value of the extra
        # regressor
        # than it would be with the "baseline" value of the regressor
        # (which would be the mean if it was standardized as by default).

        # for predict_quantiles, predictive_samples() should be used instead of
        # predict,
        # and quantiles computed on that output

        if len(self._quantiles) == 1 and self._quantiles[0] == 0.5:
            if not X_pred_grain.time_index.is_monotonic:
                # if the input was not sorted, prophet will sort it for us.
                # we need to un-do the reordering in this case.
                index = X_pred_grain.time_index.values.argsort().argsort()
                return preds['yhat'].values[index]
            else:
                return preds['yhat'].values
        else:
            raise NotImplementedError("Quantile forecasts from Prophet are not yet supported")

    def _fit_single_grain_impl(self,
                               series_frame: pd.DataFrame,
                               grain_level: Tuple[str]) -> Any:
        """Fit prophet model on one grain."""
        # get the data in the shape prophet expects: 'ds' for time and 'y' for
        # target

        # also, series_frame is a TSDF pandas dataframe with time and grain in
        # multiindex
        df = pd.DataFrame(series_frame.copy())
        if constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN in df.columns and \
                constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN in df.index.names:
            df.drop(constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN, axis=1, inplace=True)

        df.reset_index(inplace=True)
        df.rename(columns={self.time_column_name: 'ds',
                           constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN: 'y'},
                  inplace=True)

        assert('ds' in df.columns)
        assert('y' in df.columns)

        cols_to_ignore = ['ds', 'y'] + self.grain_column_names + self.drop_column_names
        list_of_features = [x for x in df.columns if x not in cols_to_ignore]
        # grain = tuple(df.iloc[0][self.grain_column_names])
        # print("INFO: Fitting Prophet on " + str(grain)) # doesn't print anyway even with pytest -s

        # for tuning, let's try playing with some propher parameters
        self.prophet_param_dict['seasonality_mode'] = 'multiplicative'

        model = self.fbprophet.Prophet(**self.prophet_param_dict)
        if len(list_of_features) > 0:
            for feat in list_of_features:
                model.add_regressor(feat)

        # Catch the FutureWarning from Prophet
        with utilities.suppress_stdout_stderr():
            model.fit(df)

        return model
