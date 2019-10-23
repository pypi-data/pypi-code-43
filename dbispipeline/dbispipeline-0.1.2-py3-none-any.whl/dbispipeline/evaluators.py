"""Module containing the evaluator base class and some default evaluators."""
import json
import warnings

import numpy as np

import pandas as pd

from sklearn import metrics
from sklearn.model_selection import GridSearchCV, PredefinedSplit

from .base import Evaluator


class ModelCallbackWrapper(Evaluator):
    """Allows a callback to do something with the fitted model (e.g. predict
    or store in a pickle)"""

    def __init__(self, wrapped_evaluator, callback):
        """returns the fitted model to the callback method after evaluating
        using the wrapped evluator.
        """
        self.wrapped_evaluator = wrapped_evaluator
        self.callback = callback

    def evaluate(self, model, data):
        result = self.wrapped_evaluator.evaluate(model, data)
        self.callback(model)
        return result

    @property
    def configuration(self):
        return {
            'model_callback': self.callback.__name__,
            'wrapped_evaluator': self.wrapped_evaluator.__class__.__name__,
            'wrapped_configuration': self.wrapped_evaluator.configuration,
        }


class GridEvaluator(Evaluator):
    """Evalutaor that performs a grid search."""

    def __init__(self, parameters, grid_parameters):
        """
        Creates a new instance.

        Args:
            parameter: passed to the GridSearchCV as configuration.E
            grid_parameter: passed to the GridSearchCV to configure the
            gridsearch.
        """
        self.parameters = parameters
        self.grid_parameters = grid_parameters

    def evaluate(self, model, data):
        """
        Evaluates the pipline based on the given dataset.

        Args:
            model: the model given in the pipeline.
            data: the data needed for this run, passed to grid as:
                grid.fit(*data) therefore, the data can also contain groups.

        Returns: A dict containting the results of the grid search.
        """

        grid = GridSearchCV(model, self.parameters, **self.grid_parameters)
        grid.fit(*data)

        try:
            best_score = grid.best_score_
            best_params = grid.best_params_
        except AttributeError:
            best_score = None
            best_params = None

        return {
            'cv_results': pd.DataFrame(grid.cv_results_).to_dict(),
            'best_score': best_score,
            'best_params': best_params,
        }

    @property
    def configuration(self):
        """
        Returns a dict-like representation of this evaluator.
        This is for storing its state in the database.
        """
        grid_parameters = {}
        for name, param in self.grid_parameters.items():
            try:
                json.dumps(param)
                grid_parameters[name] = param
            except TypeError:
                # TODO: store something more useful than nothing
                grid_parameters[name] = None

        return {
            'pipeline_parameters': self.parameters,
            'grid_parameters': grid_parameters,
        }


class CustomCvGridEvaluator(GridEvaluator):
    """ use this evaluator if your dataloader returns a custom cv object. """

    def __init__(self, params, grid_params):
        for param in ['cv']:
            if param in grid_params:
                warnings.warn(
                    f'{param}={grid_params[param]} was set in '
                    'grid_params, but this will be overwritten by the '
                    'evaluation method. Remove this parameter to silence '
                    'this warning.', UserWarning)
        super(CustomCvGridEvaluator, self).__init__(params, grid_params)

    def evaluate(self, model, data):

        assert len(data) == 3
        X, y, cv = data

        if not hasattr(cv, 'split'):
            raise Exception(f'the submitted cv {cv} does not support split()')

        self.grid_parameters['cv'] = cv
        return super().evaluate(model, (X, y))


class FixedSplitGridEvaluator(GridEvaluator):
    """ use this evaluator if your dataloader returns explicit train / test
    samples. This evaluator will then use a PredefinedSplit to create one
    single run for each grid configuration. """

    def __init__(self, params, grid_params):
        self.grid = None
        for param in ['cv']:
            if param in grid_params:
                warnings.warn(
                    f'{param}={grid_params[param]} was set in '
                    'grid_params, but this will be overwritten by the '
                    'evaluation method. Remove this parameter to silence '
                    'this warning.', UserWarning)
        super(FixedSplitGridEvaluator, self).__init__(params, grid_params)

    def evaluate(self, model, data):
        """
        Evaluates the pipline based on the given dataset.

        Args:
            model: the model given in the pipeline.
            data: the data used to load explicit train and test data.
        Returns: A dict containting the results of the grid search.
        """
        assert len(data) == 2
        assert len(data[0]) == 2
        assert len(data[1]) == 2
        (xtrain, ytrain), (xtest, ytest) = data
        # index=-1 means that these samples will never be used for testing
        target_indices = [-1] * len(xtrain) + [0] * len(xtest)
        self.grid_parameters['cv'] = PredefinedSplit(target_indices)

        xtrain = np.array(xtrain)
        ytrain = np.array(ytrain)
        xtest = np.array(xtest)
        ytest = np.array(ytest)

        X = np.concatenate((xtrain, xtest))
        y = np.concatenate((ytrain, ytest))

        return super().evaluate(model, (X, y))


class FixedSplitEvaluator(Evaluator):
    """Evaluator that runs basic classification metrics on the pipline."""

    def __init__(self, scoring):
        """
        Creates a new instance.

        Args:
            scoring: if None, then f1, accuracy, recall, precision and the
                confusion matrix are computed. Otherwise, scoring has to be a
                dict where key is the name of the score and the value contains
                a scorer.
        """
        self.scoring = scoring

    def evaluate(self, model, data):
        """
        Evaluates the pipline based on the given dataset.

        Args:
            model: the model given in the pipeline.
            data: a tuple of (xtrain, ytrain, xtest, ytest)

        Returns: A dict containting f1, accuracy, recall, precision and the
        confusion matrix.
        """
        assert len(data) == 2
        assert len(data[0]) == 2
        assert len(data[1]) == 2
        (xtrain, ytrain), (xtest, ytest) = data
        model.fit(xtrain, ytrain)

        result = {}
        for name, scorer in self.scoring.items():
            score = scorer(model, xtest, ytest)
            if isinstance(score, np.ndarray):
                result[name] = score.tolist()
            else:
                result[name] = score
        return result

    @property
    def configuration(self):
        """
        Returns a dict-like representation of this evaluator.
        This is for storing its state in the database.
        """
        return {
            'scoring': list(self.scoring.keys()),
        }


class ClassificationEvaluator(FixedSplitEvaluator):
    """Evaluator that runns basic classification metrics on the pipline."""

    def __init__(self, average='macro'):
        """
        Creates a new instance.

        Args:
            average: see the sklearn doc for e.g. f1_score .
        """
        super().__init__(
            scoring={
                'f1':
                metrics.make_scorer(metrics.f1_score, average=average),
                'accuracy':
                metrics.get_scorer('accuracy'),
                'recall':
                metrics.make_scorer(metrics.recall_score, average=average),
                'precision':
                metrics.make_scorer(metrics.precision_score, average=average),
                'confusion_matrix':
                metrics.make_scorer(metrics.confusion_matrix),
            })
        self.average = average

    @property
    def configuration(self):
        """
        Returns a dict-like representation of this evaluator.
        This is for storing its state in the database.
        """
        return {
            'average': self.average,
            **super().configuration,
        }
