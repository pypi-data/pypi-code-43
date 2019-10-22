from typing import Union, Callable, List

import numpy as np
import optuna

from yotuyu.logger import logger


class Estimator:
    def __init__(self,
                 train_ds,
                 valid_ds,
                 metrics: Callable[[np.ndarray, np.ndarray], Union[float, np.ndarray]] = None,
                 models: List = None):
        self.train_ds = train_ds
        self.train_data, self.train_target = train_ds

        self.valid_ds = valid_ds
        self.valid_data, self.valid_target = valid_ds

        self.metrics = metrics
        self.models = models

    def get_best_estimator(self):
        pass

    def fit(self, params):
        if self.models is None:
            raise Exception('target models are not defined.')
        if self.metrics is None:
            raise Exception('target metrics are not defined.')

        best_model = None
        best_score = None

        logger.info('start search')
        for model_cls in self.models:
            # gain tuned model
            study = optuna.create_study()
            objective = self.objective_func(model_cls, params)
            study.optimize(objective, n_trials=100)
            best_params = study.best_params

            # select best model
            if best_model is None:
                best_model = self.__model_restore_from_dict(model_cls(), best_params)
                best_model.fit(self.train_data, self.train_target)
                best_score = self.metrics(best_model.predict(self.valid_data), self.valid_target)

            model = self.__model_restore_from_dict(model_cls(), best_params)
            model.fit(self.train_data, self.train_target)
            score = self.metrics(model.predict(self.valid_data), self.valid_target)
            if score > best_score:
                best_model = model
        logger.info(f"best model:{best_model}")
        return best_model

    @staticmethod
    def __model_restore_from_dict(model, param):
        for key in param.keys():
            if key in model.__dict__:
                model.__dict__[key] = param[key]
        return model

    def objective_func(self, model_cls, params):
        def objective(trial):
            model_param = {}
            for param in params[model_cls]:
                key = param['key']

                target = None
                if param['type'] == 'categorical':
                    target = trial.suggest_categorical(key, param['items'])
                elif param['type'] == 'loguniform':
                    target = trial.suggest_loguniform(key, param['items'][0], param['items'][1])
                elif param['type'] == 'int':
                    target = trial.suggest_int(key, param['items'][0], param['items'][1])
                model_param[key] = target

            model = self.__model_restore_from_dict(model_cls(), model_param)

            model.fit(self.train_data, self.train_target)
            valid_pred = model.predict(self.valid_data)
            return self.metrics(self.valid_target, valid_pred)

        return objective
