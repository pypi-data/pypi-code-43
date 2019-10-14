# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module to wrap NimbusML models."""
from typing import Any, Dict, Optional, Union
import os
import tempfile

import numpy as np

import sklearn
from sklearn.base import (BaseEstimator, ClassifierMixin, RegressorMixin,
                          TransformerMixin, clone)
from sklearn.utils.multiclass import unique_labels

import azureml.dataprep as dprep

from automl.client.core.common.exceptions import ClientException
from automl.client.core.common.exceptions import ConfigException
from automl.client.core.common.exceptions import FitException
from automl.client.core.runtime.model_wrappers import _AbstractModelWrapper
try:
    import nimbusml as nml
    import nimbusml.linear_model as nml_linear
    import nimbusml.multiclass as nml_multiclass
    from nimbusml.internal.core.base_pipeline_item import BasePipelineItem
    nimbusml_present = True
except ImportError:
    nimbusml_present = False

if nimbusml_present:
    class NimbusMlWrapperBase(_AbstractModelWrapper):
        """
        NimbusML base class.

        Contains code common to multiple NumbusML learners.
        """

        SERIALIZED_MODEL_STATE_KEY = "_serialized_model_"

        def get_model(self):
            """
            Return NimbusML model.

            :return: Returns self.
            """
            return self

        def get_random_state(self, args: Dict[str, Any]) -> Any:
            """
            Get and remove the random state from args.

            :param args: parameter dictionary.
            :type args: dict
            :param y: Input target values.
            :return: Random state.
            """
            random_state = args.pop('random_state', None)

            for argname in ['n_jobs', 'model', 'steps']:
                args.pop(argname, None)

            # The RandomState class is not supported by Pipeline.
            if isinstance(random_state, np.random.RandomState):
                random_state = None

            return random_state

    class NimbusMlPipelineWrapper(nml.Pipeline, NimbusMlWrapperBase):
        """Wrapper for a NimbusML Pipeline to make predict/predict_proba API follow SciKit return types."""

        def __init__(self, steps=None, **kwargs):
            """
            Initialize NimbusML Pipeline wrapper class.

            :param steps:
                List of (name, transform) tuples (implementing fit/transform) that are chained.
            :type steps: List of Tuple.
            """
            self.classes_ = None
            super(NimbusMlPipelineWrapper, self).__init__(steps=steps, **kwargs)  # type: ignore

        def fit(self, training_data, y=None, **kwargs):
            """Fit the Pipeline."""
            try:
                if isinstance(training_data, dprep.Dataflow):
                    # if training_data is dataflow, label column is already included
                    dprep_data_stream = nml.DprepDataStream(training_data)
                    result = super(NimbusMlPipelineWrapper, self).fit(dprep_data_stream, **kwargs)
                else:
                    result = super(NimbusMlPipelineWrapper, self).fit(training_data, y, **kwargs)

                    if self.last_node.type == NimbusMlClassifierMixin._estimator_type:
                        classes = getattr(self, "classes_", None)
                        if classes is None and y is not None:
                            classes = unique_labels(y)
                        self.classes_ = classes
                return result
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="NimbusML")

        def predict(self, X, *args, **kwargs):
            """Apply transforms to the data, and predict with the final estimator."""
            if isinstance(X, dprep.Dataflow):
                X = nml.DprepDataStream(X)
            projected_column = None
            if self.last_node.type == NimbusMlClassifierMixin._estimator_type:
                projected_column = "PredictedLabel"
            elif self.last_node.type == NimbusMlRegressorMixin._estimator_type:
                projected_column = "Score"
            else:
                raise ConfigException("Unsupported nimbusml pipeline type")

            try:
                return super(NimbusMlPipelineWrapper, self).predict(X, *args, **kwargs)[projected_column].values
            except Exception as e:
                raise ClientException.from_exception(e, has_pii=True)

        def predict_proba(self, X, verbose=0, **kwargs):
            """Apply transforms to the data and predict class probabilities using the final estimator."""
            if isinstance(X, dprep.Dataflow):
                X = nml.DprepDataStream(X)

            try:
                return super(NimbusMlPipelineWrapper, self).predict_proba(X=X, verbose=verbose, **kwargs)
            except Exception as e:
                raise ClientException.from_exception(e, has_pii=True)

    class NimbusMlLearnerMixin(BasePipelineItem):
        """Base class for all NimbusML learners."""

        def get_params(self, **kwargs):
            """Return parameters for the learner."""
            if hasattr(self, 'params'):
                return self.params
            return super().get_params(**kwargs)

    class NimbusMlClassifierMixin(NimbusMlLearnerMixin, NimbusMlWrapperBase, ClassifierMixin):
        """Base class for all NimbusML classifiers, implementing common functionality."""

        def fit(self, X, y, **kwargs):
            """Fit method for a NimbusML classfier."""
            try:
                super().fit(X, y, **kwargs)
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="NimbusML")
            return self

        def predict(self, X, *args, **kwargs):
            """
            Prediction function for a NimbusML Classifier model.

            :param X: Input data.
            :type X: numpy.ndarray
            :return: Prediction values from a NimbusML Classifier model.
            """
            try:
                return super().predict(X, *args, **kwargs).values
            except Exception as e:
                raise ClientException.from_exception(e, has_pii=True)

    class NimbusMlRegressorMixin(NimbusMlLearnerMixin, NimbusMlWrapperBase, RegressorMixin):
        """Base class for all NimbusML regressors, implementing common functionality."""

        def fit(self, X, y, **kwargs):
            """Fit method for a NimbusML regressor."""
            if 'verbose' not in kwargs:
                kwargs['verbose'] = 0

            try:
                super().fit(X, y, **kwargs)
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="NimbusML")
            return self

        def predict(self, X, *args, **kwargs):
            """
            Prediction function for a NimbusML Regressor model.

            :param X: Input data.
            :return: Prediction values from a NimbusML Regressor model.
            """
            try:
                return super().predict(X, *args, **kwargs).values
            except Exception as e:
                raise ClientException.from_exception(e, has_pii=True)

    class NimbusMlAveragedPerceptronClassifier(NimbusMlClassifierMixin):
        """
        NimbusML Averaged Perceptron Classifier class usable only in SciKit pipelines.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number generator;
            If RandomState instance, random_state is the random number generator;
            If None, the random number generator is the RandomState instance used
            by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://docs.microsoft.com
            /en-us/python/api/nimbusml/nimbusml.linear_model.averagedperceptronbinaryclassifier
            for more parameters.
        """

        def __init__(self,
                     random_state: Optional[Union[int, np.random.RandomState]] = 0,
                     n_jobs: int = 1,
                     **kwargs: Any) -> None:
            """
            Initialize NimbusML Averaged Perceptron Classifier class usable only in SciKit pipelines.

            :param random_state:
                RandomState instance or None, optional (default=None)
                If int, random_state is the seed used by the random number generator;
                If RandomState instance, random_state is the random number generator;
                If None, the random number generator is the RandomState instance used
                by `np.random`.
            :type random_state: int or RandomState
            :param n_jobs: Number of parallel threads.
            :type n_jobs: int
            :param kwargs: Other parameters
                Check https://docs.microsoft.com
                /en-us/python/api/nimbusml/nimbusml.linear_model.averagedperceptronbinaryclassifier
                for more parameters.
            """
            self.params = kwargs
            self.classes_ = None
            self.model = None
            self.type = NimbusMlClassifierMixin._estimator_type

        def fit(self, X, y, **kwargs):
            """Fit method for the NimbusMlAveragedPerceptronClassifier."""
            args = dict(self.params)
            nml_model = nml_linear.AveragedPerceptronBinaryClassifier(**args)
            if len(unique_labels(y)) > 2:
                # predict_proba returns classes in the order of their indexes in string order.
                nml_model = nml_multiclass.OneVsRestClassifier(nml_model)

            if 'verbose' not in kwargs:
                kwargs['verbose'] = 0

            try:
                nml_model.fit(X, y, **kwargs)
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="NimbusML")
            self.model = nml_model
            self.classes_ = self.model.classes_
            return self

        def predict(self, X):
            """
            Prediction function for NimbusML Averaged Perceptron Classifier model.

            :param X: Input data.
            :type X: numpy.ndarray
            :return: Prediction values from NimbusML Averaged Perceptron Classifier model.
            """
            if self.model is None:
                raise sklearn.exceptions.NotFittedError()
            try:
                return self.model.predict(X).values
            except Exception as e:
                raise ClientException.from_exception(e, has_pii=True)

        def predict_proba(self, X):
            """
            Prediction class probabilities for X for NimbusML Averaged Perceptron Classifier model.

            :param X: Input data.
            :type X: numpy.ndarray
            :return: Prediction probability values from NimbusML Averaged Perceptron Classifier model.
            """
            if self.model is None:
                raise sklearn.exceptions.NotFittedError()
            try:
                return self.model.predict_proba(X)
            except Exception as e:
                raise ClientException.from_exception(e, has_pii=True)

        def get_model(self):
            """
            Return NimbusML model.

            :return: Returns wrapped Nimbus ML model.
            """
            return self.model

        def _get_node(self, **all_args):
            pass

    class AveragedPerceptronBinaryClassifier(NimbusMlClassifierMixin, nml_linear.AveragedPerceptronBinaryClassifier):
        """
        NimbusML Averaged Perceptron Binary Classifier class that can be used within Nimbus pipelines.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number generator;
            If RandomState instance, random_state is the random number generator;
            If None, the random number generator is the RandomState instance used
            by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://docs.microsoft.com
            /en-us/python/api/nimbusml/nimbusml.linear_model.averagedperceptronbinaryclassifier
            for more parameters.
        """

        def __init__(self,
                     random_state: Optional[Union[int, np.random.RandomState]] = 0,
                     n_jobs: int = 1,
                     **kwargs: Any) -> None:
            """
            Initialize NimbusML Averaged Perceptron Binary Classifier class that can be used within Nimbus pipelines.

            :param random_state:
                RandomState instance or None, optional (default=None)
                If int, random_state is the seed used by the random number generator;
                If RandomState instance, random_state is the random number generator;
                If None, the random number generator is the RandomState instance used
                by `np.random`.
            :type random_state: int or RandomState
            :param n_jobs: Number of parallel threads.
            :type n_jobs: int
            :param kwargs: Other parameters
                Check https://docs.microsoft.com
                /en-us/python/api/nimbusml/nimbusml.linear_model.averagedperceptronbinaryclassifier
                for more parameters.
            """
            self.params = kwargs
            self.classes_ = None
            self.type = NimbusMlClassifierMixin._estimator_type
            if not nimbusml_present:
                raise ConfigException("nimbusml not installed, " +
                                      "please install nimbusml for including nimbusml based models")
            args = dict(self.params)
            nml_linear.AveragedPerceptronBinaryClassifier.__init__(self, **args)

    class AveragedPerceptronMulticlassClassifier(NimbusMlClassifierMixin, nml_multiclass.OneVsRestClassifier):
        """
        NimbusML Averaged Perceptron Classifier for multiple classes that can be used within Nimbus pipelines.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number generator;
            If RandomState instance, random_state is the random number generator;
            If None, the random number generator is the RandomState instance used
            by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://docs.microsoft.com
            /en-us/python/api/nimbusml/nimbusml.linear_model.averagedperceptronbinaryclassifier
            for more parameters.
        """

        def __init__(self,
                     random_state: Optional[Union[int, np.random.RandomState]] = 0,
                     n_jobs: int = 1,
                     **kwargs: Any) -> None:
            """
            Initialize NimbusML Averaged Perceptron Classifier class.

            :param random_state:
                RandomState instance or None, optional (default=None)
                If int, random_state is the seed used by the random number
                generator.
                If RandomState instance, random_state is the random number
                generator.
                If None, the random number generator is the RandomState instance
                used by `np.random`.
            :type random_state: int or RandomState
            :param n_jobs: Number of parallel threads.
            :type n_jobs: int
            :param kwargs: Other parameters
                Check https://docs.microsoft.com
                /en-us/python/api/nimbusml/nimbusml.linear_model.averagedperceptronbinaryclassifier
                for more parameters.
            """
            self.params = kwargs
            self.type = NimbusMlClassifierMixin._estimator_type
            if not nimbusml_present:
                raise ConfigException("nimbusml not installed, " +
                                      "please install nimbusml for including nimbusml based models")
            args = dict(self.params)
            feature_col = args.pop('feature', None)
            label_col = args.pop('label', None)
            weight_col = args.pop('weight', None)
            nml_multiclass.OneVsRestClassifier.__init__(
                self,
                nml_linear.AveragedPerceptronBinaryClassifier(**args),
                feature=feature_col,
                label=label_col,
                weight=weight_col
            )

    class NimbusMlLinearSVMClassifier(NimbusMlClassifierMixin):
        """
        NimbusML Linear SVM Classifier class usable only in SciKit pipelines.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number generator;
            If RandomState instance, random_state is the random number generator;
            If None, the random number generator is the RandomState instance used
            by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://docs.microsoft.com
            /en-us/python/api/nimbusml/nimbusml.linear_model.linearsvmbinaryclassifier
            for more parameters.
        """

        def __init__(self,
                     random_state: Optional[Union[int, np.random.RandomState]] = 0,
                     n_jobs: int = 1,
                     **kwargs: Any) -> None:
            """
            Initialize NimbusML Linear SVM Classifier class usable only in SciKit pipelines.

            :param random_state:
                RandomState instance or None, optional (default=None)
                If int, random_state is the seed used by the random number generator;
                If RandomState instance, random_state is the random number generator;
                If None, the random number generator is the RandomState instance used
                by `np.random`.
            :type random_state: int or RandomState
            :param n_jobs: Number of parallel threads.
            :type n_jobs: int
            :param kwargs: Other parameters
                Check https://docs.microsoft.com
                /en-us/python/api/nimbusml/nimbusml.linear_model.linearsvmbinaryclassifier
                for more parameters.
            """
            self.params = kwargs
            self.classes_ = None
            self.model = None
            self.type = NimbusMlClassifierMixin._estimator_type

        def fit(self, X, y, **kwargs):
            """Fit method for the NimbusML Linear SVM Classifier."""
            args = dict(self.params)
            nml_model = nml_linear.LinearSvmBinaryClassifier(**args)
            if len(unique_labels(y)) > 2:
                # predict_proba returns classes in the order of their indexes in string order.
                nml_model = nml_multiclass.OneVsRestClassifier(nml_model)

            if 'verbose' not in kwargs:
                kwargs['verbose'] = 0

            try:
                nml_model.fit(X, y, **kwargs)
            except Exception as e:
                raise FitException.from_exception(e, has_pii=True, target="NimbusML")
            self.model = nml_model
            self.classes_ = self.model.classes_
            return self

        def predict(self, X):
            """
            Prediction function for NimbusML Linear SVM Classifier model.

            :param X: Input data.
            :type X: numpy.ndarray
            :return: Prediction values from NimbusML Linear SVM Classifier model.
            """
            if self.model is None:
                raise sklearn.exceptions.NotFittedError()
            try:
                return self.model.predict(X).values
            except Exception as e:
                raise ClientException.from_exception(e, has_pii=True)

        def predict_proba(self, X):
            """
            Prediction class probabilities for X for NimbusML Linear SVM Classifier model.

            :param X: Input data.
            :type X: numpy.ndarray
            :return: Prediction probability values from NimbusML Linear SVM Classifier model.
            """
            if self.model is None:
                raise sklearn.exceptions.NotFittedError()
            try:
                return self.model.predict_proba(X)
            except Exception as e:
                raise ClientException.from_exception(e, has_pii=True)

        def get_model(self):
            """
            Return NimbusML model.

            :return: Returns wrapped Nimbus ML model.
            """
            return self.model

        def _get_node(self, **all_args):
            pass

    class LinearSvmBinaryClassifier(NimbusMlClassifierMixin, nml_linear.LinearSvmBinaryClassifier):
        """
        NimbusML Linear SVM Binary Classifier class that can be used within Nimbus pipelines.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number generator;
            If RandomState instance, random_state is the random number generator;
            If None, the random number generator is the RandomState instance used
            by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://docs.microsoft.com
            /en-us/python/api/nimbusml/nimbusml.linear_model.linearsvmbinaryclassifier
            for more parameters.
        """

        def __init__(self,
                     random_state: Optional[Union[int, np.random.RandomState]] = 0,
                     n_jobs: int = 1,
                     **kwargs: Any) -> None:
            """
            Initialize NimbusML Linear SVM Binary Classifier class that can be used within Nimbus pipelines.

            :param random_state:
                RandomState instance or None, optional (default=None)
                If int, random_state is the seed used by the random number generator;
                If RandomState instance, random_state is the random number generator;
                If None, the random number generator is the RandomState instance used
                by `np.random`.
            :type random_state: int or RandomState
            :param n_jobs: Number of parallel threads.
            :type n_jobs: int
            :param kwargs: Other parameters
                Check https://docs.microsoft.com
                /en-us/python/api/nimbusml/nimbusml.linear_model.linearsvmbinaryclassifier
                for more parameters.
            """
            self.params = kwargs
            self.classes_ = None
            self.type = NimbusMlClassifierMixin._estimator_type
            if not nimbusml_present:
                raise ConfigException("nimbusml not installed, " +
                                      "please install nimbusml for including nimbusml based models")
            args = dict(self.params)
            nml_linear.LinearSvmBinaryClassifier.__init__(self, **args)

    class LinearSvmMulticlassClassifier(NimbusMlClassifierMixin, nml_multiclass.OneVsRestClassifier):
        """
        NimbusML Linear SVM Classifier for multiple classes that can be used within Nimbus pipelines.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number generator;
            If RandomState instance, random_state is the random number generator;
            If None, the random number generator is the RandomState instance used
            by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://docs.microsoft.com
            /en-us/python/api/nimbusml/nimbusml.linear_model.linearsvmbinaryclassifier
            for more parameters.
        """

        def __init__(self,
                     random_state: Optional[Union[int, np.random.RandomState]] = 0,
                     n_jobs: int = 1,
                     **kwargs: Any) -> None:
            """
            Initialize NimbusML Linear SVM Classifier class.

            :param random_state:
                RandomState instance or None, optional (default=None)
                If int, random_state is the seed used by the random number
                generator.
                If RandomState instance, random_state is the random number
                generator.
                If None, the random number generator is the RandomState instance
                used by `np.random`.
            :type random_state: int or RandomState
            :param n_jobs: Number of parallel threads.
            :type n_jobs: int
            :param kwargs: Other parameters
                Check https://docs.microsoft.com
                /en-us/python/api/nimbusml/nimbusml.linear_model.linearsvmbinaryclassifier
                for more parameters.
            """
            self.params = kwargs
            self.type = NimbusMlClassifierMixin._estimator_type
            if not nimbusml_present:
                raise ConfigException("nimbusml not installed, " +
                                      "please install nimbusml for including nimbusml based models")
            args = dict(self.params)
            feature_col = args.pop('feature', None)
            label_col = args.pop('label', None)
            weight_col = args.pop('weight', None)
            nml_multiclass.OneVsRestClassifier.__init__(
                self,
                nml_linear.LinearSvmBinaryClassifier(**args),
                feature=feature_col,
                label=label_col,
                weight=weight_col
            )

    class NimbusMlFastLinearRegressor(NimbusMlRegressorMixin, nml_linear.FastLinearRegressor):
        """
        NimbusML Fast Linear Regressor class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number generator;
            If RandomState instance, random_state is the random number generator;
            If None, the random number generator is the RandomState instance used
            by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://docs.microsoft.com/en-us/python/api/nimbusml/nimbusml.linear_model.fastlinearregressor
            for more parameters.
        """

        def __init__(self,
                     random_state: Optional[Union[int, np.random.RandomState]] = 0,
                     n_jobs: int = 1,
                     **kwargs: Any) -> None:
            """
            Initialize NimbusML Fast Linear Regressor class.

            :param random_state:
                RandomState instance or None, optional (default=None)
                If int, random_state is the seed used by the random number
                generator.
                If RandomState instance, random_state is the random number
                generator.
                If None, the random number generator is the RandomState instance
                used by `np.random`.
            :type random_state: int or RandomState
            :param n_jobs: Number of parallel threads.
            :type n_jobs: int
            :param kwargs: Other parameters
                Check https://docs.microsoft.com/en-us/python/api/nimbusml/nimbusml.linear_model.fastlinearregressor
                for more parameters.
            """
            self.params = kwargs
            self.params['random_state'] = random_state if random_state is not None else 0
            self.params['n_jobs'] = n_jobs
            if not nimbusml_present:
                raise ConfigException("nimbusml not installed, " +
                                      "please install nimbusml for including nimbusml based models")

            args = dict(self.params)
            random_state = self.get_random_state(args)

            nml_linear.FastLinearRegressor.__init__(self, **args)

        def get_model(self):
            """
            Return NimbusML Fast Linear Regressor model.

            :return: Returns the fitted model if fit method has been called.
            Else returns None.
            """
            return self

    class NimbusMlOnlineGradientDescentRegressor(NimbusMlRegressorMixin, nml_linear.OnlineGradientDescentRegressor):
        """
        NimbusML Online Gradient Descent Regressor class.

        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number generator;
            If RandomState instance, random_state is the random number generator;
            If None, the random number generator is the RandomState instance used
            by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads.
        :type n_jobs: int
        :param kwargs: Other parameters
            Check https://docs.microsoft.com/en-us/python/api/nimbusml/
                nimbusml.linear_model.onlinegradientdescentregressor
            for more parameters.
        """

        def __init__(self,
                     random_state: Optional[Union[int, np.random.RandomState]] = 0,
                     n_jobs: int = 1,
                     **kwargs: Any) -> None:
            """
            Initialize NimbusML Online Gradient Descent Regressor class.

            :param random_state:
                RandomState instance or None, optional (default=None)
                If int, random_state is the seed used by the random number
                generator.
                If RandomState instance, random_state is the random number
                generator.
                If None, the random number generator is the RandomState instance
                used by `np.random`.
            :type random_state: int or RandomState
            :param n_jobs: Number of parallel threads.
            :type n_jobs: int
            :param kwargs: Other parameters
                Check https://docs.microsoft.com/en-us/python/api/nimbusml/
                    nimbusml.linear_model.onlinegradientdescentregressor
                for more parameters.
            """
            self.params = kwargs
            self.params['random_state'] = random_state if random_state is not None else 0
            self.params['n_jobs'] = n_jobs
            if not nimbusml_present:
                raise ConfigException("nimbusml not installed, " +
                                      "please install nimbusml for including nimbusml based models")

            args = dict(self.params)
            random_state = self.get_random_state(args)

            nml_linear.OnlineGradientDescentRegressor.__init__(self, **args)

        def get_model(self):
            """
            Return NimbusML Online Gradient Descent Regressor model.

            :return: Returns the fitted model if fit method has been called.
            Else returns None.
            """
            return self
