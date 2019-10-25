# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import tempfile
import unittest

import azureml.dataprep as dprep
import numpy as np
import pandas as pd
from mock import patch
from typing import Dict, Any, List

from azureml.automl.core.constants import FeatureType
from azureml.automl.core.featurization import StreamingFeaturizer
from automl.client.core.common.exceptions import ClientException, DataException
from .utilities import dataframe_as_csv_file


class StreamingFeaturizerTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(StreamingFeaturizerTests, self).__init__(*args, **kwargs)

    def _check_featurization_summary(self,
                                     featurization_summary: Dict[str, Any],
                                     type_detected: str,
                                     engg_feature_count: int,
                                     transformations: List[str],
                                     dropped: str = 'No'):
        self.assertTrue(featurization_summary['TypeDetected'] == type_detected)
        self.assertTrue(featurization_summary['EngineeredFeatureCount'] == engg_feature_count)

        self.assertTrue(len(featurization_summary['Transformations']) == len(transformations))
        self.assertTrue(len(set(featurization_summary['Transformations']) - set(transformations)) == 0)
        self.assertTrue(featurization_summary['Dropped'] == dropped)

    def test_featurize_with_nans(self):
        train_df = _get_xor_dataset()
        self.assertTrue(len(train_df[train_df['col1'].isnull()]) > 0)
        self.assertTrue(len(train_df[train_df['col2'].isnull()]) > 0)
        path = dataframe_as_csv_file(train_df)

        try:
            X_train = (dprep.read_csv(path=path).
                       to_number(columns=['col1', 'col2']))
            streaming_featurizer = StreamingFeaturizer(X_train, 'label')
            streaming_transformer = streaming_featurizer.learn_transformations()
            featurized_X = streaming_transformer.transform(train_df)

            self.assertTrue(len(featurized_X[featurized_X['1'].isnull()]) == 0)
            self.assertTrue(len(featurized_X[featurized_X['2'].isnull()]) == 0)

            self.assertTrue(streaming_featurizer.get_transformed_vector_column_names() == ['1', '2'])

            self.assertTrue(streaming_transformer.get_engineered_feature_names() ==
                            ['col1_MeanImputer', 'col2_MeanImputer'])
            self.assertTrue(len(streaming_transformer.get_featurization_summary()) == 2)

            col1 = next(x for x in streaming_transformer.get_featurization_summary() if x['RawFeatureName'] == 'col1')
            self._check_featurization_summary(col1, FeatureType.Numeric, 1, ['MeanImputer'])

            col2 = next(x for x in streaming_transformer.get_featurization_summary() if x['RawFeatureName'] == 'col2')
            self._check_featurization_summary(col2, FeatureType.Numeric, 1, ['MeanImputer'])

        finally:
            os.remove(path)

    def test_columns_with_sample_weight(self):
        train_set_category_array = np.repeat(['cat', 'bear'], 100)
        label_set_category_array = np.repeat([0, 1], 100)
        weight_set_category_array = np.repeat([0, 0.9], 100)

        train_df = pd.DataFrame({'category': train_set_category_array, 'label': label_set_category_array,
                                 'sample_weight': weight_set_category_array})
        path = dataframe_as_csv_file(train_df)

        try:
            X_train = dprep.read_csv(path=path)
            streaming_featurizer = StreamingFeaturizer(X_train, 'label', 'sample_weight')
            self.assertTrue(streaming_featurizer._weight_column == 'sample_weight')
            self.assertSetEqual(streaming_featurizer._all_training_columns, frozenset({'category'}))

            streaming_transformer = streaming_featurizer.learn_transformations()

            _ = streaming_transformer.transform(train_df)

            # weights columns should not be featurized
            self.assertTrue(streaming_featurizer.get_transformed_vector_column_names() == ['1'],
                            "Expecting just one column to be featurized")

            self.assertTrue(streaming_transformer.get_engineered_feature_names() ==
                            ['category_OneHotEncoder_cat', 'category_OneHotEncoder_bear'])
            self.assertTrue(len(streaming_transformer.get_featurization_summary()) == 1)

            col1 = next(x for x in streaming_transformer.get_featurization_summary()
                        if x['RawFeatureName'] == 'category')
            self._check_featurization_summary(col1, FeatureType.Categorical, 2, ['OneHotEncoder'])
        finally:
            os.remove(path)

    def test_columns_with_no_sample_weight(self):
        train_set_category_array = np.repeat(['cat', 'bear'], 100)
        label_set_category_array = np.repeat([0, 1], 100)

        train_df = pd.DataFrame({'category': train_set_category_array, 'label': label_set_category_array})
        path = dataframe_as_csv_file(train_df)

        try:
            X_train = dprep.read_csv(path=path)
            streaming_featurizer = StreamingFeaturizer(X_train, 'label')
            self.assertTrue(streaming_featurizer._label_column == 'label')
            self.assertSetEqual(streaming_featurizer._all_training_columns, frozenset({'category'}))
        finally:
            os.remove(path)

    def test_categoricals_with_two_categories(self):
        # Expecting categorical data with less than 1000 unique values to be one hot encoded
        train_set_category_array = np.repeat(['cat', 'bear'], 100)
        label_set_category_array = np.repeat([0, 1], 100)
        train_df = pd.DataFrame({'category': train_set_category_array, 'label': label_set_category_array})
        path = dataframe_as_csv_file(train_df)

        try:
            X_train = dprep.read_csv(path=path)
            streaming_featurizer = StreamingFeaturizer(X_train, 'label')
            streaming_transformer = streaming_featurizer.learn_transformations()

            test = np.repeat(['cat', 'bear'], 2)
            test_df = pd.DataFrame({'category': test})
            test_transformed = streaming_transformer.transform(test_df)

            expected_df = pd.DataFrame({'1.cat': [1.0, 1.0, 0.0, 0.0],
                                        '1.bear': [0.0, 0.0, 1.0, 1.0]})
            self.assertEqual(test_transformed['1.cat'].tolist(), expected_df['1.cat'].tolist())
            self.assertEqual(test_transformed['1.bear'].tolist(), expected_df['1.bear'].tolist())
            self.assertTrue(streaming_featurizer.get_transformed_vector_column_names() == ['1'],
                            "Expecting just one column to be featurized")

            self.assertTrue(streaming_transformer.get_engineered_feature_names() ==
                            ['category_OneHotEncoder_cat', 'category_OneHotEncoder_bear'])
            self.assertTrue(len(streaming_transformer.get_featurization_summary()) == 1)

            col1 = next(x for x in streaming_transformer.get_featurization_summary()
                        if x['RawFeatureName'] == 'category')
            self._check_featurization_summary(col1, FeatureType.Categorical, 2, ['OneHotEncoder'])
        finally:
            os.remove(path)

    def test_drop_transformer(self):
        train_array_1 = np.repeat([np.nan], 100)
        train_array_2 = np.repeat(['cat', 'bear'], 50)
        label_array = np.repeat([0], 100)
        train_df = pd.DataFrame({'col1': train_array_1, 'col2': train_array_2, 'label': label_array})
        path = dataframe_as_csv_file(train_df)

        try:
            X_train = dprep.read_csv(path=path)
            streaming_featurizer = StreamingFeaturizer(X_train, 'label')
            streaming_transformer = streaming_featurizer.learn_transformations()
            _ = streaming_transformer.transform(train_df)

            self.assertTrue(len(streaming_featurizer.get_transformed_vector_column_names()) == 1,
                            "Expecting just one featurized column out of two")

            # engineered_feature_names = 'col2_OneHotEncoder_cat' and 'col2_OneHotEncoder_bear'
            # col1 should not be present since it is dropped
            self.assertTrue(len(streaming_transformer.get_engineered_feature_names()) == 2)
            self.assertTrue(len(streaming_transformer.get_featurization_summary()) == 2)

            col1 = next(x for x in streaming_transformer.get_featurization_summary()
                        if x['RawFeatureName'] == 'col1')
            self._check_featurization_summary(
                col1, FeatureType.Ignore, 0, [''], dropped='Yes')
        finally:
            os.remove(path)

    def test_date_time_transformer(self):
        dates = ["2018-01-02", "2018-02-01"]
        col2 = ['0', '1']
        label_array = np.repeat([0], 2)
        train_df = pd.DataFrame({'col1': dates, 'col2': col2, 'label': label_array})
        path = dataframe_as_csv_file(train_df)

        try:
            X_train = dprep.read_csv(path=path, infer_column_types=True)
            streaming_featurizer = StreamingFeaturizer(X_train, 'label')
            streaming_transformer = streaming_featurizer.learn_transformations()
            feat = streaming_transformer.transform(train_df)
            self.assertIsNone(feat.get('col1'), "Expected 'col1' to have been dropped.")

            self.assertTrue(len(streaming_featurizer.get_transformed_vector_column_names()) == 1,
                            "Expecting just one featurized column")

            self.assertTrue(len(streaming_transformer.get_engineered_feature_names()) == 1)
            self.assertTrue(len(streaming_transformer.get_featurization_summary()) == 2)

            col1 = next(x for x in streaming_transformer.get_featurization_summary()
                        if x['RawFeatureName'] == 'col1')
            self._check_featurization_summary(
                col1, FeatureType.Ignore, 0, [''], dropped='Yes')
        finally:
            os.remove(path)

    def test_text_transform(self):
        train_df = pd.DataFrame(
            data=dict(
                review=[
                    "This is great",
                    "I hate it",
                    "Love it",
                    "Do not like it",
                    "Really like it",
                    "I hate it",
                    "I like it a lot",
                    "I kind of hate it",
                    "I do like it",
                    "I really hate it",
                    "It is very good",
                    "I hate it a bunch",
                    "I love it a bunch",
                    "I hate it",
                    "I like it very much",
                    "I hate it very much.",
                    "I really do love it",
                    "I really do hate it",
                    "Love it!",
                    "Hate it!",
                    "I love it",
                    "I hate it",
                    "I love it",
                    "I hate it",
                    "I love it"],
                like=[
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True,
                    False,
                    True]))

        test_reviews = pd.DataFrame(
            data=dict(
                review=[
                    "This is great",
                    "I hate it",
                    "Love it",
                    "Really like it",
                    "I hate it",
                    "I like it a lot",
                    "I love it",
                    "I do like it",
                    "I really hate it",
                    "I love it"]))
        path = dataframe_as_csv_file(train_df)

        try:
            X_train = dprep.read_csv(path=path)
            streaming_featurizer = StreamingFeaturizer(X_train, 'like')

            streaming_transformer = streaming_featurizer.learn_transformations()
            featurized_X = streaming_transformer.transform(train_df)
            self.assertEqual(featurized_X.shape, (25, 55))

            test_transformed = streaming_transformer.transform(test_reviews)
            # 54 because we don't have label column here
            self.assertEqual(test_transformed.shape, (10, 54))

            self.assertTrue(streaming_featurizer.get_transformed_vector_column_names() == ['1'],
                            "Expecting just one column to be featurized")

            self.assertTrue(len(streaming_transformer.get_engineered_feature_names()) == 53)
            self.assertTrue(len(streaming_transformer.get_featurization_summary()) == 1)

            col1 = next(x for x in streaming_transformer.get_featurization_summary()
                        if x['RawFeatureName'] == 'review')
            self._check_featurization_summary(col1, FeatureType.Text, 53, ['TfIdf'])
        finally:
            os.remove(path)

    def test_multiple_text_transforms(self):
        # Each column should have it's own text transformer - they shouldn't be flattened
        series = [_get_text_column(random_seed=i) for i in range(6)]
        train_df = pd.DataFrame({'col1': series[0],
                                 'col2': series[1],
                                 'col3': series[2],
                                 'col4': series[3],
                                 'col5': series[4],
                                 'col6': series[5]})
        path = dataframe_as_csv_file(train_df)

        try:
            X_train = dprep.read_csv(path=path)
            streaming_featurizer = StreamingFeaturizer(X_train, 'col6')

            featurization_transformer = streaming_featurizer.learn_transformations()
            featurized_X = featurization_transformer.transform(train_df)
            self.assertEqual(featurized_X.shape, (10, 211))
            self.assertTrue(len(featurization_transformer.pipeline.steps) == 5,
                            "Expecting 5 separate NGram transformers for 5 input text columns")
            self.assertTrue(streaming_featurizer.get_transformed_vector_column_names() == ['1', '2', '3', '4', '5'])
        finally:
            os.remove(path)

    def test_flatten_similar_transforms(self):
        train_df = _get_categorical_df(columns='ABCD', rows=100, categories=2)
        path = dataframe_as_csv_file(train_df)

        try:
            X_train = dprep.read_csv(path=path)
            streaming_featurizer = StreamingFeaturizer(X_train, 'D')

            featurization_transformer = streaming_featurizer.learn_transformations()
            featurized_X = featurization_transformer.transform(train_df)
            self.assertEqual(featurized_X.shape, (100, 10))
            self.assertTrue(len(featurization_transformer.pipeline.steps) == 1,
                            "Expecting just 1 transformers for the given input data (1 one hot transform)")
        finally:
            os.remove(path)

    def test_onehothash_transform(self):
        train_df = _get_categorical_df(columns='ABCD', rows=100, categories=50)
        path = dataframe_as_csv_file(train_df)

        try:
            X_train = dprep.read_csv(path)
            streaming_featurizer = StreamingFeaturizer(X_train, 'D')

            streaming_transformer = streaming_featurizer.learn_transformations()
            featurized_X = streaming_transformer.transform(train_df)
            self.assertEqual(featurized_X.shape, (100, 196612))

            self.assertTrue(streaming_featurizer.get_transformed_vector_column_names() == ['1', '2', '3'],
                            "Expecting just one column to be featurized")

            self.assertTrue(len(streaming_transformer.get_engineered_feature_names()) == 196608)
            self.assertTrue(len(streaming_transformer.get_featurization_summary()) == 3)

            col1 = next(x for x in streaming_transformer.get_featurization_summary()
                        if x['RawFeatureName'] == 'A')
            self._check_featurization_summary(col1, FeatureType.CategoricalHash, 65536, ['HashOneHotEncoder'])

            col2 = next(x for x in streaming_transformer.get_featurization_summary()
                        if x['RawFeatureName'] == 'B')
            self._check_featurization_summary(col2, FeatureType.CategoricalHash, 65536, ['HashOneHotEncoder'])

            col3 = next(x for x in streaming_transformer.get_featurization_summary()
                        if x['RawFeatureName'] == 'C')
            self._check_featurization_summary(col3, FeatureType.CategoricalHash, 65536, ['HashOneHotEncoder'])
        finally:
            os.remove(path)

    def test_dataflow_extra_columns_in_parsing(self):
        train_df = pd.DataFrame({'col1': ['sample text with \n new line', 'sample text'],
                                 'col2': ['0', '1'],
                                 'label': ['0', '1']})
        path = dataframe_as_csv_file(train_df)

        try:
            X_train = dprep.read_csv(path)
            streaming_featurizer = StreamingFeaturizer(X_train, 'label')
            with self.assertRaises(DataException) as de:
                streaming_featurizer.learn_transformations()
            self.assertTrue("quotes or new-line characters are handled correctly" in str(de.exception))
        finally:
            os.remove(path)

    @patch('azureml.automl.core.column_purpose_detection.columnpurpose_detector.'
           'ColumnPurposeDetector.get_raw_stats_and_column_purposes')
    def test_unsupported_column_purpose(self, get_column_purpose_mock):
        from unittest import mock
        get_column_purpose_mock.return_value = [(mock.MagicMock(), 'unsupported_column_purpose', 'col1')]

        train_df = _get_xor_dataset()
        path = dataframe_as_csv_file(train_df)

        try:
            X_train = (dprep.read_csv(path=path).
                       to_number(columns=['col1', 'col2']))
            streaming_featurizer = StreamingFeaturizer(X_train, 'label')

            with self.assertRaises(ClientException) as ce:
                streaming_featurizer.learn_transformations()
            self.assertTrue("unsupported feature type" in str(ce.exception))
        finally:
            os.remove(path)


