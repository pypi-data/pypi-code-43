import random

import azureml.studio.modules.ml.tests.mltest_utils as mltest_utils
from azureml.studio.common.parameter_range import ParameterRangeSettings
from azureml.studio.modules.ml.tests.mltest_base import BinaryClassCommonCase
from ..average_perceptron_biclassifier.average_perceptron_classifier import AveragePerceptronBiClassifier, \
    TwoClassAveragedPerceptronModule, TwoClassAveragedPerceptronModuleDefaultParameters


class TestAPBinaryClassCase(BinaryClassCommonCase):
    entry_class = TwoClassAveragedPerceptronModule
    model_class = AveragePerceptronBiClassifier
    performance_assert_threshold = 0.90
    default_single_parameter = {
        'initial_learning_rate': 1.0,
        'maximum_number_of_iterations': 20,
        'random_number_seed': None,
    }
    default_range_parameter = {
        'ps_initial_learning_rate': ParameterRangeSettings.from_literal(
            TwoClassAveragedPerceptronModuleDefaultParameters.PsInitialLearningRate),
        'ps_maximum_number_of_iterations': ParameterRangeSettings.from_literal(
            TwoClassAveragedPerceptronModuleDefaultParameters.PsMaximumNumberOfIterations),
        'random_number_seed': None,
    }

    def test_get_initial_learning_rate(self):
        initial_learning_rate = random.random()
        clf = self._init_model(initial_learning_rate=initial_learning_rate)
        clf.init_model()
        mltest_utils.assert_array_almost_equal(clf.model.eta0, initial_learning_rate)

    def test_get_maximum_number_of_iterations(self):
        maximum_number_of_iterations = random.randint(1, 100)

        clf = self._init_model(maximum_number_of_iterations=maximum_number_of_iterations)
        clf.init_model()
        mltest_utils.assert_array_almost_equal(clf.model.max_iter, maximum_number_of_iterations)

    def test_get_initial_learning_rate_range(self):
        lr_range = random.sample([0.01, 0.05, 0.07, 0.1, 0.2, 0.5, 0.9], k=4)
        ps_initial_learning_rate = ParameterRangeSettings.from_literal(';'.join([str(x) for x in lr_range]))
        clf = self._init_range_model(ps_initial_learning_rate=ps_initial_learning_rate)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('eta0'), lr_range)

    def test_get_maximum_number_of_iterations_range(self):
        max_iters_range = random.sample([1, 5, 7, 10, 20, 50, 90], k=4)
        ps_maximum_number_of_iterations = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in max_iters_range]))
        clf = self._init_range_model(ps_maximum_number_of_iterations=ps_maximum_number_of_iterations)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('max_iter'), max_iters_range)

    def test_maximum_number_of_iterations_work(self):
        maximum_number_of_iterations_1 = 1
        maximum_number_of_iterations_2 = 20

        clf = self._init_model(maximum_number_of_iterations=maximum_number_of_iterations_1)
        clf.init_model()
        _ = mltest_utils.get_f1(clf)

        clf2 = self._init_model(maximum_number_of_iterations=maximum_number_of_iterations_2)
        clf2.init_model()
        _ = mltest_utils.get_f1(clf2)

        mltest_utils.assert_less(clf.model.n_iter_, clf2.model.n_iter_)
        mltest_utils.assert_less_equal(clf2.model.n_iter_, maximum_number_of_iterations_2)
        mltest_utils.assert_equal(clf.model.n_iter_, maximum_number_of_iterations_1)
