import random

import numpy as np
import pandas as pd
import pytest

import azureml.studio.common.error as error_setting
import azureml.studio.modules.ml.tests.mltest_utils as mltest_utils
from azureml.studio.modules.ml.common.metric_calculator import safe_divide
from azureml.studio.modules.ml.initialize_models.regressor.bayesian_linear_regression.bayesian_linear_regression \
    import BayesianLinearRegressionModule, BayesianLinearRegressor
from azureml.studio.modules.ml.tests.mltest_base import RegressionCommonCase


@pytest.fixture
def dataset_with_single_instance():
    data = pd.DataFrame(
        {
            'feature': [10],
            'label': [1]
        }
    )
    return data


@pytest.fixture
def dataset_with_zero_target_variance():
    data = pd.DataFrame(
        {
            'feature': [-10, 10],
            'label': [1, 1]
        }
    )
    return data


class TestBayesianLinearRegressorCase(RegressionCommonCase):
    entry_class = BayesianLinearRegressionModule
    model_class = BayesianLinearRegressor
    performance_assert_threshold = 0.9
    default_single_parameter = {
        'regularizer': 1.0,
        'allow_unknown_levels': True
    }

    @classmethod
    def _get_single_parameter_dict(cls):
        dp = dict()
        dp.update(cls.default_single_parameter)
        return dp

    @classmethod
    def _get_range_parameter_dict(cls):
        return cls._get_single_parameter_dict()

    def test_get_regularizer(self):
        actual_regularizer = random.random()
        clf = self._init_model(regularizer=actual_regularizer)
        clf.init_model()
        clf.train(mltest_utils.regression_sample.train_df, label_column_name='label')
        model_regularizer = clf.model.lambda_1 / clf.model.alpha_1
        mltest_utils.assert_array_almost_equal(model_regularizer, actual_regularizer,
                                               err_msg='Regularizer was not passed to model parameters.')

    def test_zero_target_variance(self, dataset_with_zero_target_variance):
        clf = self._init_model()
        clf.init_model()
        clf.train(dataset_with_zero_target_variance, label_column_name='label')
        expect_noise_precision_parameter = np.abs(safe_divide(1, clf.setting.noise_variance_uniform))
        actual_noise_precision_parameter = clf.setting.noise_precision_parameter
        mltest_utils.assert_array_almost_equal(expect_noise_precision_parameter, actual_noise_precision_parameter,
                                               err_msg='Noise precision parameter is not calculated correctly '
                                                       'when target variance is zero.')

    def test_single_instance(self, dataset_with_single_instance):
        clf = self._init_model()
        clf.init_model()
        with pytest.raises(error_setting.TooFewRowsInDatasetError):
            clf.train(dataset_with_single_instance, label_column_name='label')
