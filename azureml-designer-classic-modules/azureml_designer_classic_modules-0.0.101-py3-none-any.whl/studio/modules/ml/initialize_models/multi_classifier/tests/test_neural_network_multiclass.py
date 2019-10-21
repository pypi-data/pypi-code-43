import random

import azureml.studio.modules.ml.tests.mltest_utils as mltest_utils
from azureml.studio.common.parameter_range import ParameterRangeSettings
from azureml.studio.modules.ml.tests.mltest_base import MultiClassCommonCase
from ..neural_network_multiclassifier.neural_network_multiclassifier import \
    NeuralNetworkMultiClassifier, NeuralNetworkMultiClassifierSetting, MulticlassNeuralNetworkModule, \
    CreateNeuralNetworkRegressionModelNeuralNetworkTopology, MulticlassNeuralNetworkModuleDefaultParameters


class TestNNMultiCase(MultiClassCommonCase):
    entry_class = MulticlassNeuralNetworkModule
    model_class = NeuralNetworkMultiClassifier
    setting_factory_class = NeuralNetworkMultiClassifierSetting
    performance_assert_threshold = 0.95
    default_single_parameter = {
        'initial_weights_diameter': 0.1,
        'learning_rate': 0.1,
        'momentum': 0.0,
        'num_hidden_nodes': str(100),
        'num_iterations': 500,
        'shuffle': True,
        'random_number_seed': None,
        'neural_network_topology': CreateNeuralNetworkRegressionModelNeuralNetworkTopology.DefaultHiddenLayers
    }
    default_range_parameter = {
        'initial_weights_diameter': 0.1,
        'momentum': 0.0,
        'shuffle': True,
        'random_number_seed': None,
        'neural_network_topology': CreateNeuralNetworkRegressionModelNeuralNetworkTopology.DefaultHiddenLayers,
        'ps_learning_rate': ParameterRangeSettings.from_literal(
            MulticlassNeuralNetworkModuleDefaultParameters.PsLearningRate),
        'ps_num_iterations': ParameterRangeSettings.from_literal(
            MulticlassNeuralNetworkModuleDefaultParameters.PsNumIterations),
        'neural_network_topology_for_range':
            CreateNeuralNetworkRegressionModelNeuralNetworkTopology.DefaultHiddenLayers,
        'num_hidden_nodes_for_range': str(100),
    }

    def test_get_learning_rate_range(self):
        learning_rate_range = random.sample([0.1, 0.5, 0.7, 0.01, 0.02], k=4)
        ps_learning_rate = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in learning_rate_range]))
        clf = self._init_range_model(ps_learning_rate=ps_learning_rate)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('learning_rate_init'), learning_rate_range)

    def test_get_num_iterations_range(self):
        num_iterations_range = random.sample([1, 5, 7, 10, 20, 50, 90], k=4)
        ps_num_iterations = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in num_iterations_range]))
        clf = self._init_range_model(ps_num_iterations=ps_num_iterations)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('max_iter'), num_iterations_range)

    def test_get_learning_rate(self):
        learning_rate = random.randint(1, 100) / 10000.0
        clf = self._init_model(learning_rate=learning_rate)
        clf.init_model()
        mltest_utils.assert_array_almost_equal(clf.model.learning_rate_init, learning_rate)

    def test_get_num_hidden_nodes(self):
        num_hidden_nodes = [random.randint(1, 100)]
        num_hidden_str = ','.join([str(x) for x in num_hidden_nodes])
        clf = self._init_model(num_hidden_nodes=num_hidden_str)
        clf.init_model()
        mltest_utils.assert_array_equal(clf.model.hidden_layer_sizes, num_hidden_nodes)

    def test_get_num_iterations(self):
        num_iterations = random.randint(1, 100)
        clf = self._init_model(num_iterations=num_iterations)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.max_iter, num_iterations)

    def test_get_shuffle(self):
        clf = self._init_model(shuffle=True)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.shuffle, True)

        clf = self._init_model(shuffle=False)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.shuffle, False)

    def test_get_momentum(self):
        momentum = random.random()
        clf = self._init_model(momentum=momentum)
        clf.init_model()
        mltest_utils.assert_array_almost_equal(clf.model.momentum, momentum)

    def test_num_iterations_work(self):
        num_iterations_small = 1
        num_iterations_large = 100
        clf = self._init_model(num_iterations=num_iterations_small)
        clf.init_model()
        accuracy_value = mltest_utils.get_accuracy(clf)

        clf2 = self._init_model(num_iterations=num_iterations_large)
        clf2.init_model()
        accuracy_value2 = mltest_utils.get_accuracy(clf2)

        mltest_utils.assert_less(accuracy_value, accuracy_value2, )
