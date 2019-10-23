import random

import numpy as np

import azureml.studio.modules.ml.tests.mltest_utils as mltest_utils
from azureml.studio.common.parameter_range import ParameterRangeSettings
from azureml.studio.modules.ml.tests.mltest_base import RegressionCommonCase
from ..linear_regressor.linear_regressor import \
    SGDLinearRegressor, CreateLinearRegressionModelSolutionMethod, CreateLearnerMode, OrdinaryLeastSquaresRegressor, \
    LinearRegressionModule, LinearRegressionModuleDefaultParameters


class TestSGDRegressorCase(RegressionCommonCase):
    entry_class = LinearRegressionModule
    model_class = SGDLinearRegressor
    performance_assert_threshold = 1.0

    default_sgd_single_parameter = {
        'learning_rate': 0.1,
        'num_iterations': 10,
        'l2_regularizer_weight_ogd': 0.001,
        'normalize_features': False,
        'averaged': True,
        'decrease_learning_rate': True,
        'random_number_seed': None
    }
    default_sgd_range_parameter = {
        'ps_l2_regularizer_weight': ParameterRangeSettings.from_literal(
            LinearRegressionModuleDefaultParameters.PsL2RegularizerWeight),
        'ps_num_iterations': ParameterRangeSettings.from_literal(
            LinearRegressionModuleDefaultParameters.PsNumIterations),
        'ps_learning_rate': ParameterRangeSettings.from_literal(LinearRegressionModuleDefaultParameters.PsLearningRate),
        'normalize_features': False,
        'averaged': True,
        'decrease_learning_rate': True,
        'random_number_seed': None
    }

    default_ols_single_parameter = {
        'l2_regularizer_weight_ols': 0.001,
        'bias': True,
        'random_number_seed': None
    }

    @classmethod
    def _get_single_parameter_dict(cls):
        dp = dict()
        dp.update(cls.default_sgd_single_parameter)
        dp.update({'mode': CreateLearnerMode.SingleParameter,
                   'solution_method': CreateLinearRegressionModelSolutionMethod.OnlineGradientDescent})
        return dp

    @classmethod
    def _get_range_parameter_dict(cls):
        dp = dict()
        dp.update(cls.default_sgd_range_parameter)
        dp.update({'mode': CreateLearnerMode.ParameterRange,
                   'solution_method': CreateLinearRegressionModelSolutionMethod.OnlineGradientDescent})
        return dp

    def test_get_learning_rate_range(self):
        learning_rate_range = random.sample([0.1, 0.5, 0.7, 0.01, 0.02], k=4)
        ps_learning_rate = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in learning_rate_range]))
        clf = self._init_range_model(ps_learning_rate=ps_learning_rate)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('eta0'), learning_rate_range)

    def test_get_num_iterations_range(self):
        num_iterations_range = random.sample([1, 5, 7, 10, 20, 50, 90], k=4)
        ps_num_iterations = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in num_iterations_range]))
        clf = self._init_range_model(ps_num_iterations=ps_num_iterations)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('max_iter'), num_iterations_range)

    def test_get_l2_weight_range(self):
        l2_range = random.sample([0.01, 0.05, 0.07, 0.1, 0.2, 0.5, 0.9], k=4)
        ps_l2_regularizer_weight = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in l2_range]))
        clf = self._init_range_model(ps_l2_regularizer_weight=ps_l2_regularizer_weight)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('alpha'), l2_range)

    def test_get_learning_rate(self):
        learning_rate = random.random()
        clf = self._init_model(learning_rate=learning_rate)
        clf.init_model()
        mltest_utils.assert_array_almost_equal(clf.model.eta0, learning_rate,
                                               err_msg='SGDRegressor: learning_rate was not passed to eta0')

    def test_get_l2_regularizer_weight(self):
        l2_regularizer_weight = random.random()
        clf = self._init_model(l2_regularizer_weight_ogd=l2_regularizer_weight)
        clf.init_model()
        mltest_utils.assert_array_almost_equal(clf.model.alpha, l2_regularizer_weight,
                                               err_msg='SGDRegressor: l2_regularizer_weight was not passed to alpha')
        mltest_utils.assert_equal(clf.model.penalty, 'l2', 'SGDRegressor: penalty should set to l2')

    def test_get_num_iterations(self):
        num_iterations = random.randint(1, 100)
        clf = self._init_model(num_iterations=num_iterations)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.max_iter, num_iterations,
                                  'SGDRegressor: num_iterations was not passed to max_iter')

    def test_get_decrease_learning_rate(self):
        clf = self._init_model(decrease_learning_rate=True)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.learning_rate, 'invscaling',
                                  'SGDRegressor: learning_rate != invscaling when decrease_learning_rate is True')

        clf = self._init_model(decrease_learning_rate=False)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.learning_rate, 'constant',
                                  'SGDRegressor: learning_rate != constant when decrease_learning_rate is False')

    def test_l2_regularizer_weight_work(self):
        l2_regularizer_weight_large = 1.0
        l2_regularizer_weight_small = 0.001
        clf = self._init_model(l2_regularizer_weight_ogd=l2_regularizer_weight_large)
        clf.init_model()
        clf.train(mltest_utils.regression_sample.train_df, label_column_name='label')
        coef1 = clf.model.coef_

        clf2 = self._init_model(l2_regularizer_weight_ogd=l2_regularizer_weight_small)
        clf2.init_model()
        clf2.train(mltest_utils.regression_sample.train_df, label_column_name='label')
        coef2 = clf2.model.coef_

        model_weight_sum = np.sum(coef1 ** 2)
        model_weight_sum2 = np.sum(coef2 ** 2)
        # larger l2_regularizer got lower weight.
        mltest_utils.assert_greater(model_weight_sum2, model_weight_sum,
                                    'SGDRegressor: l2_regularizer_weight did not work')

    def test_num_iterations_work(self):
        num_iterations_small = 1
        num_iterations_large = 100
        clf = self._init_model(num_iterations=num_iterations_small)
        clf.init_model()
        error_value = mltest_utils.get_ase(clf)

        clf2 = self._init_model(num_iterations=num_iterations_large)
        clf2.init_model()
        error_value2 = mltest_utils.get_ase(clf2)

        mltest_utils.assert_greater(error_value, error_value2, 'SGDRegressor: num_iterations did not work')


