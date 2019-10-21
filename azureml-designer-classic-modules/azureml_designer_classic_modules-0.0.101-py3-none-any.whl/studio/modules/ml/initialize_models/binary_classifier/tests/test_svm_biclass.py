import random

import azureml.studio.modules.ml.tests.mltest_utils as mltest_utils
from azureml.studio.common.parameter_range import ParameterRangeSettings
from azureml.studio.modules.ml.tests.mltest_base import BinaryClassCommonCase
from ..support_vector_machine_biclassifier.support_vector_machine_biclassifier import \
    SupportVectorMachineBiClassifier, TwoClassSupportVectorMachineModule, \
    TwoClassSupportVectorMachineModuleDefaultParameters


class TestSVMBinaryClassCase(BinaryClassCommonCase):
    entry_class = TwoClassSupportVectorMachineModule
    model_class = SupportVectorMachineBiClassifier
    performance_assert_threshold = 0.95
    default_single_parameter = {
        'num_iterations': 10,
        'l1_lambda': 0.01,
        'normalize_features': True,
        'perform_projection': False,
        'random_number_seed': None
    }
    default_range_parameter = {
        'ps_num_iterations': ParameterRangeSettings.from_literal(
            TwoClassSupportVectorMachineModuleDefaultParameters.PsNumIterations),
        'ps_l1_lambda': ParameterRangeSettings.from_literal(
            TwoClassSupportVectorMachineModuleDefaultParameters.PsL1Lambda),
        'normalize_features': True,
        'perform_projection': False,
        'random_number_seed': None
    }

    def test_get_num_iterations_range(self):
        num_iterations_range = random.sample([1, 5, 7, 10, 20, 50, 90], k=4)
        ps_num_iterations = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in num_iterations_range]))
        clf = self._init_range_model(ps_num_iterations=ps_num_iterations)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('max_iter'), num_iterations_range)

    def test_get_l1_lambda_range(self):
        l1_lambda_range = random.sample([0.01, 0.05, 0.07, 0.1, 0.2, 0.5, 0.9], k=4)
        ps_l1_lambda = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in l1_lambda_range]))
        clf = self._init_range_model(ps_l1_lambda=ps_l1_lambda)
        c_list = clf.parameter_range.get('C')
        model_l1_lambda = [clf.parameter_mapping['C'].inverse_func(x) for x in c_list]
        mltest_utils.assert_array_almost_equal(model_l1_lambda, l1_lambda_range)

    def test_get_num_iterations(self):
        num_iterations = random.randint(1, 100)
        clf = self._init_model(num_iterations=num_iterations)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.max_iter, num_iterations)

    def test_get_l1_lambda(self):
        l1_lambda = random.random()
        clf = self._init_model(l1_lambda=l1_lambda)
        clf.init_model()
        mltest_utils.assert_array_almost_equal(clf.model.C, 1 / (2 * l1_lambda))

    def test_num_iterations_work(self):
        num_iterations_small = 1
        num_iterations_large = 100
        clf = self._init_model(num_iterations=num_iterations_small)
        clf.init_model()
        error_value = mltest_utils.get_f1(clf)

        clf2 = self._init_model(num_iterations=num_iterations_large)
        clf2.init_model()
        error_value2 = mltest_utils.get_f1(clf2)

        mltest_utils.assert_less(error_value, error_value2, )
