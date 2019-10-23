import random

import azureml.studio.modules.ml.tests.mltest_utils as mltest_utils
from azureml.studio.common.parameter_range import ParameterRangeSettings
from azureml.studio.modules.ml.tests.mltest_base import MultiClassCommonCase
from ..decision_forest_multiclassifier.decision_forest_multiclassifier import ResamplingMethod, \
    DecisionForestMultiClassifier, MulticlassDecisionForestModule, MulticlassDecisionForestModuleDefaultParameters


class TestDTMultiCase(MultiClassCommonCase):
    entry_class = MulticlassDecisionForestModule
    model_class = DecisionForestMultiClassifier
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
        'ps_tree_count': ParameterRangeSettings.from_literal(
            MulticlassDecisionForestModuleDefaultParameters.PsTreeCount),
        'ps_max_depth': ParameterRangeSettings.from_literal(
            MulticlassDecisionForestModuleDefaultParameters.PsMaxDepth),
        'ps_min_leaf_sample_count': ParameterRangeSettings.from_literal(
            MulticlassDecisionForestModuleDefaultParameters.PsMinLeafSampleCount)
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
