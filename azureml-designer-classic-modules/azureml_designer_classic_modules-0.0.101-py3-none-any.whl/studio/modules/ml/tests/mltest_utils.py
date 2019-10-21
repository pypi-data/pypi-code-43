import os
import unittest

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris, load_breast_cancer
from sklearn.metrics import mean_absolute_error, f1_score, accuracy_score
from sklearn.model_selection import train_test_split

from azureml.studio.modulehost.constants import ElementTypeName
from azureml.studio.modules.ml.common.constants import ScoreColumnConstants

_test_case = unittest.TestCase()
assert_equal = _test_case.assertEqual
assert_not_equal = _test_case.assertNotEqual
assert_raises = _test_case.assertRaises
SkipTest = unittest.case.SkipTest
assert_dict_equal = _test_case.assertDictEqual
assert_in = _test_case.assertIn
assert_not_in = _test_case.assertNotIn
assert_less = _test_case.assertLess
assert_greater = _test_case.assertGreater
assert_less_equal = _test_case.assertLessEqual
assert_greater_equal = _test_case.assertGreaterEqual
assert_array_almost_equal = np.testing.assert_array_almost_equal
assert_array_equal = np.testing.assert_array_equal


def _script_directory():
    return os.path.dirname(os.path.abspath(__file__))


def input_dataset_base_library():
    return os.path.join(_script_directory(), 'inputs')


class SampleData:
    _train_x = pd.DataFrame()
    _train_y = pd.Series()
    _train_df = _train_x
    _train_df['label'] = _train_y

    def __init__(self):
        pass

    @property
    def train_df(self):
        return self._train_df.copy()

    @property
    def train_x(self):
        return self._train_x.copy()

    @property
    def train_y(self):
        return self._train_y.copy()

    @property
    def split_data(self):
        train, valid = train_test_split(self._train_df, test_size=0.25, random_state=42)
        train.reset_index(drop=True, inplace=True)
        valid.reset_index(drop=True, inplace=True)
        return train, valid


# Test Data
# regression data
class RegressionSample(SampleData):
    def __init__(self):
        super().__init__()
        X = np.array([[-2, -1], [-1, -1], [-1, -2], [1, 0], [0, 1], [1, 1], [1, 2], [2, 1]])
        self._train_x = pd.DataFrame(X, columns=['f1', 'f2'])
        self._train_y = pd.Series(([-5, -3, -4, -2, 1, 3, 4, 5]))
        self._train_df = self._train_x.copy()
        self._train_df['label'] = self._train_y
        self.label_name = 'label'


class MultiClassSample(SampleData):
    def __init__(self):
        super().__init__()
        X, y = load_iris(return_X_y=True)
        self._train_x = pd.DataFrame(X, columns=['f1', 'f2', 'f3', 'f4'])
        self._train_y = pd.Series(y)
        self._train_df = self._train_x.copy()
        self._train_df['flower_type'] = self._train_y
        self.label_name = 'flower_type'


class BinaryClassSample(SampleData):
    def __init__(self):
        super().__init__()
        X, y = load_breast_cancer(return_X_y=True)
        self._train_x = pd.DataFrame(X, columns=[f'f{i}' for i in range(30)])
        self._train_y = pd.Series(y)
        self._train_df = self._train_x.copy()
        self._train_df['label'] = self._train_y
        self.label_name = 'label'


regression_sample = RegressionSample()
multi_class_sample = MultiClassSample()
binary_class_sample = BinaryClassSample()


def get_ase(learner):
    train_df = regression_sample.train_df
    if not learner.is_trained:
        learner.train(train_df, label_column_name='label')
    y = learner.predict(regression_sample.train_df)
    y = y[ScoreColumnConstants.ScoredLabelsColumnName]
    return mean_absolute_error(y_true=regression_sample.train_y, y_pred=y)


def get_accuracy(learner):
    train_df = multi_class_sample.train_df
    if not learner.is_trained:
        learner.train(train_df, label_column_name='flower_type')
    y = learner.predict(multi_class_sample.train_df)
    y = y[ScoreColumnConstants.ScoredLabelsColumnName]
    y = y.astype('int')
    return accuracy_score(y_true=multi_class_sample.train_y, y_pred=y)


def get_f1(learner):
    train_df = binary_class_sample.train_df
    if not learner.is_trained:
        learner.train(train_df, label_column_name='label')
    y = learner.predict(binary_class_sample.train_df)
    y = y[ScoreColumnConstants.ScoredLabelsColumnName]
    y = y.astype('int')
    return f1_score(y_true=binary_class_sample.train_y, y_pred=y)


def assert_data_table_equals(data_table_ref, data_table_now):
    """
    check two data table is equals.
    1. their column names
    2. not float column: strict equals
    3. float column: almost equals up to desired precision.
    :param data_table_ref: reference data table
    :param data_table_now: new output data table
    :return: None
    """
    assert set(data_table_now.column_names) == set(data_table_ref.column_names)
    for column_name in data_table_ref.column_names:
        s1 = data_table_now.get_column(column_name)
        s2 = data_table_ref.get_column(column_name)
        if data_table_now.get_element_type(column_name) == ElementTypeName.FLOAT:
            assert_array_almost_equal(s1, s2)
        else:
            assert_array_equal(s1, s2)
