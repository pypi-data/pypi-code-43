# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines a class that wraps functionality of MLI into a single API."""

from sklearn.externals import joblib

try:
    from azureml.core import Model, Dataset, Experiment
    from azureml.exceptions import UserErrorException
except ImportError:
    print("Could not import azureml.core, required if using run history")

from azureml.interpret.common.constants import ModelTask
from interpret_community.mimic.mimic_explainer import MimicExplainer
from azureml.interpret._internal.explanation_client import ExplanationClient
try:
    from azureml._logging import ChainedIdentity
except ImportError:
    from interpret_community.common.chained_identity import ChainedIdentity


class MimicWrapper(ChainedIdentity):
    """A wrapper explainer which reduces the number of function calls necessary to use the explain model package.

    :param workspace: The user's workspace object (where Models and Datasets live).
    :type workspace: azureml.core.workspace
    :param model: The model ID of a model registered to MMS or a regular machine learning model/pipeline
        to explain.
    :type model: str or model that implements sklearn.predict() or sklearn.predict_proba() or pipeline function
        that accepts a 2d ndarray
    :param explainable_model: The uninitialized surrogate model used to explain the black box model.
        Also known as the student model.
    :type explainable_model: azureml.interpret.mimic.models.BaseExplainableModel
    :param explainer_kwargs: Any keyword arguments that go with the chosen explainer not otherwise covered here.
        They will be passed in as kwargs when the underlying explainer is initialized.
    :type explainer_kwargs: dict
    :param init_dataset: The dataset ID or regular dataset used for initializing the explainer (e.g. x_train).
    :type init_dataset: str or numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
        scipy.sparse.csr_matrix
    :param run: The run this explanation should be associated with.
    :type run: azureml.core.Run
    :param features: A list of feature names.
    :type features: list[str]
    :param classes: Class names as a list of strings. The order of the class names should match
        that of the model output.  Only required if explaining classifier.
    :type classes: list[str]
    :param model_task: Optional parameter to specify whether the model is a classification or regression model.
        In most cases, the type of the model can be inferred based on the shape of the output, where a classifier
        has a predict_proba method and outputs a 2 dimensional array, while a regressor has a predict method and
        outputs a 1 dimensional array.
    :type model_task: str
    :param explain_subset: List of feature indices. If specified, only selects a subset of the
        features in the evaluation dataset for explanation, which will speed up the explanation
        process when number of features is large and the user already knows the set of interested
        features. The subset can be the top-k features from the model summary. This argument is not supported when
        transformations are set.
    :type explain_subset: list[int]
    :param transformations: sklearn.compose.ColumnTransformer or a list of tuples describing the column name and
        transformer. When transformations are provided, explanations are of the features before the transformation.
        The format for list of transformations is same as the one here:
        https://github.com/scikit-learn-contrib/sklearn-pandas.

        If the user is using a transformation that is not in the list of sklearn.preprocessing transformations that
        we support then we cannot take a list of more than one column as input for the transformation.
        A user can use the following sklearn.preprocessing  transformations with a list of columns since these are
        already one to many or one to one: Binarizer, KBinsDiscretizer, KernelCenterer, LabelEncoder, MaxAbsScaler,
        MinMaxScaler, Normalizer, OneHotEncoder, OrdinalEncoder, PowerTransformer, QuantileTransformer, RobustScaler,
        StandardScaler.

        Examples for transformations that work::

            [
                (["col1", "col2"], sklearn_one_hot_encoder),
                (["col3"], None) #col3 passes as is
            ]
            [
                (["col1"], my_own_transformer),
                (["col2"], my_own_transformer),
            ]

        Example of transformations that would raise an error since it cannot be interpreted as one to many::

            [
                (["col1", "col2"], my_own_transformer)
            ]

        This would not work since it is hard to make out whether my_own_transformer gives a many to many or one to
        many mapping when taking a sequence of columns.
    :type transformations: sklearn.compose.ColumnTransformer or list[tuple]
    :param feature_maps: list of feature maps from raw to generated feature
    :type feature_maps: list of numpy arrays or sparse matrices where each array entry
        (raw_index, generated_index) is the weight for each raw, generated feature pair. The other entries are set
        to zero. For a sequence of transformations [t1, t2, ..., tn] generating generated features from raw
        features, the list of feature maps correspond to the raw to generated maps in the same order as t1, t2,
        etc. If the overall raw to generated feature map from t1 to tn is available, then just that feature map
        in a single element list can be passed.
    :param allow_all_transformations: Allow many to many and many to one transformations
    :type allow_all_transformations: bool
    """

    def __init__(self, workspace, model, explainable_model, explainer_kwargs=None,
                 init_dataset=None, run=None, features=None, classes=None, model_task=ModelTask.Unknown,
                 explain_subset=None, transformations=None, feature_maps=None, allow_all_transformations=None):
        """Initialize the MimicWrapper.

        :param workspace: The user's workspace object (where Models and Datasets live).
        :type workspace: azureml.core.workspace
        :param model: The model ID of a model registered to MMS or a regular machine learning model/pipeline
            to explain.
        :type model: str or model that implements sklearn.predict() or sklearn.predict_proba() or pipeline function
            that accepts a 2d ndarray
        :param explainable_model: The uninitialized surrogate model used to explain the black box model.
            Also known as the student model.
        :type explainable_model: azureml.interpret.mimic.models.BaseExplainableModel
        :param explainer_kwargs: Any keyword arguments that go with the chosen explainer not otherwise covered here.
            They will be passed in as kwargs when the underlying explainer is initialized.
        :type explainer_kwargs: dict
        :param init_dataset: The dataset ID or regular dataset used for initializing the explainer (e.g. x_train).
        :type init_dataset: str or numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param run: The run this explanation should be associated with.
        :type run: azureml.core.Run
        :param features: A list of feature names.
        :type features: list[str]
        :param classes: Class names as a list of strings. The order of the class names should match
            that of the model output.  Only required if explaining classifier.
        :type classes: list[str]
        :param model_task: Optional parameter to specify whether the model is a classification or regression model.
            In most cases, the type of the model can be inferred based on the shape of the output, where a classifier
            has a predict_proba method and outputs a 2 dimensional array, while a regressor has a predict method and
            outputs a 1 dimensional array.
        :type model_task: str
        :param explain_subset: List of feature indices. If specified, only selects a subset of the
            features in the evaluation dataset for explanation, which will speed up the explanation
            process when number of features is large and the user already knows the set of interested
            features. The subset can be the top-k features from the model summary. This argument is not supported when
            transformations are set.
        :type explain_subset: list[int]
        :param transformations: sklearn.compose.ColumnTransformer or a list of tuples describing the column name and
            transformer. When transformations are provided, explanations are of the features before the
            transformation. The format for list of transformations is same as the one here:
            https://github.com/scikit-learn-contrib/sklearn-pandas.
            If the user is using a transformation that is not in the list of sklearn.preprocessing transformations
            that we support then we cannot take a list of more than one column as input for the transformation.
            A user can use the following sklearn.preprocessing  transformations with a list of columns since these are
            already one to many or one to one: Binarizer, KBinsDiscretizer, KernelCenterer, LabelEncoder,
            MaxAbsScaler, MinMaxScaler, Normalizer, OneHotEncoder, OrdinalEncoder, PowerTransformer,
            QuantileTransformer, RobustScaler, StandardScaler.
            Examples for transformations that work:
            [
                (["col1", "col2"], sklearn_one_hot_encoder),
                (["col3"], None) #col3 passes as is
            ]
            [
                (["col1"], my_own_transformer),
                (["col2"], my_own_transformer),
            ]
            Example of transformations that would raise an error since it cannot be interpreted as one to many:
            [
                (["col1", "col2"], my_own_transformer)
            ]
            This would not work since it is hard to make out whether my_own_transformer gives a many to many or one to
            many mapping when taking a sequence of columns.
        :type transformations: sklearn.compose.ColumnTransformer or list[tuple]
        :param feature_maps: list of feature maps from raw to generated feature
        :type feature_maps: list of numpy arrays or sparse matrices where each array entry
            (raw_index, generated_index) is the weight for each raw, generated feature pair. The other entries are set
            to zero. For a sequence of transformations [t1, t2, ..., tn] generating generated features from raw
            features, the list of feature maps correspond to the raw to generated maps in the same order as t1, t2,
            etc. If the overall raw to generated feature map from t1 to tn is available, then just that feature map
            in a single element list can be passed. Note that only one of transformations and feature_maps can be
            passed.
        :param allow_all_transformations: Allow many to many and many to one transformations
        :type allow_all_transformations: bool
        """
        if transformations is not None and feature_maps is not None:
            raise ValueError('Only one of transformations and feature_maps can be passed.')

        super(MimicWrapper, self).__init__()
        self._logger.debug('Initializing MimicWrapper')
        kwargs = {} if explainer_kwargs is None else explainer_kwargs
        self._workspace = workspace
        self._run = run
        self._model_id = None
        self._init_dataset_id = None
        if isinstance(model, str):
            self._logger.debug('Model ID passed in')
            self._model_id = model
            model_obj = Model(self._workspace, id=self._model_id)
            path = model_obj.download(exist_ok=True)
            model = joblib.load(path)
        if isinstance(init_dataset, str):
            self._logger.debug('Init Dataset ID passed in')
            self._init_dataset_id = init_dataset
            init_dataset_obj = Dataset.get(self._workspace, id=init_dataset)
            init_dataset = init_dataset_obj.to_pandas_dataframe().values.astype('float64')
        if init_dataset is None:
            self._logger.debug('No init dataset passed into MimicWrapper')
            raise UserErrorException('An initialization dataset is required to use MimicExplainer.')
        self._feature_maps = feature_maps
        self._internal_explainer = MimicExplainer(model,
                                                  init_dataset,
                                                  explainable_model,
                                                  features=features,
                                                  classes=classes,
                                                  model_task=model_task,
                                                  explain_subset=explain_subset,
                                                  transformations=transformations,
                                                  allow_all_transformations=allow_all_transformations,
                                                  **kwargs)

    def _explain_local(self, evals):
        """Explain a model's behavior on individual data instances.

        :param evals: The data instances to explain.
        :type evals: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A local explanation.
        :rtype: DynamicLocalExplanation
        """
        return self._internal_explainer.explain_local(evals)

    def _explain_global(self, evals=None):
        """Explain a model's behavior at the global level.

        :param evals: Representative data instances used to construct the explanation.
        :type evals: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A global explanation.
        :rtype: DynamicGlobalExplanation
        """
        return self._internal_explainer.explain_global(evaluation_examples=evals)

    def explain(self, explanation_types, eval_dataset=None, top_k=None, upload=True, upload_datasets=False,
                tag="", get_raw=False, raw_feature_names=None, experiment_name='explain_model'):
        """Explain a model's behavior and optionally upload that explanation for storage and visualization.

        :param explanation_types: A list of strings representing types of explanations desired. Currently, we support
            'global' and 'local'. Both may be passed in at once; only one explanation will be returned.
        :type explanation_types: list[str]
        :param eval_dataset: The dataset ID or regular dataset used to generate the explanation.
        :type eval_dataset: str or numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        :param top_k: Limit the amount of data returned and stored in run history to top k features when possible.
        :type top_k: int
        :param upload: If True, the explanation is automatically uploaded to Run History for storage and
            visualization. If a run was not passed in at initialization, we will create one.
        :type upload: bool
        :param upload_datasets: If set to True and no dataset IDs are passed in, the evaluation dataset will be
            uploaded to Azure storage. This will improve the visualization available in the web view.
        :type upload_datasets: bool
        :param tag: A string to attach to the explanation to distinguish it from others after upload.
        :type tag: str
        :param get_raw: If True and feature_maps were passed in during initialization, the explanation returned will
            be for the raw features. If False or not specified, the explanation will be for the data exactly as it is
            passed in.
        :type get_raw: bool
        :param raw_feature_names: The list of raw feature names, replacing engineered feature names from the
            constructor.
        :type raw_feature_names: list[str]
        :param experiment_name: The desired name we should give an explanation if upload is True but no run was passed
            in during initialization
        :type experiment_name: str
        :return: An explanation object or a dictionary of raw and engineered explanations if feature_map was passed in
            at initialization.
        :rtype: Explanation or dict{str: Explanation}
        """
        eval_dataset_id = None
        if isinstance(eval_dataset, str):
            self._logger.debug('Eval Dataset ID passed in')
            eval_dataset_id = eval_dataset
            eval_dataset_obj = Dataset.get(self._workspace, id=eval_dataset)
            eval_dataset = eval_dataset_obj.to_pandas_dataframe().values.astype('float64')
        if 'global' in explanation_types:
            if 'local' in explanation_types:
                explanation = self._explain_global(evals=eval_dataset)
            else:
                explanation = self._explain_global()
        elif 'local' in explanation_types:
            if eval_dataset is None:
                raise UserErrorException('An evaluation dataset must be passed in to do local explanation.')
            explanation = self._explain_local(eval_dataset)
        else:
            raise UserErrorException('Please pass global, local, or both into the explainer_type list.')

        if get_raw:
            if self._feature_maps is None:
                raise UserErrorException('If setting get_raw to True, please pass feature_maps during initialization.')
            else:
                self._logger.debug('Creating a raw explanation')
                explanation = explanation.get_raw_explanation(self._feature_maps, raw_feature_names=raw_feature_names)

        if upload:
            self._logger.debug('Uploading model explanation from MimicWrapper')
            if self._run is None:
                experiment = Experiment(self._workspace, experiment_name)
                self._run = experiment.start_logging()
            client = ExplanationClient.from_run(self._run)
            client.upload_model_explanation(explanation,
                                            model_id=self._model_id,
                                            init_dataset_id=self._init_dataset_id,
                                            eval_dataset_id=eval_dataset_id,
                                            upload_datasets=upload_datasets,
                                            comment=tag,
                                            top_k=top_k)
        return explanation

    @property
    def explainer(self):
        """Get the explainer that is being used internally by the wrapper.

        :return: The explainer that is being used internally by the wrapper.
        :rtype: azureml.interpret.mimic.MimicExplainer
        """
        return self._internal_explainer
