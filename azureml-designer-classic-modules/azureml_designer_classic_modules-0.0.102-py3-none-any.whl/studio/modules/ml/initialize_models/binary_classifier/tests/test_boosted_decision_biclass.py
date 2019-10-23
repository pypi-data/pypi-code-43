import os
import random

import pandas as pd

import azureml.studio.modules.ml.tests.mltest_utils as mltest_utils
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.io.pickle_utils import read_with_pickle_from_file
from azureml.studio.common.parameter_range import ParameterRangeSettings
from azureml.studio.modules.ml.score.score_generic_module.score_generic_module import ScoreModelModule
from azureml.studio.modules.ml.tests.mltest_base import BinaryClassCommonCase
from ..boosted_decision_tree_biclassifier.boosted_decision_tree_biclassifier import \
    BoostDecisionTreeBiClassifier, TwoClassBoostedDecisionTreeModule, TwoClassBoostedDecisionTreeModuleDefaultParameters


def script_directory():
    return os.path.dirname(os.path.abspath(__file__))


def _base_library():
    return os.path.join(script_directory(), 'input')


class TestBoostDecisionTreeBinaryClassCase(BinaryClassCommonCase):
    entry_class = TwoClassBoostedDecisionTreeModule
    model_class = BoostDecisionTreeBiClassifier
    performance_assert_threshold = 0.95

    default_single_parameter = {
        'number_of_leaves': 15,
        'minimum_leaf_instances': 2,
        'learning_rate': 0.2,
        'num_trees': 10,
        'random_number_seed': None
    }
    default_range_parameter = {
        'ps_number_of_leaves': ParameterRangeSettings.from_literal(
            TwoClassBoostedDecisionTreeModuleDefaultParameters.PsNumberOfLeaves),
        'ps_minimum_leaf_instances': ParameterRangeSettings.from_literal(
            TwoClassBoostedDecisionTreeModuleDefaultParameters.PsMinimumLeafInstances),
        'ps_learning_rate': ParameterRangeSettings.from_literal(
            TwoClassBoostedDecisionTreeModuleDefaultParameters.PsLearningRate),
        'ps_num_trees': ParameterRangeSettings.from_literal(
            TwoClassBoostedDecisionTreeModuleDefaultParameters.PsNumTrees),
        'random_number_seed': None
    }

    def test_get_learning_rate_range(self):
        lr_range = random.sample([0.01, 0.05, 0.07, 0.1, 0.2, 0.5, 0.9], k=4)
        ps_initial_learning_rate = ParameterRangeSettings.from_literal(';'.join([str(x) for x in lr_range]))
        clf = self._init_range_model(ps_learning_rate=ps_initial_learning_rate)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('learning_rate'), lr_range)

    def test_get_number_of_leaves_range(self):
        number_of_leaves_range = random.sample([1, 5, 7, 10, 11], k=4)
        ps_number_of_leaves = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in number_of_leaves_range]))
        clf = self._init_range_model(ps_number_of_leaves=ps_number_of_leaves)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('num_leaves'), number_of_leaves_range)

    def test_get_minimum_leaf_instances_range(self):
        minimum_leaf_instances_range = random.sample([1, 5, 7, 10, 20, 50, 90], k=4)
        ps_minimum_leaf_instances = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in minimum_leaf_instances_range]))
        clf = self._init_range_model(ps_minimum_leaf_instances=ps_minimum_leaf_instances)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('min_child_samples'),
                                               minimum_leaf_instances_range)

    def test_get_num_trees_range(self):
        num_trees_range = random.sample([1, 5, 7, 10, 20, 50, 90], k=4)
        ps_num_trees = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in num_trees_range]))
        clf = self._init_range_model(ps_num_trees=ps_num_trees)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('n_estimators'), num_trees_range)

    def test_get_number_of_leaves(self):
        number_of_leaves = random.randint(1, 100)
        clf = self._init_model(number_of_leaves=number_of_leaves)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.num_leaves, number_of_leaves)

    def test_get_minimum_leaf_instances(self):
        minimum_leaf_instances = random.randint(1, 100)
        clf = self._init_model(minimum_leaf_instances=minimum_leaf_instances)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.min_child_samples, minimum_leaf_instances)

    def test_get_learning_rate(self):
        learning_rate = random.random()
        clf = self._init_model(learning_rate=learning_rate)
        clf.init_model()
        mltest_utils.assert_array_almost_equal(clf.model.learning_rate, learning_rate)

    def test_get_num_trees(self):
        num_trees = random.randint(1, 100)
        clf = self._init_model(num_trees=num_trees)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.n_estimators, num_trees)

    def test_score_one_class_learner_success(self):
        learner_path = os.path.join(_base_library(), 'boosted_decision_tree_one_class_learner', 'data.ilearner')
        learner = read_with_pickle_from_file(learner_path)
        data_table = DataTable(pd.DataFrame({'f1': [1, 2], 'f2': [4, 5]}))
        scored_data = ScoreModelModule.run(learner=learner, test_data=data_table, append_or_result_only=True)[0]
        mltest_utils.assert_array_almost_equal(scored_data.data_frame['Scored Probabilities'], 1.0)
