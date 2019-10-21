import os
import random

import azureml.studio.modules.ml.tests.mltest_utils as mltest_utils
from azureml.studio.common.io.data_table_io import read_data_table
from azureml.studio.common.io.pickle_utils import read_with_pickle_from_file
from azureml.studio.common.parameter_range import ParameterRangeSettings
from azureml.studio.modules.ml.score.score_generic_module.score_generic_module import ScoreModelModule
from azureml.studio.modules.ml.tests.mltest_base import BinaryClassCommonCase
from ..decision_forest_biclassifier.decision_forest_biclassifier import DecisionForestBiClassifier, \
    TwoClassDecisionForestModule, ResamplingMethod, TwoClassDecisionForestModuleDefaultParameters


def script_directory():
    return os.path.dirname(os.path.abspath(__file__))


def _base_library():
    return os.path.join(script_directory(), 'input')


class TestDecisionForestBinaryClassCase(BinaryClassCommonCase):
    entry_class = TwoClassDecisionForestModule
    model_class = DecisionForestBiClassifier
    performance_assert_threshold = 0.95

    default_single_parameter = {
        'resampling_method': ResamplingMethod.Bagging,
        'tree_count': 8,
        'max_depth': 32,
        'random_split_count': 128,
        'min_leaf_sample_count': 1,
    }
    default_range_parameter = {
        'resampling_method': ResamplingMethod.Bagging,
        'ps_tree_count': ParameterRangeSettings.from_literal(TwoClassDecisionForestModuleDefaultParameters.PsTreeCount),
        'ps_max_depth': ParameterRangeSettings.from_literal(TwoClassDecisionForestModuleDefaultParameters.PsMaxDepth),
        'ps_min_leaf_sample_count': ParameterRangeSettings.from_literal(
            TwoClassDecisionForestModuleDefaultParameters.PsMinLeafSampleCount)
    }

    def test_get_tree_count_range(self):
        tree_count_range = random.sample([1, 5, 7, 10, 20, 50, 90], k=4)
        ps_tree_count = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in tree_count_range]))
        clf = self._init_range_model(ps_tree_count=ps_tree_count)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('n_estimators'), tree_count_range)

    def test_get_max_depth_range(self):
        max_depth_range = random.sample([1, 5, 7, 10, 20, 50, 90], k=4)
        ps_max_depth = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in max_depth_range]))
        clf = self._init_range_model(ps_max_depth=ps_max_depth)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('max_depth'), max_depth_range)

    def test_get_min_leaf_sample_count_range(self):
        min_leaf_sample_count_range = random.sample([1, 5, 7, 10, 20, 50, 90], k=4)
        ps_min_leaf_sample_count = ParameterRangeSettings.from_literal(
            ';'.join([str(x) for x in min_leaf_sample_count_range]))
        clf = self._init_range_model(ps_min_leaf_sample_count=ps_min_leaf_sample_count)
        mltest_utils.assert_array_almost_equal(clf.parameter_range.get('min_samples_leaf'), min_leaf_sample_count_range)

    def test_get_tree_count(self):
        tree_count = random.randint(1, 100)
        clf = self._init_model(tree_count=tree_count)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.n_estimators, tree_count)

    def test_get_max_depth(self):
        max_depth = random.randint(1, 100)
        clf = self._init_model(max_depth=max_depth)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.max_depth, max_depth)

    def test_min_leaf_sample_count(self):
        min_leaf_sample_count = random.randint(1, 100)
        clf = self._init_model(min_leaf_sample_count=min_leaf_sample_count)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.min_samples_leaf, min_leaf_sample_count)

    def test_get_resampling_method(self):
        clf = self._init_model(resampling_method=ResamplingMethod.Bagging)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.bootstrap, True)

        clf = self._init_model(resampling_method=ResamplingMethod.Replicate)
        clf.init_model()
        mltest_utils.assert_equal(clf.model.bootstrap, False)

    def test_score_one_class_learner_success(self):
        learner_path = os.path.join(_base_library(), 'decision_forest_one_class_learner', 'data.ilearner')
        learner = read_with_pickle_from_file(learner_path)
        data_path = os.path.join(_base_library(), 'decision_forest_one_class_data', 'data.dataset.parquet')
        data_table = read_data_table(data_path)
        scored_data = ScoreModelModule.run(learner=learner, test_data=data_table, append_or_result_only=True)[0]
        mltest_utils.assert_array_almost_equal(scored_data.data_frame['Scored Probabilities'], 1.0)
