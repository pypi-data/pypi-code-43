# noqa: D100
import unittest

from . import dummy_loader


class TestDataloader(unittest.TestCase):
    """
    Tests for the dbispipeline dataloader classes.
    """

    def test_loader(self):
        """
        Tests if the loader returns correctly shaped data.
        """
        loader = dummy_loader.MockLoader()
        data = loader.load()
        self.assertEqual(len(data), 2)
        X, y = data
        self.assertEqual(len(X), len(y)),

    def test_train_test_loader(self):
        """
        Tests if train test loader returns correctly shaped data.
        """
        loader = dummy_loader.MockTrainTestLoader()
        data = loader.load()
        self.assertEqual(len(data), 2)
        train, test = data
        self.assertEqual(len(train), 2)
        self.assertEqual(len(test), 2)
        xtrain, ytrain = train
        xtest, ytest = test
        self.assertEqual(len(xtrain), len(ytrain))
        self.assertEqual(len(xtest), len(ytest))

    def test_train_validate_test_loader(self):
        """
        Tests if train validate test loader returns correctly shaped data.
        """
        loader = dummy_loader.MockTrainTestValidateLoader()
        data = loader.load()
        self.assertEqual(len(data), 3)
        train, valid, test = data
        self.assertEqual(len(train), 2)
        self.assertEqual(len(valid), 2)
        self.assertEqual(len(test), 2)
        xtrain, ytrain = train
        xvalid, yvalid = valid
        xtest, ytest = test
        self.assertEqual(len(xtrain), len(ytrain))
        self.assertEqual(len(xvalid), len(yvalid))
        self.assertEqual(len(xtest), len(ytest))

    def test_multi_loader(self):
        """
        Tests if multi loader returns correctly shaped data.
        """
        loader = dummy_loader.MockMultiLoader(10)
        data = loader.load()
        index = 0
        for run in data:
            index += 1
        self.assertEqual(index, 10)
        self.assertEqual(len(loader.configuration), 10)
