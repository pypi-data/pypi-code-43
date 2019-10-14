# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the Explanation dashboard class."""

from .ExplanationWidget import ExplanationWidget
from ._internal.constants import ExplanationDashboardInterface, WidgetRequestResponseConstants
from IPython.display import display
from scipy.sparse import issparse
import numpy as np
import pandas as pd


class ExplanationDashboard(object):
    """The dashboard class, wraps the dashboard component."""

    def __init__(self, explanationObject, learner, dataset, trueY=None):
        """Initialize the Explanation Dashboard.

        :param explanationObject: An object that represents an explanation. It is assumed that it
            has a local_importance_values property that is a 2d array in teh case of regression,
            and 3d array in the case of classification. Dimensions are either samples x features, or
            classes x samples x features. Optionally, it may have a features array that is the string name
            of the features, and a classes array that is the string name of the classes.
        :type explanationObject: object
        :param learner: An object that represents a model. It is assumed that for the classification case
            it has a method of predict_proba() returning the prediction probabilities for each
            class and for the regression case a method of predict() returning the prediction value.
        :type learner: object
        :param dataset:  A matrix of feature vector examples (# examples x # features), the same sampels
            used to build the explanationObject.
        :type dataset: numpy.array or list[][]
        :param trueY: The true labels for the provided dataset
        :tpye trueY: numpy.array or list[]
        """
        self._widget_instance = ExplanationWidget()
        self._learner = learner
        self._is_classifier = hasattr(learner, 'predict_proba') and learner.predict_proba is not None
        self._dataframeColumns = None
        if isinstance(dataset, pd.DataFrame) and hasattr(dataset, 'columns'):
            self._dataframeColumns = dataset.columns
        try:
            list_dataset = self._convertToList(dataset)
        except:
            raise ValueError("Unsupported dataset type")
        try:
            y_pred = learner.predict(dataset)
        except:
            raise ValueError("Model does not support predict method for given dataset type")
        try:
            y_pred = self._convertToList(y_pred)
        except:
            raise ValueError("Model prediction output of unsupported type")
        try:
            trueY = self._convertToList(trueY)
        except:
            raise ValueError("True Y array of unsupported type")
        has_classes = hasattr(explanationObject, 'classes') and explanationObject.classes is not None
        if has_classes:
            classes = self._convertToList(explanationObject.classes)
        if all(isinstance(y_pred_val, str) for y_pred_val in y_pred):
            if not has_classes:
                raise Exception("For model that outputs strings, classes must be specified on explanation")
            y_pred = self._convertToList(np.searchsorted(classes, y_pred))
        dataArg = {
            ExplanationDashboardInterface.PREDICTED_Y: y_pred,
            ExplanationDashboardInterface.TRAINING_DATA: list_dataset,
            ExplanationDashboardInterface.IS_CLASSIFIER: self._is_classifier}

        row_length, feature_length = np.shape(list_dataset)
        if row_length > 100000:
            raise ValueError("Exceeds maximum number of rows for visualization (100000)")
        if feature_length > 1000:
            raise ValueError("Exceeds maximum number of features for visualization (1000)")
        hasLocal = hasattr(explanationObject, 'local_importance_values') \
            and explanationObject.local_importance_values is not None
        local_dim = None

        if trueY is not None and len(trueY) == row_length:
            dataArg[ExplanationDashboardInterface.TRUE_Y] = trueY

        if hasLocal:
            try:
                localExplanations = self._convertToList(explanationObject.local_importance_values)
                dataArg[ExplanationDashboardInterface.LOCAL_EXPLANATIONS] = localExplanations
            except:
                raise ValueError("Unsupported local explanation type")
            local_dim = np.shape(localExplanations)
            if len(local_dim) != 2 and len(local_dim) != 3:
                raise ValueError("Local explanation expected to be a 2D or 3D list")
            if len(local_dim) == 2 and (local_dim[1] != feature_length or local_dim[0] != row_length):
                raise ValueError("Shape mismatch: local explanation length differs from dataset")
            if len(local_dim) == 3 and (local_dim[2] != feature_length or local_dim[1] != row_length):
                raise ValueError("Shape mismatch: local explanation length differs from dataset")
        if not hasLocal and explanationObject.global_importance_values is not None:
            try:
                globalExplanation = self._convertToList(explanationObject.global_importance_values)
                dataArg[ExplanationDashboardInterface.GLOBAL_EXPLANATION] = globalExplanation
            except:
                raise ValueError("Unsupported global explanation type")
        if hasattr(explanationObject, 'features') and explanationObject.features is not None:
            features = self._convertToList(explanationObject.features)
            if len(features) != feature_length:
                raise ValueError("Feature vector length mismatch: \
                    feature names length differs from local explanations dimension")
            dataArg[ExplanationDashboardInterface.FEATURE_NAMES] = features
        if has_classes:
            if local_dim is not None and len(classes) != local_dim[0]:
                raise ValueError("Class vector length mismatch: \
                    class names length differs from local explanations dimension")
            dataArg[ExplanationDashboardInterface.CLASS_NAMES] = self._convertToList(explanationObject.classes)
        if hasattr(learner, 'predict_proba') and learner.predict_proba is not None:
            try:
                probability_y = learner.predict_proba(dataset)
            except:
                raise ValueError("Model does not support predict_proba method for given dataset type")
            try:
                probability_y = self._convertToList(probability_y)
            except:
                raise ValueError("Model predict_proba output of unsupported type")
            dataArg[ExplanationDashboardInterface.PROBABILITY_Y] = probability_y
        self._widget_instance.value = dataArg
        self._widget_instance.observe(self._on_request, names=WidgetRequestResponseConstants.REQUEST)
        display(self._widget_instance)

    def _on_request(self, change):
        try:
            data = change.new[WidgetRequestResponseConstants.DATA]
            if self._dataframeColumns is not None:
                data = pd.DataFrame(data, columns=self._dataframeColumns)
            if (self._is_classifier):
                prediction = self._convertToList(self._learner.predict_proba(data))
            else:
                prediction = self._convertToList(self._learner.predict(data))
            self._widget_instance.response = {
                WidgetRequestResponseConstants.DATA: prediction,
                WidgetRequestResponseConstants.ID: change.new[WidgetRequestResponseConstants.ID]}
        except:
            self._widget_instance.response = {
                WidgetRequestResponseConstants.ERROR: "Model threw exeption while predicting",
                WidgetRequestResponseConstants.DATA: [],
                WidgetRequestResponseConstants.ID: change.new[WidgetRequestResponseConstants.ID]}

    def _show(self):
        display(self._widget_instance)

    def _convertToList(self, array):
        if issparse(array):
            if array.shape[1] > 1000:
                raise ValueError("Exceeds maximum number of features for visualization (1000)")
            return array.toarray().tolist()
        if (isinstance(array, pd.DataFrame)):
            return array.values.tolist()
        if (isinstance(array, np.ndarray)):
            return array.tolist()
        return array
