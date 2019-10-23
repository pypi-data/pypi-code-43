import random

import numpy as np

import azureml.studio.modules.ml.tests.mltest_utils as mltest_utils
from azureml.studio.common.parameter_range import ParameterRangeSettings
from azureml.studio.modules.ml.tests.mltest_base import BinaryClassCommonCase
from ..logistic_regression_biclassifier.logistic_regression_biclassifier import LogisticRegressionBiClassifier, \
    TwoClassLogisticRegressionModule, TwoClassLogisticRegressionModuleDefaultParameters


class TestLRBinaryClassCase(BinaryClassCommonCase):
    entry_class = TwoClassLogisticRegressionModule
    model_class = LogisticRegressionBiClassifier
    performance_assert_threshold = 0.95

    default_single_parameter = {
        'optimization_tolerance': 1e-07,
        'l2_weight': 1.0,
        'memory_size': 20,
        'random_number_seed': None
    }
    default_range_parameter = {
        'ps_optimization_tolerance': ParameterRangeSettings.from_literal(
            TwoClassLogisticRegressionModuleDefaultParameters.PsOptimizationTolerance),
        'ps_l2_weight': ParameterRangeSettings.from_literal(
            TwoClassLogisticRegressionModuleDefaultParameters.PsL2Weight),
        'ps_memory_size': ParameterRangeSettings.from_literal(
            TwoClassLogisticRegressionModuleDefaultParameters.PsMemorySize),
        'random_number_seed': None
    }

    def test_get_optimization_tolerance_range(self):
        optimization_tolerance_range = random.sample([1, 5, 7, 10, 20, 50, 90], k=4)
        ps_optimization_tolerance = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in optimization_tolerance_range]))
        clf = self._init_range_model(ps_optimization_tolerance=ps_optimization_tolerance)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('tol'), optimization_tolerance_range)

    def test_get_l2_weight_range(self):
        l2_weight_range = random.sample([0.1, 0.5, 0.7, 0.01, 0.02], k=4)
        ps_l2_weight = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in l2_weight_range]))
        clf = self._init_range_model(ps_l2_weight=ps_l2_weight)
        c_list = clf.parameter_range.get('C')
        model_l2_weight = [clf.parameter_mapping['C'].inverse_func(x) for x in c_list]
        mltest_utils.assert_array_almost_equal(model_l2_weight, l2_weight_range)

    def test_get_l2_weight(self):
        l2_weight = random.random()
        clf = self._init_model(l2_weight=l2_weight)
        clf.init_model()
        mltest_utils.assert_array_almost_equal(1 / clf.model.C, l2_weight)
        mltest_utils.assert_equal(clf.model.penalty, 'l2')

    def test_get_optimization_tolerance(self):
        optimization_tolerance = random.random()
        clf = self._init_model(optimization_tolerance=optimization_tolerance)
        clf.init_model()
        mltest_utils.assert_array_almost_equal(clf.model.tol, optimization_tolerance)

    def test_l2_weight_work(self):
        l2_weight_large = 1.0
        l2_weight_small = 0.01
        clf = self._init_model(l2_weight=l2_weight_large)
        clf.train(mltest_utils.binary_class_sample.train_df, label_column_name='label')
        coef1 = clf.model.coef_

        clf2 = self._init_model(l2_weight=l2_weight_small)
        clf2.train(mltest_utils.binary_class_sample.train_df, label_column_name='label')
        coef2 = clf2.model.coef_

        model_weight_sum = np.sum(coef1 ** 2)
        model_weight_sum2 = np.sum(coef2 ** 2)
        mltest_utils.assert_greater(model_weight_sum2, model_weight_sum)
