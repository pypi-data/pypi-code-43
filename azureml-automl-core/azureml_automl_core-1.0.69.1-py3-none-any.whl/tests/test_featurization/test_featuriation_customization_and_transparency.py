import unittest
import numpy as np
import pandas as pd

from azureml.automl.core.featurization import DataTransformer, FeaturizationConfig
from azureml.automl.core.constants import FeatureType as _FeatureType


class FeaturizationCustomizationAndTransparencyTest(unittest.TestCase):
    def setUp(self):
        self.test_df = pd.DataFrame({
            "transaction_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "user_id": [1, 1, 2, 1, np.nan, 2, 3, 3],
            "amount": [500, 600, 300, 100, 80, 120, 30, 20],
            "tag": ['apple', 'avocado', 'banana', 'cherry', 'lime', 'mango', 'lime', 'mango'],
            "transaction_time": pd.date_range('2014-01-01 08:00:50', periods=8, freq='12h')
        })

    def test_feature_type_customization(self):
        transformer = DataTransformer("classification")
        features = transformer.fit_transform(self.test_df)
        feature_names = transformer.get_engineered_feature_names()
        assert (features is not None)
        assert len(feature_names) == 14
        assert (features.shape[1] == 14)
        feature_types_stats = transformer.get_stats_feature_type_summary(list(self.test_df))
        expected_feature_types = [('transaction_id', 'Numeric'), ('user_id', 'Numeric'),
                                  ('amount', 'Numeric'), ('tag', 'Ignore'),
                                  ('transaction_time', 'DateTime')]
        assert len(expected_feature_types) == len(feature_types_stats)
        for i, feature_types_stat in enumerate(feature_types_stats):
            self.assertEqual(feature_types_stat['column name'], expected_feature_types[i][0])
            self.assertEqual(feature_types_stat['feature type'], expected_feature_types[i][1])

        # customized column feature type
        feature_config = FeaturizationConfig()
        feature_config.add_column_purpose('tag', _FeatureType.Text)

        dt_transformer = DataTransformer(task="classification", featurization_config=feature_config)
        features_new = dt_transformer.fit_transform(self.test_df)
        feature_names_new = dt_transformer.get_engineered_feature_names()
        assert (features_new is not None)
        assert len(feature_names_new) == 40
        assert (features_new.shape[1] == 40)
        feature_types_stats_new = dt_transformer.get_stats_feature_type_summary(list(self.test_df))
        expected_feature_types_new = [('transaction_id', 'Numeric'), ('user_id', 'Numeric'),
                                      ('amount', 'Numeric'), ('tag', 'Text'), ('transaction_time', 'DateTime')]
        assert len(expected_feature_types_new) == len(feature_types_stats_new)
        for i, feature_types_stat in enumerate(feature_types_stats_new):
            self.assertEqual(feature_types_stat['column name'], expected_feature_types_new[i][0])
            self.assertEqual(feature_types_stat['feature type'], expected_feature_types_new[i][1])

    def test_transformer_params_customization(self):
        transformer = DataTransformer("classification")
        features = transformer.fit_transform(self.test_df)
        feature_names = transformer.get_engineered_feature_names()
        assert (features is not None)
        assert len(feature_names) == 14
        assert (features.shape[1] == 14)
        assert feature_names[0] == 'transaction_id_MeanImputer'
        assert feature_names[1] == 'user_id_MeanImputer'
        assert feature_names[3] == 'amount_MeanImputer'

        feature_config = FeaturizationConfig()
        feature_config.add_transformer_params("Imputer", ['transaction_id'], {'strategy': 'most_frequent'})
        # set overall Imputer to use median value
        feature_config.add_transformer_params("Imputer", [],
                                              {'strategy': 'median'})

        dt_transformer = DataTransformer(task="classification", featurization_config=feature_config)
        features_new = dt_transformer.fit_transform(self.test_df)
        feature_names_new = dt_transformer.get_engineered_feature_names()
        assert (features is not None)
        assert len(feature_names_new) == 14
        assert (features_new.shape[1] == 14)
        assert feature_names_new[0] == 'transaction_id_ModeImputer'
        assert feature_names_new[1] == 'user_id_MedianImputer'
        assert feature_names_new[3] == 'amount_MedianImputer'

    def test_drop_columns(self):
        transformer = DataTransformer(task="classification")
        features = transformer.fit_transform(self.test_df)
        feature_names = transformer.get_engineered_feature_names()
        assert (features is not None)
        assert len(feature_names) == 14
        assert (features.shape[1] == 14)
        feature_types_stats = transformer.get_stats_feature_type_summary(list(self.test_df))
        expected_feature_types = [('transaction_id', 'Numeric'), ('user_id', 'Numeric'),
                                  ('amount', 'Numeric'), ('tag', 'Ignore'),
                                  ('transaction_time', 'DateTime')]
        assert len(expected_feature_types) == len(feature_types_stats)
        for i, feature_types_stat in enumerate(feature_types_stats):
            self.assertEqual(feature_types_stat['column name'], expected_feature_types[i][0])
            self.assertEqual(feature_types_stat['feature type'], expected_feature_types[i][1])

        # add ignore columns in featurization config
        feature_config = FeaturizationConfig()
        feature_config.add_drop_columns(drop_columns=['tag', 'transaction_time'])

        dt_transformer = DataTransformer(task="classification", featurization_config=feature_config)
        features_new = dt_transformer.fit_transform(self.test_df)
        feature_names_new = dt_transformer.get_engineered_feature_names()
        assert (features_new is not None)
        assert len(feature_names_new) == 4
        assert features_new.shape[1] == 4
        feature_types_stats_new = dt_transformer.get_stats_feature_type_summary(list(self.test_df))
        expected_feature_types_new = [('transaction_id', 'Numeric'), ('user_id', 'Numeric'),
                                      ('amount', 'Numeric'), ('tag', 'Ignore'),
                                      ('transaction_time', 'Ignore')]
        assert len(expected_feature_types_new) == len(feature_types_stats_new)
        for i, feature_types_stat in enumerate(feature_types_stats_new):
            self.assertEqual(feature_types_stat['column name'], expected_feature_types_new[i][0])
            self.assertEqual(feature_types_stat['feature type'], expected_feature_types_new[i][1])
