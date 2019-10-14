import unittest

from automl.client.core.common.exceptions import ConfigException
from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from azureml.automl.core.constants import SupportedTransformers, FeatureType


class TestFeaturizationConfig(unittest.TestCase):
    def test_initialize_by_param(self):
        column_purposes = {'column1': FeatureType.Numeric,
                           'column2': FeatureType.Categorical,
                           'column3': FeatureType.Numeric}
        transformer_param = {'Imputer': [(['column1', 'column2'], {"strategy": "median"}),
                                         (['column3'], {"strategy": "mean"})]}
        blocked_transformers = [SupportedTransformers.CatTargetEncoder]

        config = FeaturizationConfig(column_purposes=column_purposes,
                                     transformer_params=transformer_param,
                                     blocked_transformers=blocked_transformers)

        self.assertEqual(config.column_purposes, column_purposes)
        self.assertEqual(config.transformer_params, transformer_param)
        self.assertEqual(config.blocked_transformers, blocked_transformers)

    def test_column_purpose(self):
        # test empty
        config = FeaturizationConfig()
        self.assertIsNone(config.column_purposes)

        column_purposes = {'column1': FeatureType.Numeric, 'column2': FeatureType.Categorical}

        # set test
        config.column_purposes = column_purposes
        self.assertEqual(config.column_purposes, column_purposes)
        config.column_purposes = None
        self.assertIsNone(config.column_purposes)

        # add test
        config.add_column_purpose('column1', FeatureType.Numeric)
        config.add_column_purpose('column2', FeatureType.Categorical)
        self.assertEqual(config.column_purposes, column_purposes)

        with self.assertRaises(ConfigException):
            config.add_column_purpose('column1', 'SomeFeature')
        self.assertEqual(config.column_purposes, column_purposes)

        # remove test
        config.remove_column_purpose('column1')
        column_purposes.pop('column1')
        self.assertEqual(config.column_purposes, column_purposes)

    def test_transformer_param(self):
        config = FeaturizationConfig()
        transformer_params = {
            SupportedTransformers.Imputer: [
                (['column1', 'column2'], {"strategy": "median"}),
                (['column3'], {"strategy": "mean"})
            ]
        }

        # set test
        config.transformer_params = transformer_params
        self.assertEqual(config.transformer_params, transformer_params)
        config.transformer_params = None
        self.assertIsNone(config.transformer_params)

        # add test
        config.add_transformer_params(SupportedTransformers.Imputer,
                                      ['column1', 'column2'],
                                      {"strategy": "median"})
        config.add_transformer_params(SupportedTransformers.Imputer,
                                      ['column3'],
                                      {"strategy": "mean"})
        self.assertEqual(config.transformer_params, transformer_params)

        config.remove_transformer_params(SupportedTransformers.Imputer)
        self.assertTrue(len(config.transformer_params) == 0)

        with self.assertRaises(ConfigException):
            config.add_transformer_params('TestTransformer', ['column1', 'column2'], {"strategy": "median"})

    def test_blocked_transformers(self):
        config = FeaturizationConfig()
        self.assertIsNone(config.blocked_transformers)
        blocked_transformers = [SupportedTransformers.TfIdf, SupportedTransformers.WoETargetEncoder]

        # set test
        config.blocked_transformers = blocked_transformers
        self.assertEqual(config.blocked_transformers, blocked_transformers)
        config.blocked_transformers = None
        self.assertIsNone(config.blocked_transformers)

        # add test
        config.add_blocked_transformers(blocked_transformers)
        self.assertEqual(config.blocked_transformers, blocked_transformers)

        blocked_transformers.append(SupportedTransformers.CatTargetEncoder)
        config.add_blocked_transformers(SupportedTransformers.CatTargetEncoder)
        self.assertEqual(config.blocked_transformers, blocked_transformers)

        with self.assertRaises(ConfigException):
            config.add_blocked_transformers(SupportedTransformers.CatImputer)

    def test_drop_columns(self):
        config = FeaturizationConfig()
        self.assertIsNone(config.drop_columns)
        drop_columns = ['C1', 'C2']

        # set test
        config.drop_columns = drop_columns
        self.assertEqual(config.drop_columns, drop_columns)
        config.drop_columns = None
        self.assertIsNone(config.drop_columns)

        config.add_drop_columns(drop_columns)
        config.add_drop_columns(['C3'])
        drop_columns.append('C3')
        self.assertEqual(drop_columns, config.drop_columns)


if __name__ == "__main__":
    unittest.main()
