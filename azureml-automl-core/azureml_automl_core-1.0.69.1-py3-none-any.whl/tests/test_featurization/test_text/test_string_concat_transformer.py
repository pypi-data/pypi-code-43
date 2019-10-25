import unittest
import numpy as np
import pandas as pd
from azureml.automl.core.featurizer.transformer.text import TextFeaturizers


class TestStringConcatTransformer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestStringConcatTransformer, self).__init__(*args, **kwargs)

    def test_transform(self):
        # Test numpy array
        tr = TextFeaturizers.string_concat(**{'separator': ' '})
        x = np.array([['A', 'B'], [3, 4]])
        expected_output = np.array(["A B", "3 4"])
        actual_output = tr.fit_transform(x)
        self.assertTrue(np.all(actual_output == expected_output))

        # Test dataframe
        x = pd.DataFrame(x, columns=('yeesh', 'ugh'))
        expected_output = np.array(["A B", "3 4"])
        actual_output = tr.fit_transform(x)
        self.assertTrue(np.all(actual_output == expected_output))


if __name__ == '__main__':
    unittest.main()