def _get_xor_dataset() -> pd.DataFrame:
    return pd.DataFrame({'col1': [0, 0, 1, 1, 0, 1, np.nan, 0, 1],
                         'col2': [0, 1, np.nan, 0, 1, 0, 0, 1, 0],
                         'label': [0, 1, 0, 1, 1, 1, 0, 1, 1]})


def _get_text_column(rows=10, random_seed=37):
    # Return a pandas series of type Text
    import random
    word_list = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt " \
                "ut labore et dolore magna aliqua Ut enim ad minim veniam quis nostrud exercitation ullamco " \
                " laboris nisi ut aliquip ex ea commodo consequat Duis aute irure dolor in reprehenderit " \
                "in voluptate velit esse cillum dolore eu fugiat nulla pariatur Excepteur sint occaecat " \
                "cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum".split(" ")

    random.seed(random_seed)
    sentence = []
    for i in range(rows):
        rand1 = random.randint(0, len(word_list) - 1)
        rand2 = random.randint(1, len(word_list) - 1)
        rand3 = random.randint(2, len(word_list) - 1)
        sentence.append(" ".join([word_list[rand1], word_list[rand2], word_list[rand3]]))

    return sentence


def _get_categorical_df(columns: str, rows: int, categories: int = 10) -> pd.DataFrame:
    # Return a pandas DataFrame made up of multiple categorical columns
    # Each char from 'columns' will combine with a 'rows' to produce a cell value
    # Make index = categories for a hash column
    data = {c: [str(c) + str(i % categories) for i in range(rows)]
            for c in columns}
    return pd.DataFrame(data, range(rows))
