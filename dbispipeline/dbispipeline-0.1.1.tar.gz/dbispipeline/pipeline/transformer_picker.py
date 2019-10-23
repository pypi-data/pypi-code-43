from collections import defaultdict
import warnings

from sklearn.base import TransformerMixin, BaseEstimator, ClassifierMixin
from sklearn.model_selection import ParameterGrid


class TransformerPicker(BaseEstimator, TransformerMixin, ClassifierMixin):
    """
    This stage generates models in which one of many options is selected.
    """

    def __init__(self,
                 available_models=None,
                 selected_model=None,
                 include_bypass=False,
                 optional=False):
        """
        Args:
            available_models: a list of models which should be selected from.
                If you have time on your hands, please enable the use of
                pipelines here.
            selected_model: this parameter is required for the clone operation
                used by gridsearch. It should not be used initially.
            optional: if set to true, one of the resulting configurations will
                have this stage empty.
        """
        self.optional = optional
        if include_bypass:
            self.optional = True
            warnings.warn(
                'the include_bypass parameter is renamed to optional and will'
                'be removed in version 0.6', UserWarning)

        # this is required for the clone operator used in gridsearch
        self.selected_model = selected_model

        # cloned
        if type(available_models) == dict:
            self.available_models = available_models
        else:
            # manually initialized
            self.available_models = {}
            for (key, model) in available_models:
                self.available_models[key] = model
        # TODO: pipeline objects instead

    def generate(self, param_dict=None):
        if param_dict is None:
            param_dict = dict()
        per_model_parameters = defaultdict(lambda: defaultdict(list))

        # collect parameters for each specified model
        for k, values in param_dict.items():
            # example:  randomforest__n_estimators
            model_name = k.split('__')[0]
            param_name = k[len(model_name) + 2:]
            if model_name not in self.available_models:
                raise Exception('no such model: {0}'.format(model_name))
            per_model_parameters[model_name][param_name] = values

        ret = []

        # create instance for cartesion product of all available parameters
        # for each model
        for model_name, param_dict in per_model_parameters.items():
            parameter_sets = ParameterGrid(param_dict)
            for parameters in parameter_sets:
                ret.append((model_name, parameters))

        # for every model that has no specified parameters, add default value
        for model_name in self.available_models.keys():
            if model_name not in per_model_parameters:
                ret.append((model_name, dict()))

        if self.optional:
            ret.append((None, dict(), True))
        return ret

    def get_params(self, **kwargs):
        return {
            'available_models': self.available_models,
            'selected_model': self.selected_model,
            'optional': self.optional
        }

    @property
    def transformer_list(self):
        return self.available_models

    def set_params(self, selected_model, available_models=None,
                   optional=False):
        # the parameters for this method have to be the same than the __init__
        # because of the automatic closing by gridsearch. However, the optional
        # parameter must be recalculated.
        optional = len(selected_model) == 3 and selected_model[2]

        if available_models:
            self.available_models = available_models

        if selected_model[0] is None and optional:
            self.selected_model = None
            self.optional = True
        else:
            if selected_model[0] not in self.available_models:
                raise ValueError(
                    'trying to set selected model {selected_model[0]}, which '
                    f'is not in the available models {available_models}.')
            self.selected_model = self.available_models[selected_model[0]]
            self.selected_model.set_params(**selected_model[1])

    def fit(self, X, y=None, **kwargs):
        if self.optional:
            return self
        else:
            return self.selected_model.fit(X, y, **kwargs)

    def transform(self, X, y=None, **kwargs):
        if self.optional:
            return X
        else:
            return self.selected_model.transform(X, y, **kwargs)

    def predict(self, x):
        if self.optional:
            raise ValueError('a classifier can not be optional')
        return self.selected_model.predict(x)

    def predict_proba(self, x):
        if hasattr(self.selected_model, 'predict_proba'):
            method = getattr(self.selected_model, 'predict_proba', None)
            if callable(method):
                return method(x)
        else:
            raise ValueError('Your model does not support predict_proba')

    def decision_function(self, x):
        if hasattr(self.selected_model, 'decision_function'):
            method = getattr(self.selected_model, 'decision_function', None)
            if callable(method):
                return method(x)
        else:
            raise ValueError('Your model does not support decision_function')
