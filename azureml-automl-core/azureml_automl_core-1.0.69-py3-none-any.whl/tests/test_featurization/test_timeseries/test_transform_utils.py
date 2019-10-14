import unittest

from automl.client.core.common.forecasting_exception import (InvalidTsdfArgument)
from azureml.automl.core.featurizer.transformer.timeseries.transform_utils import OriginTimeMixin


class TestOriginTimeMixin(unittest.TestCase):
    """Tests for OriginTimeMixin."""

    def test_verify_max_horizon_input(self):
        """Test max horison verification."""
        otm = OriginTimeMixin()
        # Should pass.
        otm.verify_max_horizon_input(42)
        # Should also pass.
        otm.verify_max_horizon_input({'a': 1, 'b': 2})
        # Should raise.
        with self.assertRaises(InvalidTsdfArgument):
            otm.verify_max_horizon_input({'a': 1, 'b': '2'})
        with self.assertRaises(InvalidTsdfArgument):
            otm.verify_max_horizon_input({'a': 1, 'b': -2})
        with self.assertRaises(InvalidTsdfArgument):
            otm.verify_max_horizon_input('2')
        with self.assertRaises(InvalidTsdfArgument):
            otm.verify_max_horizon_input(-2)


if __name__ == '__main__':
    unittest.main()
