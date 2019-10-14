# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines scoring models for approximating feature importance values."""

import numpy as np
import logging
import os
from abc import ABCMeta, abstractmethod
from sklearn.externals import joblib

try:
    from azureml._logging import ChainedIdentity
except ImportError:
    from interpret_community.common.chained_identity import ChainedIdentity
try:
    from azureml.core import VERSION
except ImportError:
    VERSION = None

from azureml.interpret.common.constants import LoggingNamespace, Scoring
from interpret_community.common.explanation_utils import _get_raw_feature_importances, \
    _get_dense_examples, _transform_data, _fix_linear_explainer_shap_values
from interpret_community._internal.raw_explain import DataMapper
from azureml.interpret.mimic_wrapper import MimicWrapper

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', 'Starting from version 2.2.1', UserWarning)
    import shap

LOGGER = '_logger'
SCORING_FILE = 'scoring_explainer.pkl'
DEPENDENCIES = 'dependencies'


def save(scoring_explainer, directory='.', exist_ok=False):
    """Save the scoring explainer to disk.

    :param scoring_explainer: The scoring explainer object which is to be saved. Will be written out to
        [directory]/scoring_explainer.pkl.
    :type name: ScoringExplainer
    :param directory: The directory under which the serialized explainer should be stored.
        If it doesn't exist, it will be created.
    :type directory: str
    :param exist_ok: If False (the default state), a warning will be thrown if the directory given already exists. If
        True, the current directory will be used and any overlapping contents will be overwritten.
    :type exist_ok: bool
    :return: The path to the scoring explainer pickle file.
    :rtype: str
    """
    # general check on path existence and creation
    if not os.path.exists(directory):
        os.makedirs(directory)
    elif not exist_ok:
        raise Exception('A directory already exists at this path. Please choose another path '
                        'or set exist_ok=True to overwrite the contents of the current directory.')

    # save scoring explainer to the given directory
    outpath = os.path.join(directory, SCORING_FILE)
    with open(outpath, 'wb') as stream:
        joblib.dump(scoring_explainer, stream)

    return outpath


def load(directory):
    """Load the scoring explainer from disk.

    :param directory: The directory under which the serialized explainer is stored. Assumes that
        scoring_explainer.pkl is available at the top level of the directory.
    :type directory: str
    :return: The scoring explainer from an explanation, loaded from disk.
    :rtype: azureml.interpret.scoring.scoring_explainer.ScoringExplainer
    """
    with open(os.path.join(directory, SCORING_FILE), 'rb') as stream:
        scoring_explainer = joblib.load(stream)
    return scoring_explainer


def _unwrap_tabular(explainer):
    """Remove the tabular layer around a direct explainer.

    :param explainer: An explainer.
    :type explainer: BaseExplainer
    :return: An explainer, which will be a direct explainer if the original was a TabularExplainer.
    :rtype: BaseExplainer
    """
    if 'TabularExplainer' in str(type(explainer)):
        explainer = explainer.explainer
    return explainer