class TestOLSRegressorCase(RegressionCommonCase):
    entry_class = LinearRegressionModule
    model_class = OrdinaryLeastSquaresRegressor
    performance_assert_threshold = 1.2
    personal_setting = {}

    default_sgd_single_parameter = {
        'learning_rate': 0.1,
        'num_iterations': 10,
        'l2_regularizer_weight_ogd': 0.001,
        'normalize_features': False,
        'averaged': True,
        'decrease_learning_rate': True,
        'random_number_seed': None
    }
    default_sgd_range_parameter = {
        'ps_l2_regularizer_weight': None,
        'ps_num_iterations': None,
        'ps_learning_rate': None,
    }

    default_ols_single_parameter = {
        'l2_regularizer_weight_ols': 0.001,
        'bias': True,
        'random_number_seed': None
    }

    def _get_single_parameter_dict(self):
        dp = dict()
        dp.update(self.default_ols_single_parameter)
        dp.update({'mode': CreateLearnerMode.SingleParameter,
                   'solution_method': CreateLinearRegressionModelSolutionMethod.OrdinaryLeastSquares})
        return dp

    def _get_range_parameter_dict(self):
        dp = dict()
        dp.update(self.default_ols_single_parameter)
        dp.update({'mode': CreateLearnerMode.ParameterRange,
                   'solution_method': CreateLinearRegressionModelSolutionMethod.OrdinaryLeastSquares})
        return dp

    def test_get_l2_regularizer_weight(self):
        l2_regularizer_weight = random.random()
        clf = self._init_model(l2_regularizer_weight_ols=l2_regularizer_weight)
        clf.init_model()
        mltest_utils.assert_array_almost_equal(
            clf.model.alpha,
            l2_regularizer_weight,
            err_msg='OrdinaryLeastSquaresRegressor: l2_regularizer_weight was not passed to alpha')

    def test_get_bias(self):
        for bias in (True, False):
            clf = self._init_model(bias=bias)
            clf.init_model()
            mltest_utils.assert_array_almost_equal(
                clf.model.fit_intercept,
                bias,
                err_msg='OrdinaryLeastSquaresRegressor: test_get_bias was not passed to fit_intercept')

    def test_l2_regularizer_weight_work(self):
        l2_regularizer_weight_large = 1.0
        l2_regularizer_weight_small = 0.001
        clf = self._init_model(l2_regularizer_weight_ols=l2_regularizer_weight_large)
        clf.init_model()
        clf.train(mltest_utils.regression_sample.train_df, label_column_name='label')
        coef1 = clf.model.coef_

        clf2 = self._init_model(l2_regularizer_weight_ols=l2_regularizer_weight_small)
        clf2.init_model()
        clf2.train(mltest_utils.regression_sample.train_df, label_column_name='label')
        coef2 = clf2.model.coef_

        model_weight_sum = np.sum(coef1 ** 2)
        model_weight_sum2 = np.sum(coef2 ** 2)
        # larger l2_regularizer got lower weight.
        mltest_utils.assert_greater(model_weight_sum2, model_weight_sum,
                                    'SGDRegressor: l2_regularizer_weight did not work')