class ScoringExplainer(ChainedIdentity):
    """Defines a scoring model."""

    __metaclass__ = ABCMeta

    def __init__(self, original_explainer, feature_maps=None, **kwargs):
        """Initialize the ScoringExplainer.

        If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
        the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
        If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
        explainer will expected transformed data, and by default importances will be returned for transformed data. In
        either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
        `explain` method.

        :param original_explainer: The training time explainer originally used to explain the model.
        :type original_explainer: BaseExplainer
        :param feature_maps: list of feature maps from raw to generated feature
        :type feature_maps: list of numpy arrays or sparse matrices where each array entry
            (raw_index, generated_index) is the weight for each raw, generated feature pair. The other entries are set
            to zero. For a sequence of transformations [t1, t2, ..., tn] generating generated features from raw
            features, the list of feature maps correspond to the raw to generated maps in the same order as t1, t2,
            etc. If the overall raw to generated feature map from t1 to tn is available, then just that feature map
            in a single element list can be passed.
        """
        super(ScoringExplainer, self).__init__(**kwargs)
        self._logger.debug('Initializing ScoringExplainer')

        if isinstance(original_explainer, MimicWrapper):
            original_explainer = original_explainer.explainer

        if original_explainer.transformations is not None:
            self._data_mapper = DataMapper(original_explainer.transformations)
        else:
            self._data_mapper = None
        self._feature_maps = feature_maps

        self._function = None
        # If the original was a MimicExplainer, we need custom logic to pull the model out
        if hasattr(original_explainer, Scoring.SURROGATE_MODEL):
            self._model = original_explainer.surrogate_model.model
        else:
            self._model = original_explainer.model
            if self._model is None:
                self._function = original_explainer.function
        self._features = original_explainer.features

    def fit(self, X, y=None):
        """Implement dummy method required to fit scikit-learn pipeline interface."""
        return self

    @abstractmethod
    def explain(self, evaluation_examples, get_raw):
        """Use the model for scoring to approximate the feature importance values of data."""
        pass

    @property
    def features(self):
        """Get the feature names passed into the original explainer.

        :return: The feature names, or None if none were given by the user.
        :rtype: list[str] or None
        """
        if self._features is not None and not isinstance(self._features, list):
            self._features = self._features.tolist()
        return self._features

    def _get_raw_importances(self, engineered_importances):
        """Convert from an explanation of engineered features to an explanation of raw features.

        :param engineered_importances: The results of calling .explain() on engineered data.
        :type engineered_importances: np.array
        :return: The importances for the raw features originally passed to the scoring explainer.
        :rtype: np.array
        """
        if self._data_mapper is not None:
            return _get_raw_feature_importances(engineered_importances, [self._data_mapper.feature_map])
        elif self._feature_maps is not None:
            return _get_raw_feature_importances(engineered_importances, self._feature_maps)
        else:
            raise Exception('get_raw should not be passed in if neither '
                            'transformations nor feature maps are passed in. '
                            'Please see documentation for the ScoringExplainer class for more information.')

    def predict(self, evaluation_examples):
        """Use the TreeExplainer and tree model for scoring to get the feature importance values of data.

        Wraps the .explain() function.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list
        """
        return self.explain(evaluation_examples)

    def __getstate__(self):
        """Influence how TreeScoringExplainer is pickled.

        Removes logger which is not serializable.

        :return state: The state to be pickled, with logger removed.
        :rtype state: dict
        """
        odict = self.__dict__.copy()
        del odict[LOGGER]
        return odict

    def __setstate__(self, dict):
        """Influence how TreeScoringExplainer is unpickled.

        Re-adds logger which is not serializable.

        :param dict: A dictionary of deserialized state.
        :type dict: dict
        """
        self.__dict__.update(dict)
        parent = logging.getLogger(LoggingNamespace.AZUREML)
        self._logger = parent.getChild(self._identity)


class KernelScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on KernelExplainer."""

    def __init__(self, original_explainer, initialization_examples=None, **kwargs):
        """Initialize the KernelScoringExplainer.

        If the original explainer was using a SHAP KernelExplainer and no initialization data was passed in,
        the core of the original explainer will be reused. If the original explainer used another method or new
        initialization data was passed in under initialization_examples, a new explainer will be created.

        If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
        the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
        If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
        explainer will expected transformed data, and by default importances will be returned for transformed data. In
        either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
        `explain` method.

        :param original_explainer: The training time explainer originally used to explain the model.
        :type original_explainer: BaseExplainer
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        super(KernelScoringExplainer, self).__init__(original_explainer, **kwargs)
        self._logger.debug('Initializing KernelScoringExplainer')
        if self._model is None:
            self._model_function = self._function
        else:
            try:
                self._model_function = self._model.predict_proba
            except:
                self._model_function = self._model.predict

        original_explainer = _unwrap_tabular(original_explainer)

        self._kernel_explainer = None
        has_explainer = hasattr(original_explainer, Scoring.EXPLAINER)
        if initialization_examples is not None:
            # Create new explainer
            init_data = _transform_data(initialization_examples, data_mapper=self._data_mapper)
            self._kernel_explainer = shap.KernelExplainer(self._model_function, init_data)
        elif has_explainer and type(original_explainer.explainer) == shap.KernelExplainer:
            # Reuse core of original explainer
            self._kernel_explainer = original_explainer.explainer
        else:
            raise Exception('Please pass initialization_examples to create a new explainer.')
        self._method = 'scoring.kernel'

    def explain(self, evaluation_examples, get_raw=None):
        """Use the TreeExplainer and tree model for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param get_raw: If True, importances for raw features will be returned. If False, importances for engineered
            features will be returned. If unspecified and `transformations` was passed into the original explainer,
            raw importances will be returned. If unspecified and `feature_maps` was passed into the scoring explainer,
            engineered importances will be returned.
        :type get_raw: bool
        :return: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list
        """
        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper)

        values = self._kernel_explainer.shap_values(data)
        if get_raw or (get_raw is None and self._data_mapper is not None):
            values = np.array(values) if isinstance(values, list) else values
            return self._get_raw_importances(values).tolist()

        if not isinstance(values, list):
            values = values.tolist()
        # current slight hack for inconsistent shap deep explainer return type (list of numpy arrays)
        for i in range(len(values)):
            if not isinstance(values[i], list):
                values[i] = values[i].tolist()
        return values


class DeepScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on DeepExplainer."""

    def __init__(self, original_explainer, initialization_examples=None, **kwargs):
        """Initialize the DeepScoringExplainer.

        If the original explainer was using a SHAP DeepExplainer and no initialization data was passed in,
        the core of the original explainer will be reused. If the original explainer used another method or new
        initialization data was passed in under initialization_examples, a new explainer will be created.

        If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
        the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
        If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
        explainer will expected transformed data, and by default importances will be returned for transformed data. In
        either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
        `explain` method.

        :param original_explainer: The training time deep explainer originally used to explain the model.
        :type original_explainer: BaseExplainer
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        super(DeepScoringExplainer, self).__init__(original_explainer,
                                                   **kwargs)
        self._logger.debug('Initializing DeepScoringExplainer')

        original_explainer = _unwrap_tabular(original_explainer)

        self._deep_explainer = None
        has_explainer = hasattr(original_explainer, Scoring.EXPLAINER)
        if initialization_examples is not None:
            # Create new explainer
            init_data = _transform_data(initialization_examples, data_mapper=self._data_mapper)
            self._deep_explainer = shap.DeepExplainer(self._model, init_data)
        elif has_explainer and type(original_explainer.explainer) == shap.DeepExplainer:
            # Reuse core of original explainer
            self._deep_explainer = original_explainer.explainer
        else:
            raise Exception('Please pass initialization_examples to create a new explainer.')
        self._method = 'scoring.deep'

    def explain(self, evaluation_examples, get_raw=None):
        """Use the DeepExplainer and deep model for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param get_raw: If True, importances for raw features will be returned. If False, importances for engineered
            features will be returned. If unspecified and `transformations` was passed into the original explainer,
            raw importances will be returned. If unspecified and `feature_maps` was passed into the scoring explainer,
            engineered importances will be returned.
        :type get_raw: bool
        :return: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list
        """
        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper)

        values = self._deep_explainer.shap_values(data)
        if get_raw or (get_raw is None and self._data_mapper is not None):
            values = np.array(values) if isinstance(values, list) else values
            return self._get_raw_importances(values).tolist()
        if not isinstance(values, list):
            values = values.tolist()
        # current slight hack for inconsistent shap deep explainer return type (list of numpy arrays)
        for i in range(len(values)):
            if not isinstance(values[i], list):
                values[i] = values[i].tolist()
        return values


class TreeScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on TreeExplainer."""

    def __init__(self, original_explainer, **kwargs):
        """Initialize the TreeScoringExplainer.

        If the original explainer was using a SHAP TreeExplainer, the core of the original explainer will be reused.
        If the original explainer used another method, a new explainer will be created.

        If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
        the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
        If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
        explainer will expected transformed data, and by default importances will be returned for transformed data. In
        either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
        `explain` method.

        :param original_explainer: The training time tree explainer originally used to explain the model.
        :type original_explainer: BaseExplainer
        """
        super(TreeScoringExplainer, self).__init__(original_explainer, **kwargs)
        self._logger.debug('Initializing TreeScoringExplainer')

        original_explainer = _unwrap_tabular(original_explainer)

        has_explainer = hasattr(original_explainer, Scoring.EXPLAINER)
        if has_explainer and type(original_explainer.explainer) == shap.TreeExplainer:
            # Reuse core of original explainer
            self._tree_explainer = original_explainer.explainer
        else:
            # Create new explainer
            self._tree_explainer = shap.TreeExplainer(self._model)

        # Only lightgbm and xgboost models don't directly fail with sparse data currently
        model_type_str = str(type(self._model))
        self._convert_to_dense = not ("xgboost" in model_type_str or "lightgbm" in model_type_str)
        self._method = 'scoring.tree'

    def explain(self, evaluation_examples, get_raw=None):
        """Use the TreeExplainer and tree model for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param get_raw: If True, importances for raw features will be returned. If False, importances for engineered
            features will be returned. If unspecified and `transformations` was passed into the original explainer,
            raw importances will be returned. If unspecified and `feature_maps` was passed into the scoring explainer,
            engineered importances will be returned. If unspecified and neither is passed, explanations will be given
            for the data as it was passed in.
        :type get_raw: bool
        :return: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list
        """
        if self._convert_to_dense:
            evaluation_examples = _get_dense_examples(evaluation_examples)

        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper)

        values = self._tree_explainer.shap_values(data)
        if get_raw or (get_raw is None and self._data_mapper is not None):
            values = np.array(values) if isinstance(values, list) else values
            return self._get_raw_importances(values).tolist()
        if not isinstance(values, list):
            values = values.tolist()
        return values


class LinearScoringExplainer(ScoringExplainer):
    """Defines a scoring model based on LinearExplainer."""

    def __init__(self, original_explainer, initialization_examples=None, **kwargs):
        """Initialize the LinearScoringExplainer.

        If the original explainer was using a SHAP LinearExplainer and no initialization data was passed in,
        the core of the original explainer will be reused. If the original explainer used another method or new
        initialization data was passed in under initialization_examples, a new explainer will be created.

        If `transformations` was passed in on `original_explainer`, those transformations will be carried through to
        the scoring explainer, it will expect raw data, and by default importances will be returned for raw features.
        If `feature_maps` are passed in here (NOT intended to be used at the same time as `transformations`), the
        explainer will expected transformed data, and by default importances will be returned for transformed data. In
        either case, the output can be specified by setting `get_raw` explicitly to True or False on the explainer's
        `explain` method.

        :param original_explainer: The training time explainer originally used to explain the linear model.
        :type original_explainer: BaseExplainer
        :param initialization_examples: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type initialization_examples: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        super(LinearScoringExplainer, self).__init__(original_explainer, **kwargs)
        self._logger.debug('Initializing LinearScoringExplainer')
        original_explainer = _unwrap_tabular(original_explainer)

        has_explainer = hasattr(original_explainer, Scoring.EXPLAINER)
        if initialization_examples is not None:
            # Create new explainer
            init_data = _transform_data(initialization_examples, data_mapper=self._data_mapper)
            self._linear_explainer = shap.LinearExplainer(self._model, init_data)
        elif has_explainer and type(original_explainer.explainer) == shap.LinearExplainer:
            # Reuse core of original explainer
            self._linear_explainer = original_explainer.explainer
        else:
            raise Exception('Please pass initialization_examples to create a new explainer.')
        self._method = 'scoring.linear'

    def explain(self, evaluation_examples, get_raw=None):
        """Use the LinearExplainer for scoring to get the feature importance values of data.

        :param evaluation_examples: A matrix of feature vector examples (# examples x # features) on
            which to explain the model's output.
        :type evaluation_examples: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param get_raw: If True, importances for raw features will be returned. If False, importances for engineered
            features will be returned. If unspecified and `transformations` was passed into the original explainer,
            raw importances will be returned. If unspecified and `feature_maps` was passed into the scoring explainer,
            engineered importances will be returned.
        :type get_raw: bool
        :return: For a model with a single output such as regression,
            this returns a matrix of feature importance values. For models with vector outputs
            this function returns a list of such matrices, one for each output. The dimension
            of this matrix is (# examples x # features).
        :rtype: list
        """
        data = evaluation_examples

        # convert raw data to engineered before explaining
        data = _transform_data(evaluation_examples, data_mapper=self._data_mapper)

        values = self._linear_explainer.shap_values(data)
        # Temporary fix for a bug in shap for regression models
        values = _fix_linear_explainer_shap_values(self._model, values)
        values = np.array(values)
        if get_raw or (get_raw is None and self._data_mapper is not None):
            return self._get_raw_importances(values).tolist()
        if not isinstance(values, list):
            values = values.tolist()
        return values
